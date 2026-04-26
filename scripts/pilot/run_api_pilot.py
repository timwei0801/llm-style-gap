"""
Pilot run for API Runner agent.

2 models x 10 prompts x 1 sample = 20 API calls.
Writes one JSON per call matching SamplingResult schema.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Make scripts/common importable
ROOT = Path("/mnt/nfs/maokao_3/Downloads/llm-style-gap")
sys.path.insert(0, str(ROOT / "scripts"))
from common.schema import SamplingResult, TEMPERATURE, TOP_P, MAX_TOKENS, get_model_meta  # noqa: E402

load_dotenv(ROOT / ".env")

PROMPT_IDS = ["Q001", "Q004", "Q028", "Q029", "Q045",
              "Q048", "Q064", "Q078", "Q083", "Q099"]

SAMPLE_INDEX = 1
TODAY_STAMP = "20260427"

OUT_ROOT = ROOT / "data" / "pilot" / "round1"


def load_prompts():
    data = json.loads((ROOT / "prompts" / "prompts.json").read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in data}
    return [by_id[pid] for pid in PROMPT_IDS]


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def call_anthropic(prompt_text: str):
    """Returns (response_text, token_count, model_full_id, raw_metadata).

    NOTE: claude-opus-4-7 has deprecated `temperature` and `top_p` parameters
    (API returns 400 if either is sent). We therefore omit them from the call
    and let the model use its built-in defaults. The schema fields still record
    the project-intended values (0.7 / 0.95) and `raw_metadata.sampling_note`
    flags this discrepancy for downstream agents / PM review.
    """
    from anthropic import Anthropic
    client = Anthropic()
    api_model = "claude-opus-4-7"
    msg = client.messages.create(
        model=api_model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt_text}],
    )
    text = "".join(block.text for block in msg.content if getattr(block, "type", None) == "text")
    out_tokens = msg.usage.output_tokens if msg.usage else 0
    in_tokens = msg.usage.input_tokens if msg.usage else 0
    full_id = msg.model or f"claude-opus-4-7-{TODAY_STAMP}"
    raw = {
        "id": msg.id,
        "model": msg.model,
        "stop_reason": msg.stop_reason,
        "usage": {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
        },
        "sampling_note": (
            "temperature and top_p parameters were NOT sent: "
            "claude-opus-4-7 deprecates both (API 400). "
            "Model used its internal defaults."
        ),
    }
    return text, out_tokens, full_id, raw


def call_groq(prompt_text: str):
    from groq import Groq
    client = Groq()
    api_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    resp = client.chat.completions.create(
        model=api_model,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        messages=[{"role": "user", "content": prompt_text}],
    )
    choice = resp.choices[0]
    text = choice.message.content or ""
    out_tokens = resp.usage.completion_tokens if resp.usage else 0
    in_tokens = resp.usage.prompt_tokens if resp.usage else 0
    full_id = resp.model or f"llama-4-scout-{TODAY_STAMP}"
    raw = {
        "id": resp.id,
        "model": resp.model,
        "finish_reason": choice.finish_reason,
        "usage": {
            "prompt_tokens": in_tokens,
            "completion_tokens": out_tokens,
        },
    }
    return text, out_tokens, full_id, raw


CALLERS = {
    "claude-opus-4-7": call_anthropic,
    "llama-4-scout": call_groq,
}


def run_one(model_id: str, prompt: dict):
    out_dir = OUT_ROOT / model_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{prompt['id']}.json"
    failed_path = out_dir / f"{prompt['id']}.FAILED.json"

    if out_path.exists():
        print(f"[skip] {model_id}/{prompt['id']} already exists", flush=True)
        return "skip"

    meta = get_model_meta(model_id)
    last_err = None
    for attempt in range(3):
        try:
            t0 = time.time()
            text, out_tokens, full_id, raw = CALLERS[model_id](prompt["text"])
            latency_ms = int((time.time() - t0) * 1000)

            res = SamplingResult(
                model=model_id,
                model_full_id=full_id or f"{model_id}-{TODAY_STAMP}",
                model_provider=meta["provider"],
                model_family=meta["family"],
                is_anchor=meta["is_anchor"],
                anchor_pair=meta["anchor_pair"],
                prompt_id=prompt["id"],
                prompt_category=prompt["category"],
                prompt_text=prompt["text"],
                sample_index=SAMPLE_INDEX,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                timestamp_utc=utc_now_iso(),
                response=text,
                response_token_count=int(out_tokens or 0),
                latency_ms=latency_ms,
                raw_metadata=raw,
            )
            out_path.write_text(res.to_json(), encoding="utf-8")
            print(f"[ok]   {model_id}/{prompt['id']} {latency_ms}ms tokens={out_tokens}", flush=True)
            return "ok"
        except Exception as e:  # noqa: BLE001
            last_err = e
            err_type = type(e).__name__
            print(f"[retry {attempt+1}/3] {model_id}/{prompt['id']} {err_type}: {str(e)[:120]}", flush=True)
            if attempt < 2:
                time.sleep(5)

    # All retries failed
    failed_path.write_text(json.dumps({
        "error": f"{type(last_err).__name__}: {str(last_err)[:300]}",
        "prompt_id": prompt["id"],
        "model": model_id,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[FAIL] {model_id}/{prompt['id']}", flush=True)
    return "fail"


def main():
    prompts = load_prompts()
    summary = {m: {"ok": 0, "skip": 0, "fail": 0} for m in CALLERS}
    t_start = time.time()
    for model_id in CALLERS:
        print(f"\n=== {model_id} ===", flush=True)
        for p in prompts:
            status = run_one(model_id, p)
            summary[model_id][status] += 1
            # Small delay for Groq rate limit safety
            if model_id == "llama-4-scout":
                time.sleep(0.5)
    elapsed = time.time() - t_start
    print(f"\n=== SUMMARY ({elapsed:.1f}s) ===")
    for m, s in summary.items():
        print(f"{m}: ok={s['ok']} skip={s['skip']} fail={s['fail']}")


if __name__ == "__main__":
    main()
