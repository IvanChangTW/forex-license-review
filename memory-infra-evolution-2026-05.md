# 跨 AI Agent、跨機器長期記憶管理：架構演化進程

**期間**：2026/05/06 — 2026/05/14（9 天）
**範圍**：4 端（公司 Windows × Claude Code/Codex、家裡 Mac × Claude Code/Codex）+ Notion 工作日誌 + Claude Chat
**作者**：Ivan + Claude Chat（claude.ai web）整理
**日期**：2026/05/14

---

## 整體軸

9 天內、從零建立到生產級的個人 AI 工作流記憶治理系統。**每一天加的不是 incremental feature、而是 architectural step**：

```
Day 0 (5/06)  ●  Notion 工作日誌資料庫誕生（記錄起點）
Day 1 (5/07)  ●  跨機器同步架構奠基（claude-memory repo）
Day 2 (5/08)  ●  跨 agent（Codex 接入 + 雙端 Notion）
Day 3 (5/09)  ●  跨對話視窗 SOP 對稱化
Day 4 (5/10)  ●  方法論首次正式提取（firm rule 第 8/9 條）
Day 5 (5/11)  ●  2.1 升級：tier 編譯 + cross-agent baton 概念
Day 6 (5/12)  ●  從紀律到自動化：health 哨兵 + inline 邊界 pattern
Day 7 (5/13)  ●  外部對照 + selective load pilot（Path A）
Day 8 (5/14)  ●  SOP 正式化 + parity 收斂（baton + defaults）
```

關鍵特徵：
- **每階段都先研究外部對照後再決定內部設計**（cc-switch / Hermes / PLUR / superpowers / Cowork），不閉門造車
- **每階段產出至少一條可重用方法論**，且方法論寫進 memory 自己（feedback_*.md）
- **每階段都經得起跨 4 端 + Notion 工作日誌的證據追溯**
- **設計哲學一以貫之**：explicit authoring、git 為 SSOT、local-first、與 31 年手寫日記哲學對齊

---

## 一、時間軸

### Day 0（2026/05/06）— Notion 工作日誌資料庫誕生

當天還沒有跨機器 memory 概念。三件事打下後續基礎：

- **RunLossReport AHK 重構 + Notion MCP 接通 + Git 身份統一** — Notion 接通後、開始把日常工作對話結論寫進結構化頁面、為日後跨日 memory 提供 raw 來源
- **family-assets 從零打造 + 公網部署 + Notion 同步** — 第一個生產級個人專案、走 Cloudflare Tunnel + 零公網 IP 模式、奠定 self-hosted infra 哲學
- **family-allowance 主題系統大擴增 + 認證重寫 + 多板佈告欄**

當天**沒有意識到「memory infra」是獨立 problem**、只是把日常結論寫進 Notion 試試。

---

### Day 1（5/07）— 跨機器同步架構奠基

跨出 Notion 後第一個真正的 memory infra 設計。核心 commit 落定：

**架構決策**：

```
claude-memory/                  ← GitHub private repo, SSOT
├── shared/                     ← 四端共用
├── office/                     ← 公司 Windows only
├── home/                       ← 家裡 Mac only
└── scripts/                    ← sync-{office,home,codex}.{ps1,sh}
```

**關鍵設計（首次落定）**：

| 設計 | 為什麼 |
|---|---|
| GitHub repo 為 SSOT | 與 Claude Code 本地檔 + auto-load 機制對齊、不把 Notion 塞進不擅長的 use case |
| `MEMORY.<scope>.md` 由 sync 串接生成、**不 commit** | 索引片段各 scope 自己維護、避免兩地手動同步 |
| `reference_claude_memory_repo.md`（meta-memory）| 「memory 自己的規則」也是 memory；新對話 auto-load 就懂規則、不用每次重新解釋 |
| SessionStart hook 自動 `git pull` + hash 比對 no-op | 解掉「100 個無意義 .bak」+ 「PowerShell Set-Content 偷加 CRLF」兩個隱形坑 |
| `.gitattributes` 鎖死 line endings | `.sh` 在 Mac 不會炸 — 經驗值不是試出來的 |

**這天之後的所有改動、都是這個架構的延伸或精修。**

---

### Day 2（5/08）— Codex 跨機器整合

把 Codex（公司端 + 家裡端兩個 host）也接進 memory 系統。三條動作：

- **家 Mac 端跨機 memory 接通**（sync-home.sh 落地）
- **Codex 跨機器 memory 整合 + 接 Notion + 抽 notion_helper**
- **公司 Codex + 家裡 Codex 端 Notion 接通驗證**

此時 4 端架構正式成形：

| 端 | Agent | Memory 載入機制 |
|---|---|---|
| 公司 Win10 | Claude Code | SessionStart hook `git pull` + 本機 memory dir |
| 公司 Win10 | Codex | sync-codex.ps1 編譯 AGENTS.md |
| 家裡 Mac | Claude Code | SessionStart hook + 本機 memory dir |
| 家裡 Mac | Codex | sync-codex.sh 編譯 AGENTS.md |

但**仍有 asymmetry**：四端 SOP、開工儀式、收工儀式各有微差、未來幾天會 align。

---

### Day 3（5/09）— Codex SOP 對稱化 + 跨對話視窗

收尾「四端可用、但 SOP 不對稱」的 debt。三件事：

- **付款方式三段式設計**（family-allowance）— 業務面、非 memory infra 直接相關
- **Codex SOP 對稱化** — 公司 Codex 跟家裡 Codex 開工流程拉齊
- **跨對話視窗 SOP** — 跨日、跨 session、跨機器之間的「下個 agent 該讀什麼、按什麼順序」第一次明文化

開始浮現「**跨 agent baton**」概念的雛形 — 但還沒命名、是隱含的「開工 SOP」。

---

### Day 4（5/10）— 紀律驗證 + 方法論首次提取

family-allowance 一日 22 commits / 10 件大改、過程中 SOP 被三度驗證。當天提取**首批正式方法論**：

- **第 8 條 firm rule**（具體內容是 family-allowance 業務面決策、不在 memory infra 範圍）
- **第 9 條 firm rule** — 同日成功應用、形成「rule 寫下 → 同日就用 → 驗證有效」的快循環

**這是「方法論文件化」這個 pattern 第一次自然發生**（不是某次刻意做、是工作過程自然產出）。後續 5/12 inline_size_limits 等都是這個 pattern 的延續。

---

### Day 5（5/11）— 2.1 升級：tier 編譯 + cross-agent baton 閉環

當天兩個 architectural step 同步推進：

#### Codex 記憶管理 2.1：從拼接到編譯

**問題**：AGENTS.md 一路加東西、~32 KiB 接近 Codex prompt 預算上限。

**解法**：把 AGENTS.md 從「直接拼接」改成「依 `codex_tier` 標籤編譯」。

| Tier | 處理 |
|---|---|
| `core` | 全文進 AGENTS.md |
| `summary` | 只進 summary 段 |
| `detail` | 只列檔名 + 一行描述、agent 需要時自己讀 |
| `off` | 完全不進 |

**結果**：~32 KiB → ~13.6 KiB（41%）。預算空間打開、後續加新 SOP 不再撞天花板。

#### Cross-agent baton 概念閉環

當天首次正式運作「Claude Code 提疑問 → 使用者橋接 → Codex 驗證 → 回寫」的 round-trip、約 12 分鐘。寫進 `reference_codex_memory_strategy.md`、首次成為**可命名的 architectural pattern**。

但此時還是**口頭傳遞為主、markdown 為輔**。後續幾天會 invert。

#### 衍生方法論
- **Architecture change checklist** — 5/7 寫的 SOP 5/11 升級時沒同步改、踩坑後寫進 strategy 檔當預防
- **「shared/ 是共用 source、不是等同 context」** — Claude 看全文、Codex 看編譯版、shared 不等於對等

---

### Day 6（5/12）— 從紀律到自動化

5/11 之前所有「紀律」都是 markdown 描述（agent 讀過自己記得）。5/12 開始把紀律寫成 enforcement script。

#### 五件 architectural step

1. **`memory_health.ps1`** — 哨兵化、不只是 reference 文件
   - AGENTS.md byte 接近上限警告
   - `codex_tier: core` 檔全數入編譯（沒漏）
   - `shared/` 與 `office/` / `home/` 沒互引（cross-scope leak 偵測）
   - 最近 sync timestamp
2. **`project_lifecycle_health.ps1`** — lifecycle 從文件變執行
   - 30 天無 commit → warn
   - 90 天無 commit → suggest archive
3. **Inline 邊界全套 propagate** — 8 份 status card + MEMORY.shared + feedback_daily_workflow 都加邊界
4. **`feedback_daily_workflow.md` 拆檔** — hub + morning / evening / memory_write / cross-day / home-Claude 5 個專檔
5. **Detail tier 雙層驗證**
   - Claude 端 sync-codex 加 5 行 PowerShell 存在性檢查
   - Codex 端 SOP 加「first-5-message verify 1 個 detail 檔可讀」

#### cc-switch 研究（5/12 evening）

研究 cc-switch repo、原本標題寫「吸收 CC-Switch guardrails」、事後驗證**cc-switch 跟我們場景不對應**（它做 provider config switching、我們做 memory governance）。

更新標題拿掉「受 cc-switch 啟發」。但**啟發是真的** — 「guardrail 該被產品化」這個設計衝動驅動當天從紀律到自動化的轉折。研究外部對象的價值不只在「採納什麼」、也在「觸發什麼設計衝動」。

#### 衍生方法論

**Inline boundedness 兩層 pattern**：

| 層 | 規則 | 範例 |
|---|---|---|
| 條目層 | 什麼時機把條目從檔內移走 | P0 done → 移除（不留 ✅）|
| 檔層 | 什麼時機本檔該拆成多檔 | backlog >10 條 → 拆 BACKLOG.md |

且**閾值要可觀察**（>10 條 / >30 天無 commit OK；「感覺太肥」NG）。

這條 pattern 寫進 `feedback_inline_size_limits.md`、後續 5/14 selective load 決策時自然應用、見 Day 8。

---

### Day 7（5/13）— 外部對照 + selective load pilot

當天**密度最高**的一天、三個外部架構研究 + 一個重大實作：

#### 外部架構研究

| Repo | 結論 | 採納內容 |
|---|---|---|
| **Hermes Agent**（NousResearch）| 同 problem space、互補設計；我們 indexed memory + scope 分割比社群提案領先 2 天 | 寫成 9 章節提案、提 3 條（includes / backend abstraction / scope-vs-profile）|
| **PLUR**（plur-ai）| 對立哲學（auto-emerge vs explicit authoring），不採納工具、僅吸收 3 條概念 | mem-used trailer / access count / type 四分法（提案 v1.0、待 Path A 完成後執行）|
| **superpowers**（obra）| Skill = enforced + auto-triggered（vs memory = passive loaded）；我們缺 skill layer 但**use case 不需要** | 不採納、但確認自己的 use case 是 state-centric、不是 methodology-centric |

#### Hermes 提案 → Codex 實作（同日）

**Claude Chat 起草 9 章節 markdown 提案 → Codex 接到後直接落地 Proposal 2/3 + Proposal 1 Path A pilot**。Codex 補上提案漏掉的 `codex_load: include_only` flag（提案只寫 `includes:` 陣列、沒寫如何讓被引用檔預設不進選集、Codex 補對了）。

#### 家裡端 Path A pilot 驗證 + reliability round（同日晚）

- 家裡 Codex 補上 `memory_health.sh`（Bash parity）
- 清掉 7 個 shared cross-scope warning
- macOS shasum locale warning 局部修法（只在 sha() helper 內固定 LC_ALL=C、不污染全局 shell）

#### 衍生方法論

- **「Selective」需要 declaration + exclusion 兩件**（Codex 補的 include_only 是這條的活例）
- **Pilot → reliability baseline → expansion**：當 pilot 證明 breadth 夠、下一步應補 reliability baseline、不是繼續擴 coverage
- **Health check 抓 warning 時、預設動作是「驗證 warning 是否真實」、不是「降 check 標準」** — 修問題、不修 check
- **局部、可證明無副作用的 fix**（locale 修法只在 helper 內、不全域）— 對應「最小爆炸半徑」哲學
- **Markdown-as-baton vs verbal-as-baton trade-off**（會在 5/14 正式化）

---

### Day 8（5/14）— SOP 正式化 + parity 收斂

5/13 累積的觀察、5/14 收斂成正式 SOP：

#### 三件 architectural step

**(a) Cross-agent baton SOP 正式化**

新增 `shared/feedback_cross_agent_baton.md`。**雙層規則**：

| 層 | 角色 | 規則 |
|---|---|---|
| Primary | Markdown 留存層 | source-of-truth、必信 |
| Secondary | 口頭交接 | 補速度、不替代 markdown |

順序顛倒就 drift。Baton 規則接回 4 個入口（MEMORY.shared / Claude 早上開工 / 家裡 Claude SOP / Codex 日常 workflow）。

**(b) memory_health 雙端 defaults 共用**

新增 `scripts/memory_health.common.env`、抽出 6 個最容易 silent drift 的 defaults：MAX_BYTES / WARN_BYTES / DEFAULT_STALE_HOURS / REQUIRED_CORE_ENTRY / VALID_TIERS / VALID_LOADS。

**沒抽的部分**（檢查邏輯、輸出格式、subprocess handling）保留兩份實作 — Bash vs PowerShell 差異太大、強求同碼會引入更多 bug。

**(c) Selective load 第 3 題：先 observe**

評估 Path A 擴張到 `project_status_*` 的時機、結論「先 observe 不擴」。**觸發條件設明確**：AGENTS 逼近 26 KiB / 依賴關係重複出現。

#### 衍生方法論

- **跨 shell parity 不是追求同碼、是先共用最容易 drift 處** — 應用範圍超出 memory infra
- **Baton 穩定性靠 markdown 留存層、口頭只是速度補充** — 順序顛倒就 drift
- **`feedback_inline_size_limits.md` 兩層 pattern 在生產環境第一次自然應用** — 5/11 寫下規則、5/14 在不被提醒情況下用它做決策。SOP propagation 成功的標準是「agent 自然 frame 決策用這條規則」

---

## 二、架構演化的三個 abstraction layer

整個演化可以拆三層、且每層各自有 evolution arc：

### Layer 1 — State（memory files 本身）

```
5/06 ─ 工作日誌寫進 Notion（單一 surface）
5/07 ─ claude-memory repo 建立（shared / office / home / scripts）
5/08 ─ Codex 接入、四端同步運作
5/13 ─ frontmatter includes 機制（reference_* 三檔 pilot）
5/14 ─ 維持 selective load 範圍、不擴
```

### Layer 2 — Process（sync / health / lifecycle 等執行碼）

```
5/07 ─ sync-{office,home,codex}.{ps1,sh} 落地
5/11 ─ codex_tier 編譯機制（從拼接到 build）
5/12 ─ memory_health.ps1 + lifecycle_health.ps1（enforcement、非 reference）
5/13 ─ memory_health.sh（家裡端 Bash parity）+ macOS locale 局部修
5/14 ─ memory_health.common.env（雙端共用 defaults）
```

### Layer 3 — Methodology（SOP / feedback / awareness 等規範）

```
5/07 ─ reference_claude_memory_repo.md（meta-memory）
5/09 ─ 跨對話視窗 SOP 雛形
5/10 ─ 第 8/9 條 firm rule
5/11 ─ architecture change checklist + shared ≠ context 兩條 awareness
5/12 ─ feedback_inline_size_limits.md（兩層 pattern）+ feedback_daily_workflow 拆檔
5/13 ─ Path A pilot 紀律 + 「pilot → baseline → expansion」
5/14 ─ feedback_cross_agent_baton.md（雙層 baton 規則）
```

**自指模式（self-referential）**多次發生：
- Layer 3 的方法論寫好後、變成 Layer 2 的 enforcement script
- Layer 1 的 pattern 觀察後、抽象成 Layer 3 的 methodology
- 例：CURRENT_WORK backlog 紀律（5/11） → inline_size_limits methodology（5/12） → selective load 決策（5/14）

---

## 三、Cross-agent Baton 的演化軌跡（special focus）

整段歷程裡「跨 agent 協作」這條軸演化軌跡特別清晰：

### Stage 1 — 隱含（5/06-5/10）
跨 agent 工作存在、但沒被命名。每次跨 agent 都靠 ad-hoc 重新建立 context。

### Stage 2 — 命名（5/11）
Claude Code ↔ Codex 一次成功 round-trip 之後、首次寫進 `reference_codex_memory_strategy.md`。**口頭傳遞為主、markdown 為輔**。

### Stage 3 — 跨組合驗證（5/13）
Claude Chat ↔ Claude Code 也成功跑通。Baton pattern 不限定特定 agent pair、是通用 pattern。

### Stage 4 — Payload 形式對比（5/13）
**Markdown-as-baton vs verbal-as-baton trade-off** 首次浮現：

| 形式 | 上游成本 | 下游行為 | Trade-off |
|---|---|---|---|
| Verbal-as-baton | 低 | Agent 容易 ask-back、catches edge case | Sanity check 自然發生 |
| Markdown-as-baton | 高 | Agent 容易直接做、跳過 ask-back | 失去 ask-back 的 sanity check |

選擇規則：**任務 reversible / 風險低 → markdown；任務 irreversible / 設計分歧大 → verbal 留問答空間**。

### Stage 5 — 正式 SOP（5/14）
`feedback_cross_agent_baton.md` 落地、**順序倒過來**：markdown 留存層 primary、口頭 secondary。穩定性靠 markdown、速度靠口頭。

```
Stage 1: 隱含 (5/06-5/10)
   ↓
Stage 2: 命名 + 口頭主導 (5/11)
   ↓
Stage 3: 跨組合驗證 (5/13)
   ↓
Stage 4: Payload 形式對比 (5/13)
   ↓
Stage 5: Markdown 主導 SOP (5/14)
```

**5 個 stage、9 天內走完**。

---

## 四、外部架構研究與吸收策略

5 個外部研究、各自產出不同類別的學習：

| 研究 | 日期 | 主要學習 | 採納 |
|---|---|---|---|
| **cc-switch** | 5/12 | 「Guardrail 該被產品化」設計衝動 | 不採納 patterns（場景不對）、採納 design 衝動 |
| **Hermes Agent** | 5/13 | 我們 indexed memory + scope 分割比社群方案領先；缺 plugin abstraction + agent-callable tools | 採納 includes directive 概念、不採納 plugin / vector search |
| **PLUR** | 5/13 | 對立哲學 validation（memory 是 bottleneck 不是 model intelligence）；3 條相容概念 | 採納 type 四分法 / mem-used trailer / access count（提案 v1.0、待後續執行）|
| **superpowers** | 5/13 | Skill vs memory 區分；skill = enforced + auto-triggered | 不採納（state-centric vs methodology-centric 場景差）、確認 gap 不是漏洞 |
| **Cowork** | 5/14 | Multi-surface fragmentation 風險 — 對你 SSOT 哲學是負面 | 不採納（架構整體性考量、不只 use case 考量）|

**研究外部的價值矩陣**：

| 結果類型 | 範例 |
|---|---|
| 直接採納 | Hermes Issue #22612 indexed memory 概念 |
| 概念吸收（不採納實作）| PLUR 三條（type / mem-used / access）|
| 觸發內部設計衝動 | cc-switch → 「guardrail 產品化」 |
| 反向驗證自己（這條最隱形但最重要）| superpowers 確認 skill gap 不是漏洞；Cowork 確認 surface 收斂是合理選擇 |
| 純 mapping、無採納 | Cowork 與你 use case 對位差太大 |

「**研究外部前先判斷你會用哪一類**」是後續可以記成方法論的元層級觀察。

---

## 五、累積的方法論清單

9 天內提取出來的可重用 pattern（已寫成 feedback / reference / awareness 段）：

| 方法論 | 來源 | 寫進哪 |
|---|---|---|
| Meta-memory（memory 自己的規則也是 memory）| 5/07 | `reference_claude_memory_repo.md` |
| Architecture change checklist | 5/11（事後補）| `reference_codex_memory_strategy.md` |
| `shared/` ≠ 對等 context | 5/11 | 同上 |
| Inline boundedness 兩層 pattern | 5/12 | `feedback_inline_size_limits.md` |
| Validation through use（非 inspection）| 5/12 | 概念隱含、未成檔 |
| Cross-shell parity 從 defaults 起手 | 5/14 | `scripts/memory_health.common.env` + 5/14 工作日誌 |
| 「Selective」需要 declaration + exclusion | 5/13 | Codex `codex_load: include_only` 設計上 |
| Pilot → reliability baseline → expansion | 5/13 | 概念隱含、未成檔 |
| Health check warning 預設驗證、不降標準 | 5/13 | 隱含 |
| 局部、可證明無副作用的 fix（最小爆炸半徑）| 5/13 | 隱含 |
| Markdown-as-baton vs verbal-as-baton trade-off | 5/13-14 | `feedback_cross_agent_baton.md` 內 |
| Baton 雙層規則（markdown primary、口頭 secondary）| 5/14 | 同上 |
| 26 KiB / dependency repetition 為 selective load 觸發 | 5/14 | Strategy 檔 + Notion 日誌 |

**幾條尚未成檔但值得獨立寫的**（順手記）：
- Validation through use 跨 domain 適用
- Pilot → baseline → expansion 跨 domain 適用
- 「研究外部前先分類預期採納類型」（元層級）

---

## 六、目前狀態與 open threads

### 四端狀態（2026/05/14 收尾）

| 端 | Memory infra | Health | Latest AGENTS bytes |
|---|---|---|---|
| 公司 Claude Code | ✅ 完整 | ✅ clean | N/A（不走 AGENTS）|
| 公司 Codex | ✅ 完整 + includes Path A pilot | ✅ clean | 24406 / 32768（74.5%）|
| 家裡 Claude Code | ✅ 完整 + Path A 驗證過 | ✅ clean | N/A |
| 家裡 Codex | ✅ 完整 + reliability parity | ✅ clean（5/13）| 21181 |

### Open threads（未閉環的事項）

1. **家裡端 Codex 5/14 改動後重驗** — `memory_health.common.env` 在家裡端 runtime 是否正確讀取、AGENTS 編譯是否一致、家裡端 sync-codex.sh 對 baton SOP 是否正確 propagate
2. **AGENTS bytes 趨勢監控** — 9 天從 ~13.6 KiB → 24.4 KiB、若按目前增速 3-5 天會逼近 26 KiB 觸發 selective load 擴張決策
3. **PLUR 概念吸收提案** — 已寫提案 v1.0（type 四分 / mem-used / access count），等 Path A pilot 全面 rollout 後再開工
4. **方法論未成檔項** — Validation through use、Pilot → baseline → expansion、研究外部分類 — 都還是隱含、未獨立成 feedback 檔
5. **Skill layer 評估** — 確認 gap 不是漏洞、但若未來 SOP 違規率上升、要重新評估 hybrid（hot path skill 化 + 其餘留 memory）

---

## 七、設計哲學

整個架構走下來、underlying principles 可以總結為 7 條：

1. **Explicit authoring over auto-emerge** — Memory 由人 curate，不由 LLM 自動 derive。對應 Ivan 31 年手寫日記哲學
2. **Git as single source of truth** — 所有 memory 變動可 diff / rollback / `git log`。不依賴 cloud-backed memory provider
3. **Local-first** — Memory 在本機檔系統、不依賴外部 API endpoint。Self-hosted RustDesk 同理
4. **Platform-agnostic data portability** — 用 markdown、不用 vendor-specific format。Anthropic 哪天倒了、memory 仍可讀
5. **Filesystem as unification layer** — Claude Code / Codex 都認 filesystem、所以可被 git 串起來。Cowork 不認 filesystem、所以不導入
6. **Methodology written into memory itself** — 規則寫進 memory 自己（feedback_*.md），下次 session auto-load 就懂、不靠人記
7. **Minimum blast radius for changes** — `_v2` 不覆寫、局部修不全域改、`memory_health.common.env` 只抽 defaults 不抽 logic

**這 7 條跟 Anthropic 自家產品演化方向部份對立**：
- Anthropic 推 Cowork / Cross-surface Dispatch → 多 surface
- Ivan 推 filesystem-unified 4 端 → 收斂 surface
- Anthropic 推 server-side memory derive → auto-emerge
- Ivan 推 explicit markdown authoring → manual curation

對立不是 bug、是設計權衡。Ivan 的路徑 trade off 了「自動化便利」、換來「31 年可追溯 + 完整 control + platform 中立」。

---

## 八、未來方向（open、未承諾）

按優先序：

| 方向 | 觸發條件 | 預期投入 |
|---|---|---|
| AGENTS 26 KiB selective load 擴張 | bytes 逼近 26 KiB / 重複 dependency 出現 | 3-5 hr |
| PLUR 概念吸收提案執行（type 四分先做）| Path A pilot 全面 rollout 穩定後 | 10-13 hr（三條全做）|
| 方法論成檔（validation through use 等）| 自然觸發、不主動排期 | 各 ~30 min |
| Hybrid skill layer 評估 | SOP 違反率上升、出現具體 enforcement gap | 未估 |
| Cowork / 多 surface 評估 | Anthropic 推出 unified memory layer | 未估、被動觀望 |

**故意不做的事**：

- 不導入 PLUR 工具本身（哲學對立）
- 不導入 cc-switch（場景不對）
- 不導入 Cowork（破壞 SSOT）
- 不全面 skill 化（use case 不需要）
- 不引入 vector / semantic search（規模未到）
- 不引入 cloud-backed memory provider（隱私 + 控制權）

---

## 九、結論

9 天從零到生產級。每天一個 architectural step、沒有空轉、沒有 cleanup-only 的日子。

最值得記住的三條觀察：

**1. Compound effect 真實存在**
5/06 沒有 memory infra 概念、5/14 已經有正式 baton SOP + cross-shell parity + inline boundedness pattern 在生產應用。**每天一個 step、9 步成林**。如果中間某天 skip、後面整個鏈條會斷。

**2. 研究外部 + 設計內部 + 落地實作 + 提取方法論**
這條 loop 是這幾天唯一的工作流。每外部研究都產出 internal 設計、每設計都進落地、每落地都產出方法論、方法論寫進 memory 自己。**這條 loop 自我增強**。

**3. Memory infra 是 surface 收斂的對應物**
Cowork 多 surface vs Ivan filesystem-unified — 兩條路都有 logic、但選了後者後、整個 memory infra 才能 work。**SSOT 跟 surface 收斂是同一個哲學的兩面**。

---

## 附錄：commit / Notion 日誌索引

按日期排序、可作為 traceability 入口（commit hash 部份只列已記錄到的）：

| 日期 | Notion 工作日誌 | Key commits |
|---|---|---|
| 5/06 | 3 篇（AHK / family-assets / family-allowance）| — |
| 5/07 | 跨機器 Memory 同步架構 | — |
| 5/08 | 跨機 memory 接通 + Codex 整合 + Notion 驗證（4 篇）| — |
| 5/09 | 付款方式 + Codex SOP 對稱化 + 跨對話視窗 SOP | — |
| 5/10 | family-allowance 22 commits + SOP 三度驗證 + firm rule 8/9 | — |
| 5/11 | Codex 2.1 SOP 對齊 + Cross-agent baton 閉環 + AlphaModel3 | — |
| 5/12 | Memory infra 從紀律到自動化 + cc-switch 研究 + backlog 7→0 | `9b0775a`（P0）、`aebdb36`（inline 邊界 propagate）、`73d9fa1`（backlog 紀律）|
| 5/13 | Hermes 對照 + Codex Proposal 2/3 + Path A pilot + home reliability + PLUR + superpowers | `4836d38`（home health）、`0be511d`（cross-scope 清理）、`b9d9e80`（locale）、`a914da1` |
| 5/14 | 記憶管理收斂：home reliability 接續 + cross-agent baton SOP 正式化 | （新 SOP + common.env、commit hash 見 Notion）|

---

## 附錄：本文件版本與用途

| 欄位 | 值 |
|---|---|
| 版本 | v1.0 |
| 用途 | 歷史紀錄 / 新 agent onboarding context / 跨日回顧 |
| 預期生命週期 | 半年內為 reference，半年後可成 archive |
| 建議存放位置 | `claude-memory/shared/reference_memory_evolution_2026_05.md`（codex_tier: summary、agents: [claude, codex]）|
| 更新觸發 | 下一個 architectural milestone（例如：PLUR 提案執行完、selective load 大規模 rollout、AGENTS 突破 26 KiB 後決策）|
