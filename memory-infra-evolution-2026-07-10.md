# 跨 AI Agent、跨機器長期記憶管理：演化進程 III — 內容知識論 — 2026/07/10

> 承接[演化進程 II（2026-05-15 ～ 2026-07-02、治理與擴充性）](memory-infra-evolution-2026-07.md)。
> 本篇整理 **2026-07-10 一天內**完成的一輪完整演化：內部體檢 → 同日修復 → 外部生態對標 → 概念借鏡 → 工作包施工 → 跨端驗收。
> 一句話定位：**07/02 解決「架構會不會壞、會不會不同步」；07/10 解決「架構雖然沒壞，但內容會不會慢慢失真、重複、過期、找不到、超載」——從基礎設施衛生，走進內容知識論（temporal truth・provenance・semantic drift・backlog convergence）。**

- 快照數字為 2026-07-10 定格；之後變動不回寫本文，以 health 輸出為準。
- 本文是長背景／演化脈絡／對外說明書，**不是 source of truth**——即時狀態以 `CURRENT_WORK` / `project_status` / repo health 為準。

---

## 0. 一天的數字

| 指標 | 值 |
|---|---|
| 內查 agent（體檢） | 18（5 路掃描 → 去重 → 對抗式驗證） |
| 外比 agent（生態調研） | 12（4 面向 → 8 條逐頁查核） |
| 體檢發現 | 12 confirmed／**1 refuted**／0 uncertain |
| 生態主張 | 75 條、全部附可點開 URL、8 條對抗式查核（5 條被修正） |
| 工作包 | 8 項、**完工定義＝檢查點過**、驗收 10/10 |
| 排程 → 跨端施工 → 驗收完成 | **約 2 小時**（原估 1 工作天） |
| 熱層 MEMORY.md | 25,187B（距 cap 413B）→ **23,490B** |
| lifecycle 覆蓋 | 9 → **17 張狀態卡**（假綠燈消除） |
| proposals backlog | 14 → **6**（回綠） |

---

## 1. 關鍵術語（本篇新增）

- **內容知識論（content epistemics）**：不只問「記憶存好了沒、同步了沒」，而是問「這條記憶**現在還是真的嗎、誰寫的、什麼時候被推翻的**」。07/10 的主軸。
- **黏行（fused line）**：索引檔缺換行導致兩條 bullet 熔成一行——第二條從獨立條目降格成前一條的句尾純文字，agent 掃索引時直接漏看。機械性、可 lint。
- **假綠燈（false green）**：健檢回報 clean、但掃描範圍只覆蓋部分地盤（lifecycle 只掃 shared/ 9 卡、office/ 8 卡零覆蓋）。比紅燈更危險。
- **superseded 慣例**：事實被推翻時，舊值**不刪除**、標 `superseded: YYYY-MM-DD → <接替處>` 保留——事實的變動史成為一級公民（借鏡 Graphiti bi-temporal）。
- **provenance 欄位**：frontmatter 選填 `origin_agent:` / `superseded_by:`——記憶有署名、可追寫入者（借鏡 MemClaw 四維治理）。
- **機械漂移 vs 語意漂移**：前者（黏行／斷鏈／超標／孤兒／未登記）lint 可零成本抓；後者（兩檔對同一事實講矛盾的話、「已 live」其實早過期）**仍靠人工策展＋季度 fan-out 體檢**。這條邊界是本篇最重要的誠實聲明。

---

## 2. 背景與觸發

07/02 三刀之後的 baseline：四端同步、health 檢查、backup/prune、orphan 偵測能運作——「系統能不能同步」已解。7/7 憲章（`reference_ai_workflow_harness.md`）定稿：11 條 Non-Goals ＋ 8 條 Decision Gates。

**07/10 晨的觸發**：sync 健檢 WARN——編譯後 MEMORY.md **25,187 bytes**，超過 24,576 警戒線、距 25,600 native cap 只剩 **413 bytes**（越線＝尾端條目開場靜默漏載）。同日 Ivan 下令「體檢目前長期記憶架構」，隨後追加「看 GitHub 熱門記憶架構有沒有可學的」——內查＋外比在同一天並行。

---

## 3. 內查：18-agent 體檢

方法沿 7/2 範本：**先親自釘死一手量測**（8 條 gate 的確定性數字）→ 5 路 fan-out 掃描（索引完整性／Non-Goal 違反／冷熱錯置／stale 事實抽驗／lifecycle 漂移）→ 高中嚴重度發現逐條**對抗式驗證**。

### 一手量測（fan-out 前就釘死的）

- Gate 5 🔴 FIRING：25,187B（僅剩 413B 頭寸）；79/200 行——**bytes 是 binding constraint、行數綠**（憲章 V「綁定約束會遷移」的再驗證）
- Gate 2 🟡：CURRENT_WORK.codex.md 6,300B > 6,144（75% 早期線）——且發現 **75% 線只存在於憲章文字、腳本只查 8,192 硬上限**（人工手算才抓到）
- 兩個 clone 之謎：`~/HomeProjects/claude-memory` 是 symlink → 無 split-brain ✅
- log.md 歸檔登記 33/33 齊全，但 **9 條用 Windows 反斜線**（公司端 roll_log.py 寫入的跨平台污染；經查對 grep 搜尋鏈零實質影響）

### 發現（12 confirmed、每條有獨立 verifier 讀檔／跑指令）

| 類別 | 發現 | 嚴重度 |
|---|---|---|
| bug | MEMORY.shared.md L48 黏行（兩條 feedback 熔成一行）＋ detail index L21 同款——**同一週（7/2-7/3）犯兩次** | HIGH＋LOW |
| stale | 「開工 hook 家裡待自接」——實際 6/25 當天就接好了，索引行躺了 **15 天**沒更新 | HIGH |
| 假綠燈 | lifecycle_health 只掃 shared/，office/ 8 卡（含最活躍的 TRM）零覆蓋；回報「9 cards clean」 | HIGH |
| Non-Goal 5 違反 | CURRENT_WORK 3/13 條目 mini-status-report 化（TRM 塞實測發現敘事、健檢日報塞已結案歷史事件） | MEDIUM×3 |
| gate 缺口 | Gate 2 早期警戒線無自動化 | MEDIUM |
| backlog | proposals 14 檔 vs 閾值 6 常駐紅；spec-kit Trigger A 觸發 **56 天**沒人理 | MEDIUM |
| 重複 | offload 鐵律在兩檔重寫兩遍（~2.4KB 雙源、必然 drift） | MEDIUM |
| bug | roll_log.py 缺 `.as_posix()`（反斜線根因） | LOW |

**1 條被推翻**：「handoff M1/M2 方法論從未升格」——verifier 實查發現早已升格，指控不成立。驗證機制在殺東西，不是橡皮圖章。

### 健康面（體檢也要報綠的）

73 條熱層索引 link ＋ 38 條 detail index ＋ 259 次 wiki-link 全部 **0 斷鏈**；Non-Goals **9/11 PASS**；office 索引完全乾淨；scope 紀律有持續執行的證據（6/24 搬遷註記還在）。

---

## 4. 同日修復（commit `6e4d2f6`）

9 項一次落地：黏行×2 修復、stale hook 行更正、**降級 4 條低頻索引到 lazy detail index**（Gate 5 → 23,490B、頭寸 2,110B）、CURRENT_WORK TRM／健檢日報壓回三件套（Non-Goal 5 矯正）、codex TRM 同步（Gate 2 → 6,089B）、roll_log.py `.as_posix()`、log header 反斜線 ×9 正規化。

**跨端併發實戰插曲**（教學價值高）：修復 commit 的 rebase 撞上公司端同時 push 的 TRM 更新 → 衝突解法＝**取對方最新事實 × 套本端三件套格式**；途中還遭遇殭屍 rebase-merge 目錄導致 detached HEAD、push 假陽性驗證兩次——最終以「驗父鏈（`merge-base --is-ancestor`）→ `checkout -B main` → push → 驗 HEAD 前進且等於 remote」收乾淨。教訓入袋：**push 驗證必須同時驗「相等」與「前進」**，單驗相等會被 detached HEAD 騙。

---

## 5. 外比：GitHub 生態對標（12 agent、75 claims、逐頁開原文）

四面向：主流三巨頭（mem0／Letta／Zep-Graphiti）深讀、檔案派同門（Claude Code 官方 auto-memory／Wuphf／MemSearch／Obsidian 系）、2026 H1 新秀與 benchmark（MemOS／Cognee／TencentDB／A-MEM）、多 agent 治理（MemClaw／OWASP／學術）。每條主張附 URL＋原文引句；8 條關鍵主張對抗式查核、5 條被修正（含抓到一個 README 落後實際版本、一個舊架構被當現況的印象流）。

### 三個定心丸

1. **官方追認**：Claude Code auto-memory 正式版收斂到與本架構相同形狀（MEMORY.md 索引＋25KB/200 行 cap＋主題檔 lazy load）——且官方 cap 是**死線截斷不挑內容**，人工策展比官方原生機制聰明；官方明文「不跨機器同步」＝四端 sync 這層永遠得自建。
2. **grep 有實證**：Letta 純檔案＋grep 在 LongMemEval 拿 74%、打敗多個專用記憶系統；benchmark 生態正在反噬（LOCOMO 被獨立稽核抓出 6.4% 金標錯誤、Zep/Mem0 互測數字幾週內 84%→58% 反覆改）。**Non-Goal 2（拒絕 vector search）是有實證的保守，不是偷懶。**
3. **治理是獨門**：多 agent 記憶治理 2026 上半年才從論文走到早期程式碼（MemClaw 286★、OWASP Agent Memory Guard 69★）；OWASP 把 Memory Poisoning 列 **ASI06 一級風險**；「憲章式 Non-Goals＋人工策展為主」在學界幾乎沒人研究——**是刻意取捨、走在前緣，不是落後**。

### 生態趨勢（記錄供後續校準）

- mem0 2026-04 捨棄兩階段 ADD/UPDATE/DELETE、改 **ADD-only**（「寫入時 reconciliation 會摧毀 context」）——與本架構「legacy quirk 不順手修」同向的外部驗證。
- **bi-temporal 成為「事實會過期」的業界標準答案**（Zep 甚至把 temporal knowledge graph 做成獨立概念在推廣）。
- **sleep-time compute／Dreaming**（背景 agent 自主改寫記憶）成為多家共同賣點——mem0、Letta、OpenAI、華為全在推。**這正是本架構 Decision Gate 要擋的模式**：持續警戒它滲透工具鏈、當反面教材不跟進。
- 大廠入場（騰訊 8k★／華為／Elastic），三巨頭記憶分層獨立收斂到「小容量即時層＋按需層＋全量歷史層」＝本架構的熱／溫／冷同構。

### 三借鏡（概念層、全部合憲、照 PLUR 先例「借概念不裝工具」）

| 借什麼 | 從誰 | 落地形式 |
|---|---|---|
| 不刪除、只標失效 | Graphiti bi-temporal | `superseded: 日期 → 接替處` 慣例入 memory SOP——直接對治「觀測起點偏差」（第一次被看見≠第一次發生），並防**殭屍事實**（帶舊 context 的 agent 把新值「更正」回舊值） |
| provenance＋time 缺失維度 | MemClaw scope/time/provenance/propagation 四維 | frontmatter 選填 `origin_agent:`／`superseded_by:`——**spoke 回流時代（本地 LLM 提案寫回）的前置地基**，明標「保險性投資、B 期前無法驗收益」 |
| /lint 檢查清單 | Wuphf（承 Karpathy llm-wiki） | 黏行／孤兒引用／斷鏈／未登記歸檔的 grep-based 檢查折進 memory_health——百萬 token 體檢裡機械類那半，變成每次收工零成本掃 |

另存參不急用：TencentDB「上層結論可 drill-down 回原始逐字證據」當月報 consolidation 驗收標準；Letta 併發踩坑佐證「spoke 只准 append、覆寫權收斂單一 owner」；OWASP 四態模型（allow/redact/quarantine/block）留給 B 期外部入口開放前。

### 明確不借

sleep-time compute／Dreaming 自動改寫（撞人工策展鐵則）；vector-first retrieval（trigger 未觸發＋grep 74% 實證）；一切整套第三方 harness／雲端 memory provider／graph DB 常駐服務。

---

## 6. 工作包 B→A→C：完工＝檢查點過

體檢五待辦＋三借鏡收斂成 8 項工作包，寫進 `project_status_notion_workflow.md`，**每項附 falsifiable 檢查點**——完工定義不是「程式碼寫完」而是「檢查點過」：

- **B 批（事實時間軸、執行序第一）**：B1 superseded 慣例入 SOP；B2 origin_agent/superseded_by 慣例。**執行序 B 先於 A 的理由**：B2 檢查點要求「本工作包新/改檔全帶 origin_agent」——慣例得先定、A/C 批才守得到。
- **A 批（健康可信度）**：A1 黏行偵測（檢查點＝回歸測試：對歷史壞 commit 必須抓到、當前 0 誤報）；A2 Gate 2 早警 6,144B（檢查點＝對 6,300B 歷史態重放必觸發）；A3 lifecycle 擴 office/（檢查點＝17 cards scanned）；A4 lint 三規則。
- **C 批（衛生）**：C1 handoff 三教訓升格＋歸檔；C2 proposals 封存＋Trigger A 重評；C3 offload 鐵律單一權威本。
- owner 分工：B＋A＝Codex（sync/health 腳本最熟）、A 批 `.ps1` 驗收＝公司 Claude、C1/C3＝家裡 Claude、C2＝任一端。

## 7. 跨端執行實錄：baton 完整一圈、零口頭協調

- **~10:50** 家裡 Claude 排工作包 → push（`d78c2ee`）
- **午後** 公司 Codex 開工讀 CURRENT_WORK → 接棒 → 依 B→A→C 全部施工（`4f3dbf9`／`3c58a26`）——**包括原分給家裡端的 C1/C3**（owner 是建議非強制、baton 容許）
- Codex 收工報告**誠實聲明缺口**：「PowerShell 實測 clean、**Bash 只完成語法驗證**（runtime 受本機 Scoop Git Bash 卡住）」
- **~16:00** 家裡 Claude 跨端補驗：`.sh` Mac runtime clean ＋ 檢查點逐項驗收 **10/10**——A1 回歸（歷史版抓 1／當前 0）、A3 實跑 17 cards、C2 回綠 14→6、C3 grep 單一權威本、C1 三教訓逐字升格、**B2 慣例第一天就被實際使用**（Codex 自己的新檔 frontmatter 已帶 `origin_agent: codex`）
- 收檔（`a0c0fb0`）：工作包段壓成完工紀錄、CURRENT_WORK 回 observe

原估 1 工作天 → 排程到雙端驗收完成**約 2 小時**。全程無任何口頭協調——工作包段落自帶執行序理由、檢查點定義、owner 建議，接棒端讀完即可施工。

### 自我驗證時刻

施工途中 Codex 把自己的 dashboard 推到 **6,153B——被它自己剛蓋好的 6,144B 早期警戒當場抓回**、立即壓回線下。健檢演進鏈「人記得跑→系統喊→喊了有人修→**修完變 gate**」在同一個 session 內閉環：蓋 gate 的那隻手產生的 drift，被 gate 當場接住。

---

## 8. 07/02 vs 07/10 對照

| 面向 | 07/02 三刀 | 07/10 B→A→C |
|---|---|---|
| 核心目標 | 讓四端同步、健檢、backup/prune、orphan 偵測能運作 | 讓記憶**內容本身**能辨識漂移、過期與重複 |
| Health | byte／frontmatter／orphan／conflict／sync | ＋黏行、6,144B 早警、office lifecycle、archived 引用、detail index 斷鏈、log archive 登記 |
| 事實管理 | 檔案與同步層治理 | ＋superseded／origin_agent／superseded_by——開始處理「這個事實何時失效、誰改的」 |
| Baton | 讓三端知道接棒任務 | baton 自己也能被 health 檢查（archived 後 dashboard 舊路徑會被抓出並修正） |
| Proposal 池 | 建立 proposal_health、發現超標 | 實際封存 8 份、14→6、重評 56 天 Trigger |
| 驗證方式 | 驗「系統能不能同步」 | 驗「系統會不會抓到新產生的 drift」——甚至抓到本輪自己推出的 6,153B |

**知識來源也不同**：07/02 的三刀是內部迭代；07/10 的三借鏡來自 75 條 URL 驗證的外部生態調研——harness 首次完整展示「**對外掃描 → 逐頁驗證 → 合憲吸收 → 當天落地**」的代謝循環，全程未引入資料庫、RAG、常駐服務或新記憶引擎。

---

## 9. 誠實邊界（本篇最重要的一節）

1. **lint 只治機械漂移**。語意漂移（矛盾陳述、過期的「已 live」）今天是靠百萬 token 的 fan-out 體檢抓出來的——lint 抓不到。分工：機械＝每次收工零成本掃；語意＝人工策展＋季審 fan-out。**「health 全綠」不可讀成「內容全真」。**
2. **provenance 是保險性投資**：收益在 spoke 回流時代（本地 LLM 提案寫回）才能驗證，B 期前無法驗收——明標、不假裝已證明。
3. **效益主張≠已驗證事實**：工作包八項的檢查點全過＝「該修的修了、規則抓得到歷史事故」；「修完會多好」中只有可重放的部分（回歸、覆蓋率）當天驗證，superseded 慣例掛 observe 等下一次真實事實更正當首例。
4. 快照數字（23,490B／17 cards／14→6）為 2026-07-10 定格。

## 10. 設計哲學：前篇 11 條全數存活，新增 3 條

1. **完工＝檢查點過，不是報告寫完**——工作包每項自帶 falsifiable 檢查點，跨端接棒者可獨立驗收，報告與驗收分離（本輪 Codex 施工＋家裡 Claude 驗收即實例）。
2. **借概念、不裝工具**——外部生態是概念礦場不是軟體貨架；每個借鏡標注「與哪條 Non-Goal 衝突（若整套採用）」，衝突的部分留在門外。
3. **內容知識論**——記憶不只要存在與同步，要有時間（何時為真、何時失效）、有署名（誰寫的）、有絆線（發現過的失敗模式永久可偵測）。

## 11. Open threads（2026-07-10 收尾時點）

- superseded 慣例首例驗證：等下一次真實事實更正（頻率約每週）
- 語意漂移季審：下次全量 fan-out 體檢（約 2026-10）
- spoke 治理（`jarvis_tier` 策展下發）：刻意等 Mac Studio 到位、本地 LLM 家庭助理上線才開——Non-Goal 8 邊界已畫好
- Gate 6：log.md 125K 接近 roll 線（收工例行處理）
- Cowork 在收工 checklist 的立場不一致（watch 項）

## 12. 結論

07/02 之後，這套系統知道自己**有沒有壞**；07/10 之後，它開始知道自己**有沒有在慢慢變得不真**。一天之內：內查 18 agent、外比 12 agent、修復 9 項、工作包 8 項跨端接力完工、驗收 10/10——而最能說明這套 harness 成熟度的，不是任何單項數字，是兩個瞬間：**驗證機制推翻了自己陣營的一條指控**，以及**新蓋的警戒線當場抓住了蓋它的那隻手**。

原則未變：沒有資料庫、沒有 RAG、沒有常駐服務、沒有新記憶引擎——只有 Git ＋ Markdown ＋ health ＋ baton，被做得更會自我維持。

---

*成文：2026-07-10 家裡 Claude；資料來源：當日對話實錄、claude-memory commits（`6e4d2f6`…`a0c0fb0`）、體檢/調研 workflow 原始輸出。*
