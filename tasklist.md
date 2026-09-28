# Payment Reconciliation & Fee Explainer Agent — Step-by-step 任務清單

> **目標：** 用 Python FastAPI 建立後端，查詢模擬交易數據及檢索虛構 payment gateway 文件，回答手續費與對帳問題，並提供可核對的數字和文件引用。
>
> **資料限制：** 只使用自己生成的模擬交易及虛構文件；不要使用 Hantec 或任何公司的真實交易、客戶資料、內部文件或費率。
>
> **使用方法：** 按 Step 順序完成。每一步通過「完成檢查」才繼續；不需要按週趕進度。

## 技術選擇與整體路線

| 部分 | 選擇 |
|---|---|
| Backend API | Python + FastAPI |
| 結構化資料 | PostgreSQL + SQLAlchemy |
| Schema migration | Alembic |
| 文件向量儲存 | PostgreSQL + pgvector |
| Frontend | React + Vite |
| LLM／embedding | 選定一組 API 與模型後，記錄名稱及設定 |
| 本機資料庫 | Docker Compose |

```text
FastAPI 基礎
    ↓
PostgreSQL + 模擬交易
    ↓
虛構收費文件
    ↓
文件 ingestion + 搜尋（先不用 LLM）
    ↓
RAG 文件問答
    ↓
安全的交易查詢工具
    ↓
SQL + RAG 組合回答
    ↓
React + Vite Demo
    ↓
Evaluation 與優化
```

**前後端分工：** React 只負責輸入問題及展示答案；資料庫查詢、文件檢索、LLM 呼叫及 API key 都留在 FastAPI backend。

---

## Step 0：準備開發環境與專案

- [ ] 安裝 VS Code、Git、Python、Node.js（包括 npm）及 Docker Desktop。
- [ ] 在 VS Code 安裝 Python extension。
- [ ] 在終端機檢查 `python --version`（Windows 如有需要可用 `py --version`）、`git --version`、`node --version`、`npm --version` 及 `docker --version`。
- [ ] 建立資料夾 `payment-reconciliation-agent`，用 VS Code 開啟。
- [ ] 在根目錄保存本檔案為 `TASKLIST.md`。
- [ ] 執行 `git init`。
- [ ] 建立 `.gitignore`，至少忽略 `.env`、`.venv/`、`__pycache__/`、`.pytest_cache/`、`node_modules/`、`dist/`。
- [ ] 建立 `.env.example`，只放環境變數名稱及假值；真正密鑰放 `.env`，不要提交到 Git。

**完成檢查：** VS Code 終端機能執行上述工具；`.env` 不會被 Git 追蹤。

## Step 1：建立最小 FastAPI 專案

- [ ] 建立 `backend/`、`backend/app/` 及 `backend/tests/`。
- [ ] 在 `backend/` 建立及啟用 Python 虛擬環境 `.venv/`。
- [ ] 安裝 `fastapi`、`uvicorn`、`pytest`、`httpx`。
- [ ] 建立 `backend/app/main.py`，新增 `GET /health`，回傳 `{"status": "ok"}`。
- [ ] 啟動開發伺服器，測試 `/health` 及 FastAPI 自動產生的 `/docs`。
- [ ] 寫測試，檢查 `/health` 回傳 HTTP 200 及正確內容。
- [ ] 在 README 記錄建立虛擬環境、啟動服務及執行測試的方法。

**完成檢查：** 尚未接資料庫或 LLM，FastAPI 已可啟動，`/health` 測試通過。

## Step 2：定義系統要回答的問題

- [ ] 建立 `docs/core_questions.md`，寫下 10 個核心用戶問題。
- [ ] 為每題標記所需能力：文件 RAG、交易查詢，或兩者結合。
- [ ] 為每題列出必需資料，例如交易 ID、gateway、交易日期、費用組成及文件版本。
- [ ] 定義固定費、百分比費、FX 費、總費用、預期淨額、實際結算額及對帳差額的含義。
- [ ] 決定日期處理規則：資料庫用 UTC 儲存；「昨天」、「上星期」等按 Asia/Hong_Kong 解讀，轉成明確查詢範圍。

**完成檢查：** 對每條問題，你都能指出答案應從資料庫、文件，還是兩者取得。

## Step 3：啟動 PostgreSQL 並連接 FastAPI

- [ ] 在根目錄建立 `compose.yaml`，用 Docker Compose 啟動支援 pgvector 的 PostgreSQL。
- [ ] 在 `.env.example` 記錄資料庫連線所需的環境變數。
- [ ] 在 backend 安裝 SQLAlchemy、PostgreSQL driver 及 Alembic。
- [ ] 建立資料庫連線設定及連線測試。
- [ ] 初始化 Alembic；以後修改資料表結構都建立 migration。
- [ ] 確認重啟資料庫容器後，資料仍然存在。

**完成檢查：** FastAPI 可以連接 PostgreSQL；你知道資料庫如何啟動、停止及保存資料。

## Step 4：設計交易資料表

- [ ] 設計 `gateways`、`transactions`、`gateway_settlements`、`reconciliation_results` 等表。
- [ ] 金額在 Python 使用 `Decimal`，在 PostgreSQL 使用 `NUMERIC`；不要用浮點數計費。
- [ ] 為交易保存 gateway、交易類型、幣種、金額、時間、狀態及費用組成。
- [ ] 為對帳保存預期金額、實際結算金額、差額及不符標記。
- [ ] 建立 Alembic migration 及必要索引，例如交易 ID、gateway 與交易時間。
- [ ] 在 `docs/data_model.md` 解釋資料表關係及主要計算公式。

**完成檢查：** 你能解釋一筆交易如何對應 gateway 結算及對帳結果。

## Step 5：生成可重現的模擬交易

- [ ] 建立 `scripts/generate_data.py`，使用固定 random seed。
- [ ] 建立 3 個虛構 gateway，例如 NorthstarPay、HarborFlow、CedarGate。
- [ ] 先生成 20 筆可人工檢查的交易，再擴充至約 5,000 筆。
- [ ] 加入正常及刻意設計的異常案例：最低收費、費率改版、跨幣種 FX 費、退款、失敗交易及對帳差額。
- [ ] 確保生成程式可重複執行，不會意外插入重複資料。
- [ ] 寫測試核對交易數量、費用計算及已知異常案例。
- [ ] 在 README 記錄 seed、生成規則及重新產生資料的方法。

**完成檢查：** 你能找出幾筆指定交易，手動計算出與資料庫一致的費用。

## Step 6：撰寫虛構 gateway 文件

- [ ] 在 `docs/source/` 建立 3 個 gateway 的收費表、FX 規則及對帳 SOP，先使用 Markdown 格式。
- [ ] 至少為一個 gateway 編寫兩個不同時期生效的費率版本。
- [ ] 每份文件標示文件 ID、名稱、版本、gateway、章節、生效日期；如適用，亦標示失效日期。
- [ ] 條款清楚說明適用交易、計費基礎、百分比、固定費、最低費及例外。
- [ ] 確保文件條款與 Step 5 的模擬資料生成邏輯一致。
- [ ] 在文件加入可人工核對的計算例子。

**完成檢查：** 不用 LLM，你也能從文件找出某筆交易發生時適用的條款。

## Step 7：做文件 ingestion；先不要接 LLM

- [ ] 建立 `document_chunks` 表，保存 chunk 內容、文件 ID、章節、版本、生效日期及來源路徑。
- [ ] 寫 ingestion 程式讀取 `docs/source/` 下的 Markdown。
- [ ] 優先按標題／章節分 chunk；章節過長時才再細分。
- [ ] 確保同一份文件重複 ingestion 不會產生重複 chunks。
- [ ] 寫檢查指令，列出指定文件的 chunks 及 metadata。
- [ ] 檢查費率與相關例外條件沒有被切開至失去上下文。

**完成檢查：** 在資料庫能找到文件各章節的內容、來源及適用日期。

## Step 8：加入 embedding 與文件搜尋

- [ ] 選擇 embedding model，記錄名稱及向量維度。
- [ ] 在 PostgreSQL 啟用 pgvector，為 chunk 加入對應維度的向量欄位。
- [ ] 為文件 chunks 產生 embeddings 並存入資料庫。
- [ ] 先寫**不使用 LLM**的搜尋函式：輸入問題，輸出相關 chunks、來源及相似度。
- [ ] 在適用情況下，按 gateway、文件類型及交易日期過濾文件。
- [ ] 手動試 10 條文件問題，記錄有沒有找到正確章節及版本。
- [ ] 先確保搜尋結果正確，之後才研究向量索引及效能優化。

**完成檢查：** 問某 gateway 的 FX 費如何計算時，搜尋結果包含正確、當時有效的條款。

## Step 9：建立第一個 RAG 文件問答 API

- [ ] 在 backend 加入 LLM API 設定；API key 只存於 backend 使用的環境變數。
- [ ] 建立 `POST /api/ask-document`：接收問題 → 搜尋文件 → 將段落及來源交給 LLM → 回傳答案及引用。
- [ ] 要求模型只根據檢索到的文件解釋條款；證據不足時明確說明無法確認。
- [ ] 回傳結構化引用：文件 ID、名稱、版本、章節及 chunk ID。
- [ ] 測試可回答問題、無答案問題，以及新舊版本容易混淆的問題。
- [ ] 人工檢查引用內容是否真的支持答案；不能只看答案有沒有附文件名稱。

**完成檢查：** 文件問題有可核對的引用；文件沒有答案時不會亂編。

## Step 10：建立安全的交易查詢工具

- [ ] 先寫普通 Python 函式：`get_transaction`、`list_reconciliation_mismatches`、`aggregate_fees`、`compare_transactions`。
- [ ] 為每個函式定義輸入、輸出、錯誤情況及測試。
- [ ] 使用 SQLAlchemy 或參數化查詢；不要拼接用戶提供的 SQL 字串。
- [ ] 限制時間範圍、最多回傳筆數及查詢時間。
- [ ] 為問答查詢準備唯讀資料庫帳號；migration 和資料生成則使用另一个具寫入權限的帳號。
- [ ] 回傳可核對的交易 ID、費用欄位、時間範圍及彙總數值。

**完成檢查：** 尚未使用 agent，直接呼叫 Python 函式已能正確回答交易數據問題。

## Step 11：加入 tool calling，組合 SQL 與 RAG

- [ ] 只讓 LLM 呼叫已定義的交易查詢工具及文件檢索工具；不要提供任意 SQL 執行工具。
- [ ] 驗證每次工具呼叫的參數，設定最多工具呼叫次數。
- [ ] 為「為何這筆提款比上月貴？」實作流程：
  1. 查指定交易；
  2. 找可比較的上月交易；如有多個而比較準則不明，先澄清；
  3. 找兩筆交易各自發生時適用的文件版本；
  4. 根據查到的數字及條款形成答案。
- [ ] 答案區分「資料庫事實」、「文件條款」、「計算／解釋」及「尚未確認的部分」。
- [ ] 記錄工具名稱、查詢條件、結果摘要及文件引用，方便除錯。

**完成檢查：** 一條問題可同時查交易及文件；數字與費率均有可核對來源。

## Step 12：用 React + Vite 建立第一版 Demo

- [ ] 在根目錄建立 `frontend/` React + Vite 專案。
- [ ] 先做單頁介面：問題輸入框、送出按鈕、答案區域及引用區域。
- [ ] 用 `fetch` 呼叫 FastAPI 的 `/api/...` endpoint。
- [ ] 本機開發使用 Vite proxy 將 `/api` 請求轉發到 FastAPI，避免在元件內硬寫 backend 位址。
- [ ] 顯示相關交易 ID、文件版本／章節，以及系統使用的查詢時間範圍。
- [ ] 加入載入中、查無資料、證據不足及 API 錯誤狀態。
- [ ] 加入 3–5 條可點選的示範問題。
- [ ] **保持介面簡單：** 暫時不加狀態管理庫、複雜 routing 或多頁 dashboard。
- [ ] 測試完整流程：啟動 Docker → 啟動 FastAPI → 啟動 Vite → 提問 → 查看答案及來源。

**完成檢查：** 在 React 頁面能完整展示 SQL + RAG 的回答；LLM API key 不會出現在 frontend。

## Step 13：建立 evaluation 基線

- [ ] 建立 `eval/questions.jsonl`，準備 40 題：文件問答、交易查詢、混合問題及無答案問題。
- [ ] 為每題保存預期答案要點、正確交易 ID／數值、適用文件版本與章節。
- [ ] 數值標準答案由資料庫查詢或資料生成規則驗證，不單靠另一個 LLM 生成。
- [ ] 寫評測程式，分開統計交易數值正確率、檢索命中率、引用正確率及無答案處理。
- [ ] 記錄每題延遲、token 用量及估算 API 成本。
- [ ] 保存資料版本、prompt 版本、模型名稱及第一版結果。

**完成檢查：** 有可重複執行的 40 題測試及第一版真實分數。

## Step 14：根據失敗案例優化

- [ ] 將錯誤分類：查錯交易、找錯文件版本、找不到章節、計算錯誤、引用不支持結論等。
- [ ] 每次只改一項主要因素，例如 chunking、metadata filter、prompt、關鍵字搜尋或 reranking。
- [ ] 用同一批題目重新評測，記錄準確率、引用、延遲及成本的變化。
- [ ] 在 `eval/experiments.md` 記錄有效及無效的嘗試。
- [ ] 更新 README：架構、啟動方法、示範問題、評測結果與已知限制。

**完成檢查：** 你能用具體數字解釋每項修改帶來的改善及代價。

## 建議目錄結構

```text
payment-reconciliation-agent/
├── TASKLIST.md
├── README.md
├── .gitignore
├── .env.example
├── compose.yaml
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── .venv/             # 不提交到 Git
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── core_questions.md
│   ├── data_model.md
│   └── source/
├── scripts/
│   └── generate_data.py
├── data/
└── eval/
    ├── questions.jsonl
    ├── experiments.md
    └── results/
```