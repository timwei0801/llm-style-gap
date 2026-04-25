# Prompts

> 這個資料夾由 **Prompt Designer Agent** 維護。

## Files

- `prompts.json` — 100 題主題庫(freeze 後不可改)
- `pilot/` — Pilot test 結果
  - `round1_results.json` — 第一輪 pilot 採樣結果
  - `round1_analysis.md` — 第一輪鑑別度分析
  - `round2_*.{json,md}` — 第二輪
- `archive/` — 被淘汰的題目(保留歷史)

## Status

- [ ] V1 草稿(100 題)
- [ ] Round 1 Pilot(10 題 × 3 模型)
- [ ] Round 1 修訂
- [ ] Round 2 Pilot(若需要)
- [ ] **Frozen**(Week 2 結束前必須達成)

## Schema

每題格式:

```json
{
  "id": "Q001",
  "category": "emotion",
  "text": "我剛失戀,12 字內安慰我",
  "design_notes": "短、有字數限制、逼模型選擇陪伴 vs 分析",
  "expected_dimensions_to_distinguish": ["temperature", "directness"],
  "version": 1,
  "frozen": false
}
```

## Rules

1. **Freeze 後不可改**:除非 PM 開新 issue 批准
2. **每題必填 design_notes**:解釋這題為什麼這樣設計
3. **拒絕類題目絕不可惡意**:只設計灰色地帶,不設計傷害性題目
