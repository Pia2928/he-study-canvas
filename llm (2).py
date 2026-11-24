# llm.py: thin wrapper around the AI service (Anthropic by default; Azure/OpenAI supported; mock without key)
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("MODEL", "")
TEMPERATURE = os.environ.get("TEMPERATURE", "0.7")                 # OpenAI only; "" for models that reject it
ANTHROPIC_TEMPERATURE = os.environ.get("ANTHROPIC_TEMPERATURE", "")
ANTHROPIC_THINKING = os.environ.get("ANTHROPIC_THINKING", "")
MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "500"))      # replies are short: 2 to 3 chips and at most about 55 words

_client = None


def provider():
    if ANTHROPIC_API_KEY:
        return "anthropic"
    if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
        return "azure"
    if OPENAI_API_KEY:
        return "openai"
    return "mock"


def client():
    global _client
    if _client is None:
        p = provider()
        if p == "anthropic":
            import anthropic
            _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        elif p == "azure":
            from openai import AzureOpenAI
            _client = AzureOpenAI(azure_endpoint=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY,
                                  api_version=AZURE_OPENAI_API_VERSION)
        elif p == "openai":
            from openai import OpenAI
            _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def model_name():
    if MODEL:
        return MODEL
    return "claude-sonnet-5-5" if provider() == "anthropic" else "gpt-4o"


def normalise_history(history):
    """Alternate user/assistant turns, starting with the user (Anthropic requirement)."""
    out = []
    for m in history:
        if m["role"] not in ("user", "assistant") or not m["content"].strip():
            continue
        if out and out[-1]["role"] == m["role"]:
            out[-1] = {"role": m["role"], "content": out[-1]["content"] + "\n\n" + m["content"]}
        else:
            out.append({"role": m["role"], "content": m["content"]})
    while out and out[0]["role"] != "user":
        out.pop(0)
    return out


def reply(system_prompt, history):
    """Return (text, model). history: [{"role": "user"|"assistant", "content": str}]"""
    p = provider()
    if p == "mock":
        return ('{"reply": "[MOCK] Good start. What would make a customer choose you over someone else?", '
                '"suggestions": ["Mock suggestion A for this box", "Mock suggestion B for this box", '
                '"Mock suggestion C for this box"]}'), "mock"
    c = client()
    if p == "anthropic":
        kwargs = {"model": model_name(), "system": system_prompt, "messages": normalise_history(history),
                  "max_tokens": MAX_OUTPUT_TOKENS}
        if ANTHROPIC_TEMPERATURE != "":
            kwargs["temperature"] = float(ANTHROPIC_TEMPERATURE)
        if ANTHROPIC_THINKING.lower() in ("", "disabled"):       # no extended thinking by default: Compi has to answer quickly ("default" keeps the model's own setting)
            kwargs["thinking"] = {"type": "disabled"}
        try:
            resp = c.messages.create(**kwargs)
        except Exception as exc:
            if "thinking" not in kwargs or "thinking" not in str(exc).lower():
                raise
            kwargs.pop("thinking")                               # a model that does not accept the setting: ask again without it
            resp = c.messages.create(**kwargs)
        text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")
        return text, getattr(resp, "model", model_name())
    kwargs = {"model": model_name(), "messages": [{"role": "system", "content": system_prompt}] + history,
              "max_tokens": MAX_OUTPUT_TOKENS}
    if TEMPERATURE != "":
        kwargs["temperature"] = float(TEMPERATURE)
    resp = c.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or "", getattr(resp, "model", model_name())
