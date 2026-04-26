"""
GPU Runner — Pilot run for deepseek-r1:70b
1 model x 10 prompts x 1 sample = 10 calls.

Hard-coded params (do not change):
- temperature 0.7, top_p 0.95, num_predict 800, num_ctx 4096
- sample_index 1
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path("/mnt/nfs/maokao_3/Downloads/llm-style-gap")
PROMPTS_FILE = ROOT / "prompts" / "prompts.json"
OUT_DIR = ROOT / "data" / "pilot" / "round1" / "deepseek-r1-70b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_URL = "http://127.0.0.1:11502/api/chat"
OLLAMA_TAG = "deepseek-r1:70b"
MODEL_DIGEST = "d37b54d01a76"  # short digest from `ollama list`
MODEL_FULL_ID = f"{OLLAMA_TAG}@{MODEL_DIGEST}"

TEMPERATURE = 0.7
TOP_P = 0.95
MAX_TOKENS = 800
NUM_CTX = 4096
SAMPLE_INDEX = 1

WANTED_IDS = ["Q001", "Q004", "Q028", "Q029", "Q045", "Q048",
              "Q064", "Q078", "Q083", "Q099"]


def load_prompts():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        all_prompts = json.load(f)
    by_id = {p["id"]: p for p in all_prompts}
    return [by_id[pid] for pid in WANTED_IDS]


def call_once(prompt_text):
    payload = {
        "model": OLLAMA_TAG,
        "messages": [{"role": "user", "content": prompt_text}],
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "num_predict": MAX_TOKENS,
            "num_ctx": NUM_CTX,
        },
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=900)
    r.raise_for_status()
    return r.json()


def call_with_retry(prompt_text, max_attempts=3):
    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            return call_once(prompt_text)
        except Exception as e:
            last_err = e
            print(f"  attempt {attempt} failed: {e}", flush=True)
            if attempt < max_attempts:
                time.sleep(5)
    raise last_err


def main():
    prompts = load_prompts()
    print(f"Loaded {len(prompts)} prompts: {[p['id'] for p in prompts]}", flush=True)

    overall_start = time.time()
    written = 0
    failed = []
    total_eval_count = 0
    total_eval_seconds = 0.0

    for idx, p in enumerate(prompts, 1):
        pid = p["id"]
        out_path = OUT_DIR / f"{pid}.json"
        failed_path = OUT_DIR / f"{pid}.FAILED.json"

        if out_path.exists():
            print(f"[{idx}/10] {pid} already exists, skipping", flush=True)
            continue

        # remove any stale FAILED file from a previous run
        if failed_path.exists():
            failed_path.unlink()

        print(f"[{idx}/10] {pid} ({p['category']}): {p['text'][:40]}...", flush=True)
        t0 = time.time()
        try:
            data = call_with_retry(p["text"])
        except Exception as e:
            print(f"  FAILED: {e}", flush=True)
            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump({"error": str(e), "prompt_id": pid}, f, ensure_ascii=False, indent=2)
            failed.append(pid)
            continue

        wall_ms = int((time.time() - t0) * 1000)
        msg = data.get("message", {})
        content = msg.get("content", "")
        thinking = msg.get("thinking", "")

        eval_count = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 0)
        total_duration_ns = data.get("total_duration", 0)
        prompt_eval_count = data.get("prompt_eval_count", 0)
        latency_ms = int(eval_duration_ns / 1_000_000) if eval_duration_ns else wall_ms

        if eval_duration_ns > 0:
            total_eval_count += eval_count
            total_eval_seconds += eval_duration_ns / 1e9

        record = {
            "model": "deepseek-r1-70b",
            "model_full_id": MODEL_FULL_ID,
            "model_provider": "ollama",
            "model_family": "deepseek",
            "is_anchor": False,
            "anchor_pair": None,
            "prompt_id": pid,
            "prompt_category": p["category"],
            "prompt_text": p["text"],
            "sample_index": SAMPLE_INDEX,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "top_p": TOP_P,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "response": content,
            "response_token_count": eval_count,
            "latency_ms": latency_ms,
            "raw_metadata": {
                "thinking": thinking,
                "num_ctx": NUM_CTX,
                "ollama_total_duration_ms": int(total_duration_ns / 1_000_000) if total_duration_ns else wall_ms,
                "prompt_eval_count": prompt_eval_count,
            },
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0
        print(f"  done: {eval_count} tokens in {wall_ms} ms ({tps:.1f} t/s), thinking={len(thinking)} chars",
              flush=True)
        written += 1

    elapsed = time.time() - overall_start
    avg_tps = (total_eval_count / total_eval_seconds) if total_eval_seconds > 0 else 0
    print("\n=== Summary ===", flush=True)
    print(f"Written: {written}", flush=True)
    print(f"Failed: {len(failed)} {failed}", flush=True)
    print(f"Total wall time: {elapsed:.1f} s ({elapsed/60:.2f} min)", flush=True)
    print(f"Avg generation speed: {avg_tps:.1f} t/s "
          f"(over {total_eval_count} tokens / {total_eval_seconds:.1f} s)", flush=True)


if __name__ == "__main__":
    main()
