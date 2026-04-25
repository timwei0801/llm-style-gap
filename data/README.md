# Data

> 由 **API Runner**、**GPU Runner**、**Feature Extractor** agent 維護。

## Folder Structure

```
data/
├── samples/          # 每模型 5 筆樣本(會 commit,讓人看格式)
├── raw/              # 完整原始回答(.gitignore,放 server)
│   ├── claude-opus-4-7/
│   │   ├── Q001_1.json
│   │   ├── Q001_2.json
│   │   └── ...
│   ├── gpt-5-4/
│   └── ...
├── features/         # 特徵矩陣(會 commit)
│   ├── full_matrix.csv
│   ├── behavior_only_matrix.csv
│   ├── feature_correlation.png
│   └── anomalies.csv
└── README.md
```

## Status (更新時請改這裡)

### 採樣完成度

| 模型 | 預期 | 實際 | 失敗 | 狀態 |
|------|------|------|------|------|
| claude-opus-4-7 | 300 | - | - | ⏳ |
| claude-sonnet-4-6 | 300 | - | - | ⏳ |
| gpt-5-4 | 300 | - | - | ⏳ |
| gpt-5-4-mini | 300 | - | - | ⏳ |
| gemini-3-1-pro | 300 | - | - | ⏳ |
| gemini-3-flash | 300 | - | - | ⏳ |
| llama-4-scout | 300 | - | - | ⏳ |
| llama-3-3-70b | 300 | - | - | ⏳ |
| kimi-k2 | 300 | - | - | ⏳ |
| deepseek-v3-2 | 300 | - | - | ⏳ |
| qwen3-6-32b | 300 | - | - | ⏳ |
| glm-4-7-flash | 300 | - | - | ⏳ |
| gemma-4-26b | 300 | - | - | ⏳ |
| **總計** | **3,900** | **-** | **-** | |

### 特徵抽取完成度

- [ ] 第一層:語意特徵
- [ ] 第二層:結構特徵
- [ ] 第三層:行為特徵
- [ ] 標準化
- [ ] 完整矩陣輸出
- [ ] 純行為矩陣輸出

## Notes

- 完整原始資料(`raw/`)放在學校 server,**沒有 commit 進 git**
- 若想 reproduce 結果,只需要 `features/*.csv` + `scripts/`
- `samples/` 下每模型 5 筆讓你看格式長什麼樣
