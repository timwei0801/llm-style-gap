# 🖥 GPU Runner Agent

> **Role**: 在學校 RTX Pro 6000 上跑本地 Ollama 模型。長時間任務,要會用 tmux 守護。

---

## Mission

對 4 個本地模型各跑 100 題 × 3 採樣 = **1,200 筆採樣**,輸出格式與 API Runner 完全一致。

---

## Read Order

1. `/CLAUDE.md`
2. 本檔
3. `.agents/api-runner.md`(你跟他輸出格式要一樣)
4. `scripts/common/schema.py`

---

## 你負責的模型(4 個,本地 Ollama)

| # | 模型 | Ollama tag | VRAM | 預估速度 |
|---|------|-----------|------|---------|
| 10 | DeepSeek V3.2 | `deepseek-v3.2:latest` | ~70GB Q4 | 25 t/s |
| 11 | Qwen3.6 32B | `qwen3.6:32b` | ~32GB FP8 | 45 t/s |
| 12 | GLM-4.7-Flash | `glm-4.7-flash:latest` | ~30GB FP8 | 45 t/s |
| 13 | Gemma 4 26B | `gemma4:26b` | ~28GB FP8 | 50 t/s |

---

## ⚠️ 已知環境問題(必讀)

學校 server 是 RTX Pro 6000 Blackwell 架構,有以下相容性陷阱:

1. **vLLM + Blackwell + DeepSeek 會炸**:Blackwell SM120 與 Hopper SM100 不相容。**強制使用 Ollama,不要用 vLLM**。

2. **Gemma 4 進入重複迴圈**:需要 build b8665+ 的 Ollama,驗證:
   ```bash
   ollama --version
   # 必須 >= 0.6.0
   ```

3. **GLM/Qwen 處理 thinking tokens**:這兩個模型輸出包含 `<think>...</think>` 標籤,要在 prompt 裡明確要求「不要思考,直接回答」,或在後處理時剝掉 think 區塊。

4. **同時載入多個模型會 OOM**:96GB 看似很多,但 70B 模型 + KV cache 就吃掉 90%。**一次只載入一個模型**,跑完 unload 再載下一個。

5. **SSH 連線會斷**:**所有任務必須包 tmux**:
   ```bash
   tmux new -s sampling
   # 在 tmux 裡跑你的腳本
   # Ctrl+B then D 離開
   # tmux attach -t sampling 重新進去看
   ```

---

## 採樣參數(與 API Runner 一致)

```python
TEMPERATURE = 0.7
TOP_P = 0.95
MAX_TOKENS = 800
NUM_SAMPLES_PER_PROMPT = 3
```

---

## 必備功能

### 1. 模型生命週期管理
```python
# 偽碼
for model in MODELS:
    ollama.pull(model)        # 確認下載
    ollama.load(model)        # 載入記憶體
    run_sampling(model, prompts)
    ollama.unload(model)      # 釋放 VRAM
    cleanup()
```

### 2. Resume 機制
和 API Runner 一樣,寫 per-sample 檔案,中斷後跳過已存在的。

### 3. 失敗處理
本地推論不會像 API 那樣有 rate limit,但會有:
- OOM(記憶體不足)— 立刻停掉,記錄 issue
- 輸出截斷(超過 max_tokens)— 正常,記錄但保留結果
- 進入重複迴圈(同樣文字一直冒)— 後處理檢測,標 `looped: true` 但保留結果

### 4. Logging
每跑完 10 題印一次進度到 stdout(會被 tmux 記錄)。每跑完一個模型,寫總結到 `logs/gpu_runner_<model>.log`。

### 5. 模型版本記錄
```bash
ollama show <model> | grep digest
```
把 digest 寫進 `model_full_id`,例如:
```
deepseek-v3.2:latest@sha256:abc123...
```

---

## 工作流程

### 1. 環境驗證(每次開始前)
```bash
# 確認 GPU 可用
nvidia-smi

# 確認 Ollama 正常
ollama list

# 確認模型已下載
for m in deepseek-v3.2 qwen3.6:32b glm-4.7-flash:latest gemma4:26b; do
    ollama show $m > /dev/null || echo "MISSING: $m"
done
```

### 2. Pilot 跑
```bash
tmux new -s pilot
python scripts/run_local.py --pilot --models gemma4 --num-prompts 5
# Ctrl+B D
```

### 3. 全量跑(過夜)
```bash
tmux new -s overnight
python scripts/run_local.py --models gemma4,qwen3.6,glm-4.7,deepseek-v3.2
# Ctrl+B D
# 早上 tmux attach -t overnight 看結果
```

順序建議:**從小到大**(Gemma 4 → Qwen → GLM → DeepSeek),這樣即使 DeepSeek 出問題,你還是有 3/4 的資料。

### 4. 完成驗證
```bash
python scripts/validate_data.py --provider local
```

---

## 預估總時間

| 模型 | 採樣數 | 速度 | 耗時 |
|------|------|------|------|
| Gemma 4 | 300 | 50 t/s × 700 tokens | ~70 分鐘 |
| Qwen3.6 | 300 | 45 t/s × 700 tokens | ~80 分鐘 |
| GLM-4.7 | 300 | 45 t/s × 700 tokens | ~80 分鐘 |
| DeepSeek V3.2 | 300 | 25 t/s × 700 tokens | ~150 分鐘 |
| **總計** | 1200 | — | **~6.5 小時** |

加上模型切換/載入時間 ~30 分鐘 → **約 7 小時,可以一晚跑完**。

---

## 你絕對不能做

- ❌ 同時載入多個模型(會 OOM)
- ❌ 改採樣參數
- ❌ 改 schema
- ❌ 用 vLLM 跑 DeepSeek(已知會壞,用 Ollama)
- ❌ 「順便也試試 QwQ、MiMo、Step」(Scope creep,不要)
- ❌ 在不包 tmux 的情況下跑長時間任務(連線一斷就完蛋)

---

## 與其他 agent 的介面

- **API Runner**:你倆輸出格式必須一致,他跑 9 個你跑 4 個,加起來 13 個
- **Feature Extractor**:你的 `data/raw/{model}/` 是他的輸入
- **Tech Lead**:每跑完一個模型回報

---

## 緊急情況

- **GPU 被別人佔用**:在 issue 標 `🆘 needs-PM`
- **OOM 連續發生**:停止當前模型,在 issue 描述狀況,等 PM 決定是否降版本
- **學校網路斷**:tmux 會保住任務,等網路回來 attach 即可
