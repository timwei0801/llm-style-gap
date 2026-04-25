# 🚀 Quickstart for PM (Timwei)

> 這份是給你(PM)的 onboarding。Agent 不需要看這份。

---

## Step 1: GitHub repo 建立

```bash
# 在學校 server 上(或本地都行)
cd ~
git clone <unzipped-folder> llm-style-gap
cd llm-style-gap

# 推到 GitHub
gh repo create llm-style-gap --public --source=. --push
```

或用 web UI 建立 repo 後:
```bash
git remote add origin git@github.com:<你的 username>/llm-style-gap.git
git add .
git commit -m "chore: initial commit with agent scaffolding"
git push -u origin main
```

---

## Step 2: 設置 API key(本地,不進 git)

```bash
cp .env.example .env
# 用編輯器填入真實 API key
nano .env
```

⚠️ **千萬確認 `.env` 在 `.gitignore` 裡**(已經設好了)

驗證:
```bash
git status
# .env 不應該出現
```

---

## Step 3: 確認 Claude Code 環境

在學校 server 上:

```bash
# 啟用 Claude Code 的 Agent Teams 功能
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# 進入 repo
cd llm-style-gap

# 啟動 Claude Code(它會自動讀 CLAUDE.md)
claude
```

第一次進去,跟 Claude Code 說:
```
請讀完 CLAUDE.md,然後讀 .agents/tech-lead.md。
你現在是 Tech Lead Agent。
請列出本專案目前的狀態,並建議第一個該做的任務。
```

---

## Step 4: PM 工作節奏建議

### 每天(約 30 分鐘)
- **早上 5 分鐘**:看 `Daily Status` issue 的最新 comment
- **午休 15 分鐘**:處理 PR review(集中處理,別零碎)
- **睡前 10 分鐘**:看明天的計畫,給方向性指示

### 每週(約 1 小時)
- **週日**:Review 整週進度,調整下週計畫
- **預算檢查**:確認 API 花費沒有超 $10

### 緊急情況
- Issue 標 `🚨 urgent` 的會 ping 你,放下手邊事處理

---

## Step 5: Agent Teams 啟動模式

### Mode 1:互動式(Week 2 — Prompt 設計階段)
你坐在電腦前,跟 Prompt Designer 一起改題目。
```bash
claude
> 切換成 Prompt Designer Agent。我們來討論 emotion 類的題目。
```

### Mode 2:背景模式(Week 3 — 採樣階段)
你掛機,讓 agent 在 server 上跑。
```bash
tmux new -s claude-runner
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
claude --headless "Tech Lead, 請啟動 API Runner 跑完所有 9 個 API 模型,然後啟動 GPU Runner 跑 4 個本地模型。完成後在 issue #X 留言通知我。"
# Ctrl+B D
```

### Mode 3:Review 模式(Week 4 — 分析階段)
你 SSH 進去,手動點開 PR review。

---

## Step 6: 緊急止血指令

如果發現任何不對勁(資料被覆蓋、agent 跑歪、被覆蓋 secret):

```bash
# 立刻凍結:把所有 agent 工作分支保護起來
gh issue create --title "🚨 EMERGENCY FREEZE" --body "停止所有 agent 工作直到 PM 評估"

# 看最近 commit
git log --all --oneline -20

# 回退 main(如果 main 被汙染)
git checkout main
git reset --hard <good-commit-sha>
git push --force-with-lease  # 慎用
```

---

## 資源清單

- 提案書:`docs/proposal.docx`(已準備)
- Agent 操作手冊:`CLAUDE.md`
- 各 agent system prompt:`.agents/`
- Schema:`scripts/common/schema.py`

---

## FAQ

**Q: Agent 想改 schema,該怎麼辦?**
A: 拒絕。讓他開 issue,你親自決定。Schema 改動會影響所有 agent。

**Q: 一個 agent 卡在某個模型跑不出來?**
A: 看 `🆘 needs-PM` issue。如果是非關鍵模型(例如 GLM),允許跳過。如果是關鍵模型(例如 Claude Opus),要排除問題,不能跳過。

**Q: 我不在學校,server 連不上?**
A: 在家用 VPN 或 SSH tunnel。`tmux` 會保住任務不會掉。

**Q: API 預算快超了?**
A: 切到便宜模型(GPT-5.4 → mini),或用 Groq 替代某些閉源模型。**不要硬撐花錢**。

**Q: 要不要寫單元測試?**
A: 不用。這是研究專案不是 production。能跑 = 過。

**Q: Claude Code 跑到一半 context 滿了怎麼辦?**
A: 開新 session,讓他先讀 `CLAUDE.md` + 對應 agent system prompt + `gh issue list --limit 20` 補回 context。
