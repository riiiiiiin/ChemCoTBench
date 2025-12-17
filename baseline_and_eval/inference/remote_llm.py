import requests
from .inference_interface import InferenceInterface
from tqdm import tqdm
import json

class RemoteLLM(InferenceInterface):
    def __init__(self, api_key, base_url, model_name, streaming = False, enable_thinking = False):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.streaming = streaming
        self.enable_thinking = enable_thinking
    
    def predict(self, input):
        # not batched for remote api
        response = []
        for request in tqdm(input):
            temperature = request.get("temperature", 0)
            enable_thinking = self.enable_thinking
            messages = request.get("messages", [])
            if self.streaming:
                raw_response = call_direct_stream_raw(self.api_key, self.base_url, self.model_name, messages, temperature, enable_thinking)
                parsed_text = parse_stream_raw(raw_response["text"])
                response.append(parsed_text)
            else:
                raw_response = call_direct(self.api_key, self.base_url, self.model_name,
                            messages,
                            temperature,
                            enable_thinking)
                response.append(raw_response['choices'][0]['message']['content'])
        return response
    
def call_direct(api_key, base_url, model_name, messages, temperature=0, enable_thinking=False):
    url = f"{base_url.rstrip('/')}/chat/completions"
    if api_key:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    else:
        headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "enable_thinking": enable_thinking
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

def call_direct_stream_raw(
    api_key,
    base_url: str,
    model_name: str,
    messages,
    temperature: float = 0.0,
    enable_thinking: bool = False,
    timeout = None
):
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "enable_thinking": enable_thinking,
        "stream": True,
    }

    lines = []
    # 使用 context manager 保证连接关闭
    with requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout) as r:
        # 保持与原函数一致的错误处理：如果状态码表示错误则抛出
        r.raise_for_status()

        # 按行读取（decode_unicode=True -> 得到 str，每行不含换行符）
        for raw_line in r.iter_lines(decode_unicode=True):
            # raw_line 可能为 b''/''（空行），iter_lines 已过滤大部分空缓冲
            # 我们把所有非 None 的行收集下来（保留原始内容，不进行解析/trim）
            if raw_line is None:
                continue
            lines.append(raw_line)

    full_text = "\n".join(lines)
    return {
        "status_code": r.status_code,
        "headers": dict(r.headers),
        "text": full_text,
    }

def parse_stream_raw(lines_or_text):
    """
    解析你发来的原始流（SSE 风格每行以 "data: ..." 开头）。
    - 输入可为 list[str]（如 result['lines']）或整段 raw text。
    - 返回 dict:
        {
          "chunks": [parsed_json_objects...],   # JSON 解析成功的 chunk（按原始顺序）
          "raw_contents": [str,...],            # 每个 chunk 中提取出的原始 content（未修复）
          "fixed_contents": [str,...],          # 修复后的 content（如果尝试修复失败则与 raw_contents 相同）
          "final_text": str                     # 拼接后的最终文本（fixed_contents 串联）
        }
    """
    if isinstance(lines_or_text, str):
        raw_lines = [ln for ln in lines_or_text.splitlines() if ln.strip() != ""]
    else:
        raw_lines = [ln for ln in lines_or_text if (isinstance(ln, str) and ln.strip() != "")]

    chunks = []
    raw_contents = []

    for line in raw_lines:
        # 支持 "data: {...}" 或直接 JSON 行
        l = line.strip()
        if l.startswith("data:"):
            payload = l[len("data:"):].strip()
        else:
            payload = l

        if payload == "[DONE]":
            break

        try:
            obj = json.loads(payload)
        except Exception:
            # 解析失败则跳过（保留原行为调试）
            continue

        chunks.append(obj)

        # 提取常见位置的文本增量（OpenAI-兼容样式）
        text_piece = ""
        choices = obj.get("choices") or []
        if choices:
            # 优先 delta.content（增量模式），否则尝试 choices[0].text
            first = choices[0]
            delta = first.get("delta") or {}
            text_piece = delta.get("content")
            if text_piece is None:
                # 兼容其它实现：完整文本可能在 'text'
                text_piece = first.get("text") or ""
        raw_contents.append(text_piece or "")

    # 修复可能的 mojibake：把当作 latin-1 编回字节，再 utf-8 解码
    fixed_contents = []
    for s in raw_contents:
        if s == "":
            fixed_contents.append(s)
            continue
        try:
            # 仅当字符串可被 latin-1 编码时尝试修复（否则留原样）
            # 对 ASCII/常规字符，这个操作一般不会破坏内容；
            # 对已经正确的中文/emoji，会触发 UnicodeEncodeError -> 保留原样。
            candidate = s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            fixed_contents.append(s)
        else:
            # 进一步做个简单判断：如果修复后的文本看起来更“正常”（例如包含 CJK 或 emoji），采用修复结果
            def score(u: str) -> int:
                cjk = sum(1 for ch in u if "\u4e00" <= ch <= "\u9fff")
                emoji = sum(1 for ch in u if ord(ch) > 0x1f000)
                return cjk + emoji * 2
            if score(candidate) >= score(s):
                fixed_contents.append(candidate)
            else:
                fixed_contents.append(s)

    final_text = "".join(fixed_contents)
    
    final_text.replace("[DONE]", "")

    return final_text