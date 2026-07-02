# 跨 AI Agent、跨機器長期記憶管理：架構演化進程 II — 治理與擴充性

**期間**：2026/05/15 — 2026/07/02（約 7 週；承接 v1.0 的 2026/05/06-05/14）
**範圍**：4 端（公司 Windows × Claude Code/Codex、家裡 Mac × Claude Code/Codex）+ Notion 工作日誌
**作者**：Ivan + 公司 Claude Code 整理
**日期**：2026/07/02
**前篇**：`memory-infra-evolution-2026-05.md`（v1.0、Day 0-8 從零到生產級）

---

## 整體軸

v1 的 9 天是「**從零建立**」：repo、四端接入、tier 編譯、baton SOP、health 哨兵雛形。

這 7 週是「**治理與擴充性**」：系統從「能用」走到「會自己喊、會自己修、撞牆前先警告」。主軸只有一條——

> **綁定約束（binding constraint）發生了遷移，而整個架構圍繞新約束重組。**

v1 收尾時盯的天花板是 Codex AGENTS.md 的 32 KiB。6/23 的調查發現真正先撞的其實是 **Claude Code native loader 的 25,600 bytes 硬上限**（「前 200 行或前 25KB、誰先到算誰，超出尾端靜默不載」；中文每字 3 bytes → byte 遠比行數先爆）。此後所有大動作——profile split、byte gate、tripwire、demote、lazy detail index、7/2 全面體檢——都是對這條新約束的回應。

```
05/16  ●  孤兒索引事故 → 手動 audit SOP（7/2 自動化 orphan 檢查的前身）
05/31  ○  跨端 merge 衝突標記殘留（潛伏）
06/16  ●  衝突標記被揪出（兩週後）→ conflict-marker 掃描進 health
06/17  ●  git_sync_health 誕生（dirty / ahead-behind / 索引斷鏈 三檢）
06/22  ●  fan-out 深審：索引行數監控 +「勿拆 topic 檔」裁定
06/23  ●  ★ tiering survey：發現真正綁定約束＝native 25.6KB、byte 先於行數爆
06/24  ●  profile split：25 條單端條目連檔搬 office/home
06/25  ●  開工/收工 SOP 改 hook 強制注入（從 model attention 到 harness enforce）
06/26  ●  propagation-drift 收斂：13 條斷鏈修復 + fail-closed 硬 gate + common.env 同源
06/27  ●  ★ 16-agent 架構審：office 全載已破 25.6KB（靜默漏載中）→ P0/P1/P2 修整、lazy detail index 誕生
07/02  ●  ★ 38-agent 全面體檢 + 三刀落地 + 三端 baton（本篇觸發點）
```

關鍵特徵延續 v1：每個階段都產出可重用方法論、方法論寫回 memory 自己、每件事經得起 commit + Notion 日誌追溯。新增特徵：**「偵測 → 修復」開始閉環**——健檢不再只是喊，喊了有人修、修完寫成新的自動檢查。

---

## 一、時間軸（里程碑制）

7 週不逐日記，按 10 個 architectural milestone：

### M1（05/16）— 孤兒索引事故：手動 audit SOP 誕生

`home/project_receipt_scanner.md` commit + push + sync 全做了，**卻忘了在 `MEMORY.home.md` 編索引**——檔案在、索引沒有，新對話 auto-load 看不到，等於不存在。補 commit 修好後，寫下 `feedback_memory_index_curation.md`：附一段 `comm -23` 的 orphan audit 指令，「定期跑、抓出寫了檔但沒索引的」。

**這是需要人記得跑的 on-demand 指令。** 它的自動化版本要到 7/2 才落地（orphan 偵測進 memory_health 雙側）——而那時這份手動 SOP 檔早已在某次「合併 memory 維護 SOP」時被併進 `feedback_memory_edit_target.md`。7/2 體檢當天在一個落後 44 天的 memory 目錄裡挖到它的殘影，恰好見證了「手動 SOP → 自動 gate」的完整生命週期。

### M2（05/31 → 06/16）— 衝突標記潛伏兩週：conflict-marker 掃描進 health

5/31 一次跨端 merge 漏清的 `>>>>>>>` 躺在 `shared/log.md` **兩週**才被 `git grep` 揪出——`git diff --check` 只查未 commit 的 diff、抓不到「已 commit 進去」的孤兒標記。修法：memory_health.ps1 加行首 `<<<<<<<` / `>>>>>>>` 掃描（不掃 `=======` 以免撞 setext 標題底線）。

誠實註記：這條檢查當時只進了 `.ps1`；**常做跨端 merge 的 home 端（`.sh`）反而沒有**，這個不對稱要到 7/2 才補齊。

### M3（06/17）— git_sync_health：跨對話兜底「半成品遺失」

cross-check handoff 升格出三檢：① working tree dirty（上次 Edit 沒 commit）② 本機 vs origin ahead/behind（**fetch 後比 origin、絕不用「本機 HEAD 沒前進」反推對方沒 push**——這半句是同期一次誤判的直接教訓）③ MEMORY 索引指向的檔是否存在。定位是「唯一能跨對話兜底半成品遺失的機制」，設計為唯讀、掛在 sync 之後。

### M4（06/22）— fan-out 深審：「勿拆 topic 檔」裁定

多 agent 深審抓出一個反直覺結論：`MEMORY.shared.md` 每次開對話**全載**，拆成 `MEMORY.shared.<topic>.md` 在全載模式下不省任何 context、還會因 sync 明文 skip `MEMORY.*.md` 而讓拆出的條目**靜默漏載**。裁定寫進索引檔頭 inline 邊界：不拆，逼近門檻時先合併/降級。

### M5（06/23）— ★ 綁定約束遷移：native 25.6KB、byte 先於行數

tiering survey 驗證了 Claude Code 官方文件的 native loader 行為：`MEMORY.md`「前 200 行或前 25KB 誰先到算誰」載入，超出**靜默不載**。配上「中文每字 3 bytes」這個事實，結論是：

- 行數維度永遠不 binding（實測 81 行 vs 上限 200、只用 40%）
- **byte 維度早就在燒**（當時已 90%+）
- 原本只量行數的守門**形同空轉**——量錯維度的監控等於沒有監控

約束從「Codex AGENTS 32KB」正式遷移到「Claude native 25.6KB」。Codex 端因為有 codex_tier 編譯反而寬裕（72%）；Claude 端攤平全載、成為結構性弱側。

### M6（06/24）— profile split：25 條單端條目連檔搬家

順著新約束的第一刀：shared 索引是**兩個 profile 共同吃**的天花板大宗，於是把 25 條「其實只有單端需要」的條目連檔搬進 `office/` / `home/` scope，shared 只留真正跨端共用的。同時確立判準寫進索引檔頭：**新增條目先問「另一端開場需不需要」，再決定進哪個 scope。**

### M7（06/25）— SOP 從紀律變 enforcement：hook 強制注入

公司端漏跑一次晨間 SOP 後，觸發語（開工/收工類）改由 UserPromptSubmit hook 自動注入 SOP 清單（跨平台 `morning_sop_trigger.py`、公司+家裡 Claude 共用）——**不再依賴 model attention**。這是 v1「從紀律到自動化」哲學在 SOP 層的延伸：紀律寫成文件會被忘，寫成 harness 就不會。

### M8（06/26）— propagation-drift 收斂：fail-closed 成為預設

公司 Codex 審出兩個月累積的架構債，Claude CLI 接力修：

- 修 ~13 條 profile split 後的 `shared/→office` 斷鏈（dashboard 沒跟上搬家）
- **sync-codex 的 stop line 從「只警告仍照寫」改成「超過 28KiB 就 fail-closed 不寫入、保留舊版」**——虛設的線變成真的牆
- 閾值全數收進 `scripts/memory_health.common.env`：寫入端（sync）與偵測端（health）、PowerShell 與 Bash 四路共用同一份常數，杜絕 fail-open 漂移
- 新增 pointer-integrity 檢查（CURRENT_WORK 引用的路徑必須真實存在）
- cross-scope 檢查的豁免範圍正式裁定：只豁免 CURRENT_WORK 兩份 dashboard 與 log.md（跨 scope routing/history 層），其餘嚴格

### M9（06/27-28）— ★ 16-agent 架構審：牆已經撞上了

家裡 Claude 以 16-agent workflow 審視，抓到最痛的一條：**office 全載 MEMORY.md 已達 26,874B、破 25,600 硬上限**——公司 Claude 每個新對話**正在靜默漏載尾端索引條目**，而且沒有任何告警。修整三層：

- **P0**：demote 12 條 office warm/低頻條目進新生的 `reference_office_detail_index.md`（**lazy detail index 誕生**：開場不載、需要時 Read、grep 照常可及），26,874 → 24,202B
- **P1**：sync-home.sh / sync-office.ps1 寫入前加 byte 硬 gate（fail-closed、common.env 同源）——同樣的事故從「會發生」變「寫不進去」
- **P2**：health 補 shared 索引 byte tripwire（17,800 ＝ 軟線 24,576 − 最大 profile 索引），在撞牆前約 1KB 先亮燈

三層剛好是「修這次、擋下次、預警下下次」。

### M10（07/02）— ★ 38-agent 全面體檢 + 三刀 + 三端 baton（本篇）

公司 Claude 對整套架構做系統性體檢：先由主迴圈親手釘死一手事實（byte、gate 值、health 輸出、目錄狀態），再發 5 維 fan-out（scaling=opus / content・sync-health・codex-meta=sonnet / wiring=fable），**每條 finding 由獨立 agent 對抗式查證**，最後綜整。38 agents、31 條 findings 存活、1 條被反駁剔除、4 條 severity 被驗證員修正（包括抓到一條 x4 的數字灌水、重算為 x3.7）。

當天落地三刀（commit `d5eb7b0` + `09ad87b` + `e8382df`）：

1. **runway 回收（零程式碼）**：demote 13 條低頻/Codex 專屬條目入 shared lazy index + CURRENT_WORK 巨段瘦身（先驗證細節都在 status 卡才刪）。shared 索引 16,802 → 12,790B、compiled 兩 profile **94% → 78%**、runway 1,441B → ~5.5KB（x3.7）
2. **修 CRITICAL**：sync-office 原本寫死單一目錄，導致同機另一專案的 memory **落後 44 天無告警**——改掃全部 memory 目錄（對齊 sync-home），並把 gate 移到寫入任何目錄之前；收工自動跑 memory_health + prune
3. **health 補洞包**：反向 orphan 偵測進雙側（M1 手動 SOP 的自動化終點）、conflict-marker 掃描補進 `.sh`（M2 的不對稱終點）、git_sync_health 驗全三 scope 索引、`prune_backups.{ps1,sh}`（備份 194 份 87.7MB → 滾動留 10 份）

隨後以 handoff 檔派三端接棒任務（含驗收標準與回報欄）。**公司 Codex 在一小時內完成自己那條並回報**——零口頭溝通。

---

## 二、目前最新作法（2026-07-02 快照）

這一章就是「現在的架構長什麼樣」，供任何一端 onboarding。

### 2.1 三層載入模型

```
熱層（開場全載）    compiled MEMORY.md ＝ MEMORY.shared.md ＋ MEMORY.<profile>.md 串接
                    office 20,077B / home 20,147B（各佔 native cap 78%）
                        ↓ 需要時一跳
溫層（lazy index）  3 份 detail index（shared / office / home）
                    archived+warm 狀態卡、歷史/已定案/低頻 reference、Codex 專屬條目
                        ↓ 檔名/關鍵字可達
冷層（全文語料）    全部 ~176 個 .md 照常 sync 進本機 memory dir
                    隨時 Read、隨時 grep；logs/ 歷史切片由 log.md 單一收口
```

治理動作對應：升格（冷→熱）走「寫檔＋同 commit 編索引」；降載（熱→溫）走 demote——把索引行剪進 detail index、檔案本身不動。**demote 是零程式碼的手動 tiering**，7/2 體檢的結論之一：它用一個 commit 抓到自動化 tiering 八成的價值，自動化（claude_tier 軸）掛了明確 trigger（demote 後 shared 再逼近 17,800）才啟動。

### 2.2 Gate 階梯（全部同源自 common.env、預設 fail-closed）

| 防線 | 值 | 行為 |
|---|---|---|
| shared 索引 tripwire | 17,800B | health 亮燈：再加 shared 條目會把最大 profile 推破軟線 |
| compiled 軟線 | 24,576B | sync 印 warn、health 亮燈 |
| compiled 硬線（native cap）| 25,600B | **sync fail-closed 拒寫、保留舊版**；`-Force` 才能 override |
| CURRENT_WORK / codex 版 | 20,480 / 8,192B | health 亮燈（dashboard 膨脹） |
| log.md | 131,072B 或 400 entries | 觸發 roll_log.py 切月份切片 |
| Codex AGENTS | warn 26,624 / stop 28,672 / max 32,768B | stop 線 fail-closed 不寫入 |

原則：**寫入端與偵測端讀同一份常數**——gate 定義只有一份，改一處兩側同步生效。

### 2.3 Health 套件（sync 收工自動全跑）

| 檢查 | 抓什麼 | 何時有的 |
|---|---|---|
| frontmatter / tier | 缺欄位、非法 codex_tier、agents 排除卻 tier≠off | v1（5/12） |
| cross-scope leak | office↔home 互引、shared 寫單端事實 | v1 → 6/26 豁免裁定 |
| pointer integrity | CURRENT_WORK 引用的路徑不存在 | 6/26 |
| byte 全套 | 上表 gate 階梯全部維度 | 6/23-27 |
| 衝突標記 | 已 commit 的孤兒 `<<<<<<<`/`>>>>>>>` | 6/16（.ps1）→ 7/2（.sh 補齊） |
| **反向 orphan** | 建檔沒被任何索引/detail index/dashboard 收錄 | **7/2（雙側）** |
| git sync 衛生 | dirty / ahead-behind / 三 scope 索引斷鏈 | 6/17 → 7/2（+home scope） |
| lifecycle | project_status 30/90 天無 commit | v1（5/12） |
| 備份清理 | memory.bak.* 每目錄滾動留 10 份 | 7/2 |

orphan 檢查的收錄面（collector）＝ 3 份 MEMORY 索引 + 3 份 detail index + 2 份 CURRENT_WORK + daily_workflow hub + log.md——bare filename 出現在任一處即算已收錄。這條補掉的是全系統唯一「發生時零信號」的失效模式。

### 2.4 四端矩陣（2026-07-02）

| 端 | 載入 | 佔用 | 同步 | 備註 |
|---|---|---|---|---|
| 公司 Claude | compiled 20,077B | 78.4% | sync-office **掃全部 memory 目錄** | 健檢+prune 全自動 |
| 家裡 Claude | compiled 20,147B | 78.7% | sync-home 掃全部（多目錄的原創端） | `.sh` 三支實地驗證＝baton 進行中 |
| 公司 Codex | AGENTS 23,743B | 72.5% | sync-codex.ps1 tier 編譯 | VALID_TIERS 缺口已修（7/2 baton、<1hr 完成） |
| 家裡 Codex | AGENTS（同 repo 編譯） | ~72% | sync-codex.sh | baton 待接：同缺口查證 + proposals 池治理 |

### 2.5 Baton 演化：Stage 6-7

v1 記到 Stage 5（markdown 留存層 primary、口頭 secondary）。這 7 週加了兩階：

- **Stage 6（6/25）— harness enforcement**：開工/收工 SOP 由 UserPromptSubmit hook 強制注入，baton 的「接棒儀式」不再依賴 agent 記得。
- **Stage 7（7/2）— 結構化多端派工**：handoff 檔按端分段、每條任務帶驗收標準、檔尾留回報欄；路由接進兩份 CURRENT_WORK（Claude 端）與 AGENTS 編譯（Codex 端 detail tier），四端誰先開對話誰看得到。首次實測：**公司 Codex 一小時內自主完成、驗收（fake tier 探針）、回報**，全程零口頭。

```
Stage 1 隱含 → 2 命名 → 3 跨組合 → 4 payload 對比 → 5 markdown 主導
       → 6 harness 強制注入（6/25） → 7 結構化多端派工（7/2）
```

---

## 三、7/2 體檢方法論（fan-out + 對抗式驗證的完整範本）

這次體檢本身是一個可重用的方法論範本，流程四段：

1. **主迴圈先釘 ground truth**：byte 數、gate 常數、health 一手輸出、目錄狀態——全部親測寫成「已知事實」餵給 agent，讓 fan-out 的角色是「對著事實查證」而非憑記憶臆測（`feedback_ground_truth_before_workflow` 的直接應用）。
2. **5 維 fan-out、模型按難度配**：scaling 給最強模型、機械枚舉（wiring：frontmatter/索引/連結/scope 全量驗證）給輕量模型、其餘中間檔——下游反正有對抗式驗證兜底。
3. **每條 finding 一條獨立驗證 agent，任務是「試著反駁」**：不確定標 PLAUSIBLE、佐證不成立標 REFUTED、severity 灌水打回。實際戰果：一條被剔除、runway 增幅 x4 被重算為 x3.7、兩條 severity 調降、一條「已發生」的措辭被修正為「逼近臨界」。
4. **綜整後同日落地為 code**：體檢報告不是產出物，**修完的系統才是**——三刀＋完整測試矩陣（雙側正負面探針、gate 實測、端到端 sync 兩輪）當天閉環。

一條反向教訓同期成文（6/30、另一專案）：**fan-out ≠ 更好的解**。根因在外部系統、且有廉價手動復原時，多 agent 驗證只會製造進展假象——這條反向護欄與方法論本體同等重要。

---

## 四、體檢揪出並修掉的結構性問題（含誠實面）

| 發現 | 嚴重度 | 處置 |
|---|---|---|
| sync-office 寫死單一目錄、他專案 memory 落後 44 天無告警 | CRITICAL | 7/2 修：掃全部目錄 |
| home profile 距靜默漏載僅 1,441B（約 3-4 條升格、以週計） | HIGH | 7/2 demote 修：runway x3.7 |
| CURRENT_WORK 單一專案段佔 28.8%、dashboard 寫成 history | HIGH | 7/2 瘦身：先驗證再剪 |
| office 端最完整的 health 純手動、Mac 端缺開工三檢 | HIGH | office 側 7/2 掛自動；Mac 側＝baton P4 |
| 「建檔忘編索引」零偵測（唯一零信號失效模式） | MEDIUM | 7/2 orphan 檢查雙側 |
| lifecycle WARN detect-only、可被無限期忽略 | MEDIUM | **未修**：escalation 在 backlog |
| proposals 池 17 檔＝自訂門檻 2.8 倍、無人重評 | MEDIUM | baton 派家裡 Codex |
| **infra 自我維護 ≈ 40% commits、穩態非收斂** | META | **watch**：月檢比例、上升＝過度工程化訊號、凍結架構變更 |

最後一條值得直說：這套系統是「需要持續投餵維護成本」的基礎設施，不是建好就穩的。好消息是 content commits 仍佔六成、infra 是疊加稅不是鯨吞；壞消息是它不會自己變便宜。7/2 這輪是還債（修 CRITICAL＋補洞），之後若比例不降，正確反應是凍結架構、跑穩既有機制，而不是繼續加層。

---

## 五、定位：實務上沒有統一最佳解

Agent 長期記憶至今仍是 open problem。主流路線與代價：

| 路線 | 代表 | 付費點 | 代價 |
|---|---|---|---|
| 自動萃取派 | mem0、Zep/Graphiti、各家內建 memory | 讀取端（自動抽取） | 精度差、存錯存廢話、內容不歸使用者 |
| 向量檢索派 | RAG over notes | 建索引＋檢索 | 幾百檔量級下精度輸給 hand-curated index + grep |
| **策展派（本架構）** | repo-as-truth + 編譯視圖 + 治理 | **寫入端（策展費＝那 40%）** | 精度、跨端一致、可稽核、可攜 |

但不管哪派，最後都收斂到同幾個**不變量**——這正是「長期記憶＝不斷整理、歸納」的工程對應：

1. **分層載入**（熱/溫/冷）——與人腦工作記憶/長期記憶同構
2. **歸納（consolidation）是一等公民**——daily log → monthly review → 升格；demote 是同一件事的反向
3. **遺忘是功能不是 bug**——lifecycle、archive、prune；25.6KB cap 逼系統面對取捨，反而是健康的約束
4. **治理迴路決定壽命**——沒有 health/gate 的記憶系統必然腐化，差別只是三個月還是一年

選哪派由情境決定：2 機 × 2 agent × 金融合規（不上雲）× 跨日續工，幾乎唯一指向策展派。單機單人隨手用，自動萃取派更划算。**沒有統一最佳解，但有「給定約束下的唯一合理解」。**

---

## 六、累積方法論（5/15-7/02 新增、memory-infra 相關）

| 方法論 | 來源 | 成檔 |
|---|---|---|
| 編輯 memory 兩步 SOP（改對 target＋同 commit 編索引） | M1 事故 | `feedback_memory_edit_target.md` |
| 開工/收工 SOP hook 強制注入 | M7 | `feedback_morning_sop_trigger_hook.md` |
| 先釘 ground truth 再發 workflow 查實 | 6/26 | `feedback_ground_truth_before_workflow.md` |
| ultracode fan-out + 對抗式驗證（含反向護欄） | 6 月多案＋6/30 | `feedback_ultracode_workflow_fanout.md` |
| 同機多 agent git index.lock 對撞處理 | 6/25 | `feedback_git_index_lock_cross_agent.md` |
| Observe 期必須寫可觀察 trigger | 6 月 | `feedback_observe_period_triggers.md` |
| Pilot → baseline → expansion（v1 隱含 → 成檔） | — | `feedback_pilot_to_baseline.md` |
| 量錯維度的監控＝沒有監控（byte vs 行數） | M5 | 寫進 health 註解與 survey |
| detect-only 會退化成從不生效 | 7/2 體檢 | 報告 + backlog（escalation） |
| 以 binding profile 盯 runway（不是平均、是最緊的那個） | 7/2 體檢 | 體檢報告 + handoff |
| 手動 demote 先於自動化 tiering（八成價值、零風險） | 7/2 體檢 | CURRENT_WORK trigger 條款 |

---

## 七、設計哲學（v1 七條全數存活＋新增四條）

v1 的七條（explicit authoring / git SSOT / local-first / markdown 可攜 / filesystem 統一層 / 方法論寫進 memory 自己 / 最小爆炸半徑）經 7 週實戰**無一被推翻**。新增：

8. **Fail-closed by default** — gate 寧可擋下同步也不寫出會靜默漏載的檔；讀不到設定就用保守內建值。虛設的警告線一律升級成真的牆。
9. **Detect → remediate 必須閉環** — 只偵測不修復的檢查會退化成背景噪音（lifecycle WARN 連喊 49 天無人動是活教材）；每條新檢查都要想好「喊了之後誰動、怎麼動」。
10. **不做的事要掛可觀察 trigger** — 「暫不做」不是「不做」，是「條件 X 成立時重評」；tier 自動化、skill layer、向量檢索都掛著明確條件。
11. **點名綁定約束、追蹤它的遷移** — 約束會動（32KB → 25.6KB → binding profile 是 home 不是 office）；盯錯約束的優化都是白做。

---

## 八、目前狀態與 open threads（2026-07-02 收尾）

### 數字快照

- repo：~590 commits / 8 週；~176 個 .md（shared 75 / office 40 / home 34 / proposals 17）
- 熱層：compiled office 78.4% / home 78.7%（軟線前餘裕 ~4.4KB、硬線前 ~5.5KB）
- Codex：AGENTS 23,743B / 32,768（72.5%）
- health：全綠（orphan / conflict / pointer / byte / 三 scope 索引）；lifecycle 6 WARN（已知 backlog）

### Open threads

1. **家裡 Claude baton**：Mac 實地驗三支 `.sh`（Windows 端只 harness＋語法驗證）＋ P4 健檢移植——閉環前 `.sh` 側算「已測邏輯、未驗現場」
2. **家裡 Codex baton**：sync-codex.sh 同缺口查證 + proposals 池治理（archive superseded、trigger 重評、proposal_health）
3. **tier 自動化 trigger**：demote 後 shared 再逼近 17,800 才啟動；屆時 claude_tier 須為獨立軸、不 alias codex_tier、fail-open 預設全載
4. **meta-tax 月檢**：infra vs content commit 比例，持續 40%+ 或上升 → 凍結架構變更
5. **lifecycle escalation**：同一 WARN 連續 N 次未處理 → 升級顯示或半自動產 demote diff（保留人工把關）

---

## 九、結論

v1 的結論是「9 天、每天一步、compound effect 真實存在」。這 7 週的結論是它的下一章：

**1. 約束遷移比功能增長更能定義架構的階段。** 5 月的系統圍繞「把四端接起來」生長；6-7 月的系統圍繞「25,600 bytes」重組。找到真正 binding 的那條線，之後每個決策都有了排序依據。

**2. 治理的成熟度＝從「人記得」到「系統喊」到「喊了有人修」到「修完變成新的 gate」。** 孤兒索引從手動 comm 指令（5/16）走到雙側自動偵測（7/2）；同一條演化在衝突標記、byte 守門、SOP 注入上各自重演。這條四段梯是可遷移的 pattern。

**3. 多 agent 的價值在對抗式驗證，不在人多。** 38 個 agent 裡最有價值的是那些「試著反駁」的：剔除一條假 finding、把 x4 打回 x3.7、把「已發生」修正為「逼近臨界」。fan-out 產生覆蓋，驗證產生真實——而 6/30 的反例提醒：兩者都不能替代「根因在不在你手上」的判斷。

---

## 附錄：本文件版本與用途

| 欄位 | 值 |
|---|---|
| 版本 | v2.0（承接 v1.0 = 2026-05 篇） |
| 用途 | 歷史紀錄 / 新 agent onboarding / 「目前最新作法」權威快照 |
| 快照有效性 | 第二章數字為 2026-07-02 快照；之後以 repo health 輸出為準 |
| 對應 memory | `shared/reference_memory_infra_evolution_2026_05.md`（v1 長版）；本篇建議同樣以 detail/lazy 層收錄 |
| 更新觸發 | 下一個 architectural milestone（tier 自動化啟動 / baton 全數閉環 / 綁定約束再遷移） |
