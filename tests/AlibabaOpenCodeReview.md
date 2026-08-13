
Z:\open-code-review

https://www.youtube.com/shorts/M1Dyg-hd7i0

這三款工具定位不同：**Alibaba Open Code Review (OCR)** 是開源 CLI、可自帶模型；**Claude Code Review** 是 Anthropic 託管的 GitHub PR 自動審查服務（多代理、行級評論）；**Antigravity Review** 則是編輯器內建、以靜態分析＋AI 的多維度審查（安全/效能/架構等）。 [github](https://github.com/alibaba/open-code-review)

## 快速比較表

| 維度       | Alibaba Open Code Review                                           | Claude Code Review                                                                | Antigravity AI Code Review                                                    |
| ---------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 形態       | 開源 CLI (`ocr`)，可整合到 Claude Code 等 Agent                  | 託管服務（GitHub App）＋本地`/code-review` 指令                                 | 編輯器功能（Antigravity Editor）＋可接 GitHub Actions                         |
| 授權/費用  | Apache-2.0 免費；只付 LLM inference 費用                           | Team/Enterprise 可用；按 token 計費（每 PR 約 $15–25）                           | 產品頁面未公開定價；以編輯器授權為主                                          |
| 部署方式   | 本地/CI 自行部署，可選 OpenAI/Anthropic 等模型端點                 | 雲端託管（Anthropic 基礎設施）；也可用本地`/code-review`                        | 編輯器內建；可設定專案`.antigravity-review.yml`                             |
| 審查範圍   | Git diff 為單位；支援分支範圍、單 commit、staged 等                | GitHub PR 自動觸發（開 PR/每次 push/手動）；也可本地 diff                         | 檔案/專案層級；提供 Security/Performance/Style/Testing 等模式                 |
| 核心架構   | **確定性工程＋LLM Agent**：規則匹配、檔案捆綁、定位/反思模組 | **多代理平行分析**：不同代理看不同問題類別，再驗證去重                      | **靜態分析＋ML**：七維度（安全、效能、品質、Bug、架構、測試、可維護性） |
| 行級精準度 | 強調「位置漂移」問題，有外部定位與反思模組提升準確度               | 行級 inline comment＋Check Run 註解；嚴重度分級（Important/Nit/Pre-existing）     | 行級建議（含嚴重度 Critical/High/Medium）                                     |
| 可客製化   | 四層規則優先級（CLI flag > 專案 > 全域 > 內建），可自訂 JSON rules | `CLAUDE.md`（專案記憶）＋`REVIEW.md`（審查專用指令）調整 flagged 內容與嚴重度 | `.antigravity-review.yml` 自訂規則；可抑制特定問題                          |
| 整合生態   | 可當 Claude Code Skill/Plugin；也有 WebUI viewer (`ocr viewer`)  | 深度 GitHub 整合（PR comment、Check Run、用量分析儀表板）                         | 編輯器工作流；可接 GitHub Actions 做 PR 自動審查                              |
| 適合場景   | 想要開源、可自帶模型、在本地/CI 跑、重視穩定性與位置準確           | 團隊已用 Claude Code、要 GitHub PR 自動審查、可接受託管費用                       | 單人/小團隊在編輯器內即時反饋、想一次看多維度（安全/效能/架構）               |

 [github](https://github.com/alibaba/open-code-review)

## Alibaba Open Code Review 的優點（相對 Claude/Antigravity）

- **開源且模型自由**：Apache-2.0 授權，軟體本身免費；可接 OpenAI/Anthropic 或其他端點，成本可控。 [github](https://github.com/alibaba/open-code-review)
- **確定性＋Agent 混合架構**：用工程邏輯保證「一定不能錯」的步驟（檔案選擇、捆綁、規則匹配、定位/反思），減少純提示詞驅動的不穩定與位置漂移。 [github](https://github.com/alibaba/open-code-review)
- **精細規則系統**：四層規則優先級（CLI > 專案 > 全域 > 內建），可用 glob 匹配自訂審查規則，適合企業內部規範落地。 [github](https://github.com/alibaba/open-code-review)
- **大規模實戰驗證**：源自阿里內部兩年、數萬開發者、百萬缺陷發現的生產系統，針對大 changeset 的併發與穩定性有實戰背書。 [github](https://github.com/alibaba/open-code-review)
- **本地/CI 友好**：CLI 設計，易嵌入既有 CI；也有 WebUI viewer 查看審查會話紀錄。 [github](https://github.com/alibaba/open-code-review)

## Claude Code Review 的優點（相對 OCR/Antigravity）

- **GitHub PR 深度整合**：自動在 PR 開啓/每次 push 觸發，行級 inline comment＋Check Run 註解，並提供用量儀表板與嚴重度統計。 [code.claude](https://code.claude.com/docs/en/code-review)
- **多代理＋驗證去重**：多個專用代理平行分析，再對候选問題做行為驗證、去重與嚴重度排序，降低假陽性。 [code.claude](https://code.claude.com/docs/en/code-review)
- **可調審查行為**：透過 `CLAUDE.md`/`REVIEW.md` 直接影響 flagged 內容、嚴重度定義、Nit 上限、跳過路徑等。 [code.claude](https://code.claude.com/docs/en/code-review)
- **團隊協作體驗**：可在 PR 上對發現按 👍/👎 回饋， Anthropic 會收集用於優化；也支援手動 `@claude review` 觸發。 [code.claude](https://code.claude.com/docs/en/code-review)

## Antigravity AI Code Review 的優點（相對 OCR/Claude）

- **七維度一站式審查**：安全、效能、程式品質、Bug、架構、測試覆蓋、可維護性一次看，適合單人開發者快速全貌掃描。 [antigravitylab](https://antigravitylab.net/en/articles/editor/ai-code-review)
- **編輯器內即時反饋**：在 Antigravity Editor 中按鍵即得分析，並提供 Security/Performance/Style/Testing 等模式切換。 [antigravitylab](https://antigravitylab.net/en/articles/editor/ai-code-review)
- **可專案化設定**：`.antigravity-review.yml` 統一團隊標準，並可 inline 抑制特定問題。 [antigravitylab](https://antigravitylab.net/en/articles/editor/ai-code-review)

## 怎麼選（實務建議）

- 你已在用 **Claude Code** 且團隊要 **GitHub PR 自動審查**：優先選 **Claude Code Review**（託管、整合度最高）。 [code.claude](https://code.claude.com/docs/en/code-review)
- 你想要 **開源、可自帶模型、在本地/CI 跑**，且重視 **行級位置準確與規則可控**：選 **Alibaba Open Code Review**。 [github](https://github.com/alibaba/open-code-review)
- 你主要用 **Antigravity Editor**，希望 **編輯器內即時、多維度**（尤其安全/架構/測試）反饋：選 **Antigravity Review**，並用 `.antigravity-review.yml` 收斂假陽性。 [antigravitylab](https://antigravitylab.net/en/articles/editor/ai-code-review)

如果你願意，我可以依你的工作流（例如：Xilinx/FreeRTOS 專案、是否用 GitHub、是否已有 Claude Code 訂閱）給一個更貼合的導入方案與設定範例。
