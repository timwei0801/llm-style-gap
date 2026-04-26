# LLM Style GAP Analysis 🎨

> **大型語言模型回答風格之圖譜分析** — 應用 GAP (Generalized Association Plots) 探索 13 個 LLM 的「人格指紋」

[![Status](https://img.shields.io/badge/status-WIP-orange)]() [![License](https://img.shields.io/badge/license-MIT-blue)]() [![Made with](https://img.shields.io/badge/made_with-Claude_Code-purple)]()

---

## 🎯 Project at a Glance

**Question**: 不同 LLM 的回答「風格」是否真的有差異?如果有,哪些模型在風格上是親戚?

**Method**: 對 13 個主流 LLM 各跑 100 題、3 次採樣,抽取多維風格特徵,用 GAP seriation 重排「模型 × 特徵」矩陣,挖掘風格群落。

**Special**: 設計 3 組「同家族不同規模」錨點對(Claude Opus/Sonnet、GPT/mini、Gemini Pro/Flash),驗證 GAP 是否能捕捉家族特質。

---

## 🤖 Models Under Test (12)

| # | Model | Provider | Role |
|---|-------|----------|------|
| 1 | Claude Opus 4.7 | Anthropic | Flagship |
| 2 | Claude Sonnet 4.6 | Anthropic | ⚓ Anchor A |
| 3 | GPT-5.4 | OpenAI | Flagship |
| 4 | GPT-5.4 mini | OpenAI | ⚓ Anchor B |
| 5 | Gemini 3.1 Pro | Google | Flagship |
| 6 | Gemini 3 Flash | Google | ⚓ Anchor C |
| 7 | Llama 4 Scout | Meta (via Groq) | Open-source |
| 8 | Llama 3.3 70B | Meta (via Groq) | Cross-gen |
| 9 | Kimi K2 | Moonshot (via Groq) | China top-tier |
| 10 | DeepSeek R1 70B | DeepSeek (local Ollama) | China reasoning |
| 11 | Qwen3.6 35B-A3B | Alibaba (local Ollama) | China general |
| 12 | Gemma 4 31B | Google (local Ollama) | Lightweight OSS |

---

## 🏗 Architecture

This repo is built using **Claude Code Agent Teams** with a PM + Tech Lead + 5 specialized agents pattern:

- 🎯 **Tech Lead** — orchestration & integration
- 📝 **Prompt Designer** — 100-question prompt set
- 🌐 **API Runner** — closed-source + Groq APIs
- 🖥 **GPU Runner** — local Ollama on RTX Pro 6000
- 📊 **Feature Extractor** — 3-layer feature engineering
- 🎨 **GAP Analyst** — seriation, visualization & storytelling

PM (human) reviews PRs and makes methodological decisions. Agents handle execution.

See [`CLAUDE.md`](./CLAUDE.md) for full operational manual.

---

## 📂 Repo Structure

```
.
├── CLAUDE.md              # Agent operations manual
├── .agents/               # Per-agent system prompts
├── prompts/               # 100-question prompt set
├── scripts/               # Per-agent execution scripts
├── data/                  # Samples (full data on server)
├── analysis/              # GAP results & figures
└── docs/                  # Proposal, final report
```

---

## 🚀 Quickstart (for collaborators)

```bash
# 1. Clone
git clone https://github.com/<your-username>/llm-style-gap.git
cd llm-style-gap

# 2. Set up env
cp .env.example .env
# fill in your API keys

# 3. Install deps
pip install -r requirements.txt

# 4. Run pilot
python scripts/run_api.py --pilot --models claude-opus --num-prompts 5
```

---

## 📊 Key Findings (TBD)

Will be populated after Week 4. Expected stories:

1. 🔥 Cross-family kinship — do Claude and Gemini cluster despite different lineage?
2. ⚓ Anchor validation — do same-family pairs stay close?
3. 🌐 Open-source convergence — do OSS models share behavioral traits?
4. 🇨🇳 China model divergence — are Chinese models really one family?

---

## 📜 Citation

If you find this useful for your own research:

```bibtex
@misc{wei2026llmgap,
  title={LLM Style GAP Analysis: Visualizing Response Patterns Across 13 Frontier Models},
  author={Wei, Qi-Hong (Timwei)},
  year={2026},
  howpublished={\url{https://github.com/<username>/llm-style-gap}}
}
```

GAP method credit: Chen, C. H. (2002). *Generalized Association Plots*. Statistica Sinica.

---

## 📝 License

MIT — feel free to fork, learn from, and build upon.

---

## 🙏 Acknowledgments

- Lab for Information Visualization, Institute of Statistical Science, Academia Sinica — for the GAP software & method
- 學校 GPU 資源(RTX Pro 6000)
- Anthropic, OpenAI, Google, Groq, Meta, Moonshot, DeepSeek, Alibaba, Z.ai — for making their models accessible
