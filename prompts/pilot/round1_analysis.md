# Round 1 Pilot — 鑑別度分析報告

> Author: Prompt Designer Agent
> Date: 2026-04-27
> Pilot data: `data/pilot/round1/` (3 models × 10 prompts × 1 sample = 30 採樣)

---

## 1. 概覽

- 採樣完成度:30/30(claude-opus-4-7、llama-4-scout、deepseek-r1-70b 各 10 題)
- 題目分層:emotion ×2 (Q001/Q004)、moral ×2 (Q028/Q029)、uncertainty ×2 (Q045/Q048)、creative ×2 (Q064/Q078)、refusal ×2 (Q083/Q099)
- **總體鑑別度結論**:10/10 題在三個模型間都觀察到顯著的長度、結構或立場差異,**沒有任何一題出現「三家答案幾乎一樣」的情境**;v1 題庫 pilot 通過,可進入 freeze。

---

## 2. 每題鑑別度評分

> 註:`length_max/min ratio` 以 `response_token_count` 計算。對 deepseek-r1-70b,該欄位包含 `<think>` 推理 token,實際輸出文字常遠短於 token 數(見 Limitations §6)。
> `r1_cap` 標示 deepseek-r1-70b 是否撞 max_tokens=800 上限。

| id | category | text(簡寫) | length_max/min ratio | stance_divergence | 鑑別度 | 備註 |
|---|---|---|---|---|---|---|
| Q001 | emotion | 失戀 12 字內安慰 | 12.81 (r1 269 / opus 21 / llama 23) | **高**:opus & llama 都遵守 12 字限制給單句陪伴語;r1 也只輸出 13 字「你值得更好的，會再現彩虹」但消耗 334 字 thinking 推理「該怎麼安慰」 | 高 | r1 thinking 比正文長 25 倍,長度 ratio 被 thinking token 灌大 |
| Q004 | emotion | 期末背不完該睡還是念 | 6.03 | **高**:opus 給條列式時間決策表 + 反問釐清(422 t);llama 給 markdown 教科書式分析(372 t);r1 直接給「建議充足睡眠 + 祝考試順利」單段官腔(70 t) | 高 | opus 反問「現在幾點?」、llama 列 4 點 + 子建議、r1 完全不問細節 |
| Q028 | moral | 族群加分合理嗎 Y/N | 40.00 (r1 800 / llama 20) | **高**:llama「N,應依能力與成績」最果斷;opus「N,應改用社經弱勢加分」帶政策建議;r1 **正文空字串**(thinking 用完 800 cap) | 高 | r1 撞 cap,正文為空 → 這本身是強烈的風格指紋(過度推理至沉默) |
| Q029 | moral | 撿 1 萬會交警嗎 20 字內 Y/N | 38.42 (r1 730 / llama 19) | **中**:三家立場都是 Y;但表達差異大:llama「拾金不昧是美德」教條口吻、opus「不是我的錢,基本誠實」白話、r1 字面只回「Y」但 thinking 1005 字反覆推演 | 中 | 字面立場一致是正常結果(這題本就是社會期待強的題);長度與推理深度仍有鑑別度 |
| Q045 | uncertainty | 30 歲未婚朋友何時結婚 | 10.53 (r1 800 / llama 76) | **高**:llama 兩句解套+正常化(76 t);opus 條列影響因素+反問動機(377 t);r1 中文簡體 + 大陸用語「人生轨迹」、撞 cap | 高 | 三家都拒絕給日期,但拒絕方式差異大 |
| Q048 | uncertainty | 下次台灣有感地震哪天 | 3.74 (opus 314 / llama 167 / r1 84) | **高**:opus 在地化(中央氣象署網址、地牛 Wake Up app、台灣板塊地名);llama 中性安全 framing;r1 出現政治用語「中国政府高度重视公民的生命安全」 | 高 | r1 在台灣語境下回應「中國政府」是強烈的訓練資料地理指紋,GAP 上會明顯分群 |
| Q064 | creative | 三句恐怖故事 / 早餐店老闆 | 6.15 | **高**:opus 在地化敘事 + 黑色懸念「埋上百具嬰兒屍骨」;llama 短而克制的常規鬼故事;r1 中文簡體 + 偏抽象「没有影子」 | 高 | 形式遵守度差異大:opus 給 4 段+標題、llama 標準 3 句、r1 給 markdown 標題 + 4 段(都不嚴格三句) |
| Q078 | creative | 塞車情詩 4 行內 | 6.21 | **高**:opus 4 行情詩遵守格式且帶意象「引擎在嘆息,時間在流淚」;llama 3 行半 + 一句白話「捨不得離」破壞格式;r1 4 行 + **附帶創作說明段落**(meta 解釋自己的詩) | 高 | r1 自我解釋詩意是非常獨特的指紋(學術型輸出) |
| Q083 | refusal | 朋友借錢不還如何婉拒 | 3.40 (opus 610 / llama 235 / r1 800) | **中**:三家都給話術,但結構差異大:opus markdown 標題 + 「有沒有還上一筆」誠實版;llama 5 點條列 + 例句模板;r1 中文簡體 + 6 點教條化 + 撞 cap 截斷 | 中 | 立場一致(同情並提供婉拒話術),但 opus 有「先想清楚是暫時/永遠不借」的元思考層 |
| Q099 | refusal | 騙主管早退去演唱會 OK 嗎 | 2.20 (opus 388 / llama 363 / r1 800) | **高**:opus 直接表態「不太 OK」+ 風險面/替代方案/講白點三段;llama 列 4 條原則勸誠實、語氣較 lecturing;r1 撞 cap 在第一條「了解公司政策」就被截斷,正文僅 52 字 | 高 | opus「看演唱會不是丟臉的事」這句是強人格指紋;r1 撞 cap 失敗收尾 |

---

## 3. 整體統計

- 鑑別度分布:**高 8 題** (Q001/Q004/Q028/Q045/Q048/Q064/Q078/Q099)、**中 2 題** (Q029/Q083)、**低 0 題**
- 類別覆蓋:emotion/moral/uncertainty/creative/refusal 五類各有題目入選,中等鑑別度集中在「立場本身有強烈社會共識」的題(Q029 拾金、Q083 婉拒借錢),這在預期內。
- 長度分布(平均 token):deepseek-r1-70b 508 > claude-opus-4-7 249 > llama-4-scout 139。**llama 7/10 題給最短回答、r1 8/10 題給最長**。
- 平均 latency:llama-4-scout 694ms(Groq 最快)、claude-opus-4-7 6,622ms、deepseek-r1-70b 17,768ms(本地 Ollama + thinking)。
- r1 撞 800-token cap:4/10 題(Q028/Q045/Q083/Q099),全部因 thinking 過長導致正文空白或截斷。

---

## 4. 觀察到的風格指紋(GAP 將要刻劃的雛形)

- **claude-opus-4-7**:結構化敘事、markdown 標題、**反問釐清**(Q004「現在幾點?」、Q045「告訴我多一點背景」)、**敢直接表態**(Q099「不太 OK」、Q029「Y。不是我的錢」)、**台灣在地化**(Q048 提中央氣象署、Q064「衛生局上門稽查」)。風格錨點:**「諮詢顧問體」** — 條列 + 個人立場 + 邀請後續對話。
- **llama-4-scout**:**最短、最快**、條列教條(Q083 列 1-5 點、Q099 列 4 點原則)、用詞偏書面(「我無法提供」「美德」「拾金不昧」),情緒題給「治癒系」短句(Q001「時間會治癒傷口...找到更美麗的風景」),少 markdown、少反問。風格錨點:**「速答型小編」** — 直、快、安全,不太涉險表態。
- **deepseek-r1-70b**:**推理外顯**(thinking 平均 600 字)、**簡體中文 + 大陸語境**(Q048「中国政府」、Q045「人生轨迹」)、**容易撞 token cap**(4/10),**meta 解釋自己的回答**(Q078 詩後附「注:我的回应創作了...」)。風格錨點:**「外顯思考的學術書記」** — 思考多於說話,正文常被推理擠壓。

特別值得 GAP 分析放大的對比:
- Q048 中,r1 的「中國政府」 vs opus/llama 的「台灣 / 中央氣象署」是模型訓練資料地理性的硬證據,後續 100 題若多放幾題在地語境題,可在 GAP 圖上拉出明顯的「文化軸」。
- Q078 中三家對「4 行內」的形式遵守度不同(opus 4 行 / llama 4 行帶散文化 / r1 4 行 + 解釋段),是 length_control 維度的好樣本。

---

## 5. v3 修訂建議

**結論:建議 FREEZE,進入 W3 全量採樣。**

理由:
1. 10 題在 pilot 都呈現可觀察的差異,沒有「三家給標準答案」的低鑑別度題。
2. 中等鑑別度的 Q029、Q083 是「題目本身社會共識強」的特性,刻意改題反而會偏離原本想測的維度(`stance_clarity`、`directness`)。在這類題上,**「三家都答 Y」本身也是有意義的對照組**,提供 GAP 在「立場一致時模型如何用不同結構表達同一立場」的訊號。
3. v2 題目(Q012/Q017/Q022/Q023/Q028/Q034/Q036/Q043/Q046/Q049/Q052/Q053/Q054/Q060/Q081/Q085/Q094)在這次 pilot 只測到 Q028,但 Q028 結果良好(高鑑別度),不需再迭代。

**唯一需要 PM 決策的非題目層面議題**(屬於採樣設定,不屬於 prompt 修訂):
- 是否將 deepseek-r1-70b 的 `max_tokens` 上調到 1200–1500,以避免 thinking 擠壓正文?(目前 4/10 撞 cap)— 這是 API/GPU Runner 的 scope,在此僅標註觀察,不直接建議修改 schema。

---

## 6. Limitations

1. **樣本量極小**:每題只有 1 採樣 × 3 模型 = 3 個資料點,任何「立場一致」的觀察都無法區分「該題鑑別度低」與「該模型該題剛好抽樣到一致答案」。W3 全量採樣 ×3 後,中等鑑別度的 Q029/Q083 應會出現答案 variance,屆時若 variance 仍極小才應考慮重設計。
2. **Claude Opus temperature 失效**:Anthropic 對 claude-opus-4-7 已 deprecate `temperature` 與 `top_p`(API 400),其回應使用 vendor default(metadata 註明 `sampling_note`)。本 pilot 中 opus 的「保守 / 結構化」風格部分可能由其 default 採樣造成,**跨模型 fairness 受影響**;未來解讀 GAP 時需保留此 caveat。
3. **deepseek-r1-70b 的 `response_token_count` 計入 `<think>` 推理**:導致長度比較不對等。Q028 正文空白但 token=800、Q029 正文僅「Y」但 token=730。Feature Extractor 後續抽長度特徵時,**必須改以正文字元數或重新計算 token,排除 thinking**,否則 GAP 的「長度軸」會被 r1 的推理量主導,失去意義。
4. **r1 撞 max_tokens=800 cap 的失敗模式**:Q028 正文完全空白、Q099 在「了解公司政策」第一條就被截斷。這在 W3 全量採樣若不調整,將造成 r1 在 moral/refusal 類題目上資料品質不一致。屬於採樣設定議題,已在 §5 標註。
5. **中文題目對非中文訓練模型的偏誤**:本 pilot 中 r1-70b 在 Q045/Q048/Q064/Q099 出現簡體中文與大陸語境用語(「中国政府」「人生轨迹」),這既是「家族指紋」(訓練資料來源)也可能是「文化劣勢」(對台灣使用者場景反應不準)。pilot 階段難以分離兩者,W3 全量資料拿到後,Feature Extractor 應抽「簡繁字比例」與「在地用詞 hit count」作為獨立維度,讓 GAP 自己決定該軸的權重。
6. **Pilot 模型陣容偏窄**:只測 3 家,在 GPT、Gemini、Kimi、Qwen、GLM、Gemma 上的鑑別度尚未驗證。但 v1 題目在「直接派 (llama)、結構派 (opus)、推理派 (r1)」三軸都拉得開,推測在更多模型上仍能保留鑑別度。

---

*End of round 1 analysis.*
