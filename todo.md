# https://www.gitagent.sh

# https://repoinside.com/open-gitagent/gitagent

gitagent.sh
GitAgent：Git-Native AI Agent 開放標準
三個核心檔案（agent.yaml + SOUL.md + SKILL.md）定義 AI agent
可攜式 agent 定義 (龍蝦也是類似架構，但是還多了 Memory 管理）
支援匯出到 Claude Code、OpenAI Agents SDK、CrewAI、Google ADK、LangChain

- 天生繼承 git 的版本控制
- branching promotion（dev→staging→main）
- PR review 做 human-in-the-loop

# https://github.com/awesome-skills/code-review-skill

- https://zhuanlan.zhihu.com/p/2015725269667840386

• Anthropic 官方 Skills 仓库：https://github.com/anthropics/skills

• Anthropic 官方 Plugins 仓库：https://github.com/anthropics/claude-plugins-official

• Awesome Claude Skills 社区列表：https://github.com/travisvn/awesome-claude-skills

• Claude Code Skills 文档：https://code.claude.com/docs/en/skills

• Skills 市场：https://skillsmp.com/

/brooks-lint:brooks-review 触发 PR 审查，/brooks-lint:brooks-audit 做架构审计。

## #


我已經針對 **Phase 131: 知識庫反向檢索與分享** 完成了詳細的 GSD 研究與計畫制定。

這次的實作重點在於讓 LineBot 具備「搜尋」能力：

1. **關鍵字 `?`** ：直接對話式詢問 NotebookLM 大腦。
2. **關鍵字 `get:`** ：搜尋 Google Drive 檔案並回傳下載/檢視連結。

詳細的改動點請參考 `implementation_plan.md`。在進入 **Execute (執行)** 階段前，有一個關鍵的資安選擇需要您的確認：

IMPORTANT

* **關於 Google Drive 檔案分享權限 (Security Issue)** 當使用者搜尋到檔案並要求獲取連結時，如果該檔案目前是私有的，系統需要透過 API 將其權限變更為  **「任何知道連結的人皆可讀取 (anyoneWithLink)」** ，這樣 Line 的使用者點開連結時才不會被擋在 Google 登入畫面外。

**您是否同意系統在執行 `get:` 搜尋指令後，自動調整匹配檔案的分享權限？** (如果是放在一個本身就已經公開的資料夾，則不會有額外的權限變更行為)

## 五、 進階技巧：把提示詞「說兩次」

把同一段提示詞完整貼上兩次（Prompt Repetition），就能在不拉長輸出內容、幾乎不加成本的情況下，顯著提升很多 LLM 的表現。

這是因為多數模型是因果語言模型，注意力是「單向」的，模型在讀前半段（例如問題）時看不到後半段（例如背景文章），所以會出現理解力不足的情況。若把整段「問題＋背景」重複一次，模型在讀「第二輪的問題」時，前面那一整輪「問題＋背景」已經都在它的「過去」裡了，等於用很粗暴的方式，逼它在同一個序列裡可以注意到所有 token。

## 一、4個提問心法，讓AI成為思考夥伴

1. **請 AI 「教你怎麼問」：** 當你對主題不熟悉時，直接問：「我想了解 [XX 主題]，我該如何提問才能獲得最精準的答案？」或「你還需要哪些背景資訊，才能提供更好的建議？」
2. **先拆解、後內化：** 面對大題目（如：產業分析）時，請 AI 先將其拆解為一系列小問題。最後用你自己的話重新記錄對話結論，這能幫你檢視推論邏輯，避免「外包大腦」而失去判斷力。
3. **跨模型交叉詰問：** 養成「讓不同 AI 互相質疑」的習慣。例如：將 Gemini 生成的報告丟給 Claude 挑錯，補足單一模型的盲點。
4. **「英文問、中文答」策略：** 由於模型訓練資料以英文為主，用英文提問通常能獲得更深度的內容。但在處理台灣法規或在地文化時，則應切換回中文並具體指名（如：台灣勞基法第幾條）。

# 這是 Google 針對 Workspace Gemini 推出的指令標準模組：

* **角色 (Persona)** ：設定 AI 應扮演的角色、職位或身分。例如：你是一位 [產業] 的專案經理。
* **任務 (Task)** ：明確指出您希望 AI 執行的具體工作。這是提示詞中最重要的部分，請務必包含明確的動詞或指令（例如：撰寫、總結、改變語氣等）。
* **背景資訊 (Context)** ：提供相關的背景細節、參考資料或情境，讓 AI 根據這些資訊生成內容。例如：根據 [相關專案文件的細節]。
* **格式 (Format)** ：指定輸出的形式或呈現方式。例如：「限制使用列點方式呈現」 或「整理成表格格式」。

git cli
https://ithelp.ithome.com.tw/articles/10240215

https://deepwiki.com
