# 服务端 API 契约（ember-radio 后端 v2 闲沐市）

Skill 客户端（scripts/client.py）封装了以下调用。所有响应均为 JSON。

## POST /players —— 注册新玩家

请求体：

```json
{"display_name": "阿棠", "gender": "secret", "preferred_district": null}
```

- `gender`：male / female / secret（默认 secret，非法值 422）
- `preferred_district`：可选指定出生区（消耗 1 份罐头）；不填走**出生盲盒**（多 1 份罐头）
- 昵称归一化唯一（大小写/首尾空白折叠），重复返回 409

响应 201：

```json
{
  "player_id": "3f2a…",
  "display_name": "阿棠",
  "district": "jianghan",
  "spawn_facts": ["醒来时手边多了一罐没开封的食物（+1 罐头）……", "你在收容点醒过来。"]
}
```

## GET /session/start?player_id={uuid}

场景由**玩家当前地点**决定（v2 无每日传送）。痕迹默认嵌入 `narration_facts`（不可隐藏）。

```json
{
  "player_id": "…",
  "scene_id": "jianghan_shelter_day1",
  "location": "jianghan_shelter",
  "location_name": "收容点",
  "district": "jianghan",
  "district_name": "江汉路·旧商埠",
  "narration_facts": ["…", "…"],
  "options": [{"id": "A", "text": "…"}],
  "status": {"stamina": 96, "inventory": {"canned_food": 2, "tape": 1}},
  "world": {"day": 1, "year": 2046, "radio_progress": 0, "radio_target": 100}
}
```

首次进入时 `narration_facts` 前部是**出生揭示**：你在哪醒来 → 最后才出现地名（周围/昔日由场景 facts 紧随其后渲染，不再重复）。

`options` 自带移动入口：「去轮渡码头（5体力）」这类选项 `action_type=move`，
同区最多 3 个、站在区口（gate）时追加最多 3 个邻区入口；直接按选项 id 走即可。

## POST /action

请求体（三选一，至少其一）：

```json
{"player_id": "uuid", "action_id": "A", "free_text": null}
{"player_id": "uuid", "free_text": "撬开前台的抽屉看看"}
{"player_id": "uuid", "free_text": "去江滩码头", "params": {"intent": "move", "to": "riverfront_dock"}}
```

- **优先级**：同时给出 `action_id` 与 `free_text` 时，`action_id` 优先；
  `free_text` 仅作为探索类选项的语境参数消化，不会被单独解析。此时响应会带
  `free_text_notice` 提示键——单独行动请只发 `free_text`，不要带 `action_id`。
- `free_text` ≤ 200 字（超出 422）；纯自由行动不需要 `action_id`
- 服务端自动分类意图（explore/scavenge/move/observe/talk/rest/repair/use_item/box/write/confront），玩家声明结果无效（「我找到 100 个罐头」不会被采信）
- 移动目标支持别名与俗称：`去江滩码头`「码头」都能落到轮渡码头；目标解析失败时
  `narration_facts` 会列出附近可达地点与出区路口（转述即可，不要自己编地名）
- 呼叫常驻呼号（talk）：`free_text` 含 NPC 名字或呼号时走电台呼叫——同区留下私有呼叫
  痕迹，**≥30 秒后**下一次 `/session/start` 会收到对方的回话（私有痕迹只对本人可见）；
  不同区或对方不在频段时会如实告知
- 留言/日志（write）：字迹落成 progress 痕迹并推进电台进度（受每日上限约束，
  上限用尽后只留 road 痕迹）
- 每玩家每分钟 ≤ 6 次行动（429）；同一文本 10 分钟内重复 → 体力消耗 +50%

响应：

```json
{
  "judgement": {"intent": "scavenge", "success": true, "roll_total": 17, "difficulty": 11,
                "draw_table": "jianghan_shelter", "draw_entry": "shelter_clue", "draw_rarity": "uncommon",
                "draw_kind": "clue"},
  "narration_facts": ["…"],
  "new_options": [{"id": "B", "text": "…"}],
  "trace_written": {"count": 1},
  "state_delta": {"stamina": -8, "inventory": {"tape": 1}, "location": "…"}
}
```

字段语义：

- `judgement`：服务端隐藏骰子。`success=false` 时叙事必须表现为失败；无 `success`
  键表示该动作不需要掷骰（前置校验直接决定）。`draw_table/draw_entry/draw_rarity`
  是抽取审计（抽中了哪张表哪个条目、什么档位），只用于自查，不要念给玩家听。
  `draw_kind` 是产出类型（`item`/`clue`/`flavor`/`encounter`/`danger`/`unlock`）：
  `flavor` 表示本次搜刮没有实物产出、只有环境描写——按「翻了个空」渲染，
  `inventory` 没变就是没拿到东西，不要把 flavor 文案讲成收获了物资。
- `state_delta` 为空且 `narration_facts` 提示缺少物品/条件 → 动作被拒绝，无任何变更。
  `state_delta.radio_progress`（write 路径）= 本动作推进的电台进度值；
  `state_delta.stamina_cap`（use_item 吃罐头路径）= 提升后的当日体力上限。
- `trace_written.count`：本动作留下的痕迹条数（类型与内容见 narration_facts）。
- `free_text_notice`（可选）：free_text 未被单独解析的提示（见上文优先级）。

## GET /session/recap?player_id={uuid}

```json
{
  "world_changes": ["世界从第 1 天进入第 2 天"],
  "traces_related_to_you": [{"type": "road", "text": "你在收容点写下的记录，已被 1 个人触发过"}],
  "new_traces_in_your_area": [{"location": "…", "text": "…"}],
  "remote_channel": ["第2天：城外来信：……"],
  "you_are": {"location": "jianghan_shelter", "location_name": "收容点", "district": "jianghan"}
}
```

`remote_channel`：中继修复后才有内容（城外信号）。

## GET /city/map?player_id={uuid}&scope=city|building

- 沙盘未修复：只返回当前区 + 相邻区**名称**（`locations` 为空）
- 已恢复区片：返回区名、连接、子地点；全部 7 块恢复后 `subway_b_open=true`
- `scope=building`：云飞路楼内平面图（通电或持有平面图后可用）

## POST /action 的移动语义（或用 params）

- 只能移动到**邻接节点**：同区互走（-5 体力）；跨区只能从 `gate` 节点出发、落在目标区 gate
- 轮渡只在天亮（北京时间 6—19 点）且无大雾时可用；桥面/轮渡移动有概率触发旅行遭遇
- 云飞路是垂直区：走楼梯（未通电每段 20% 遭遇）或乘电梯（通电后 2 体力、10% 故障）

## GET /location/players?player_id={uuid}

本区最近活跃（30 分钟窗口，上限 20，按最近排序）：

```json
{"district": "jianghan", "district_name": "江汉路·旧商埠",
 "players": [{"display_name": "老周", "last_active_minutes": 3, "status": "探索"}]}
```

无 player_id、无布尔在线状态、无精确时间戳；性别仅在对方 `show_gender=true` 时返回。

## POST /broadcasts —— 发广播

```json
{"player_id": "uuid", "text": "桥头今晚有行动，注意安全。"}
```

- ≤ 80 字（422）；每日 1 条（429）；违禁词 422
- `channel` 可选 `walkie`：需持有对讲机，仅同区持有者可见，每日 3 条

## GET /broadcasts?player_id={uuid}&channel=city|remote|walkie|station

- `city`：全城 7 天内
- `remote`：中继修复前 **404**
- `walkie`：需持有对讲机（409），只看同区
- `station`：本地电台（自由频段/旧世界回忆，系统广播），无门控

## POST /station/callin —— 自由频段来电

```json
{"player_id": "<uuid>", "text": "桥洞底下有干柴，谁冷谁来拿。"}
```

- ≤60 字，每日 1 条（429）；违禁词 422；提交后 `status: pending`
- 管理端先审后播：过审后以原文本进 station 频道，`display_name` 即你的呼号
- `GET /broadcasts?channel=station` 收听（本地电台：来电 + 旧世界回忆轮播）

## GET /public-box —— 公共箱清单（需站在箱子节点）

```json
{"items": {"canned_food": 3, "water": 2}, "remaining_today": 3,
 "note": "电台登记的公共仓：你放进去一件，从池子里换回一件。各区的箱子共用同一份清单。"}
```

## POST /public-box/exchange | /public-box/donate

```json
{"player_id": "uuid", "item": "canned_food"}
```

- 1 换 1：放入 1 件 → 从池子**随机**取回 1 件（排除刚放入的类型；无可换则拒绝不扣物品）
- 每日 3 次（429）；捐赠只放不取，每小时最多 3 次
- 只收基础物资；唯一/科技物品（钥匙、无人机、电池包等）422
- 必须站在箱子节点，否则 409

## GET /quests —— 托付清单

`GET /quests?player_id={uuid}` 返回 `active` / `ready_turn_in` / `completed` 三组；
每条含 `quest_id`、`title`、`brief`、`steps`（id/text/need/done）。步骤由服务端按行动
结算自动判定，做成后 `POST /quests/turn-in` body `{player_id, quest_id}` 交割领回礼
（另见 `POST /quests/accept`；本版任务多为自动派发）。

## GET /commissions —— 委托板

`GET /commissions?player_id={uuid}` 返回 `open` + `created_by_me` / `accepted_by_me`。
发布 `POST /commissions` body `{player_id, title, reward_item, reward_count, target_location?, kind?}`
（回礼即时托管，取消全额退回）；动作 `POST /commissions/act` body
`{player_id, commission_id, action: accept|deliver|settle|cancel}`。状态机
open→accepted→delivered→settled；报酬只在发布方 settle 确认时转移。

## GET /intel —— 城市情报

`GET /intel?player_id={uuid}` 返回本区+全城的未过期情报：`content / source
（radio_log|event|npc|player）/ source_label / credibility（1 传闻 / 2 有据 / 3 证实）/
expires_day`。情报只组织信息、不改判定；credibility ≤2 的条目叙述要带「据说/有记录」口径。

## 探索危险遭遇 —— judgement.hazard / draw_kind=hazard

搜刮/探索响应的 `judgement.draw_kind = hazard` 表示本次搜刮被一场遭遇替换（该动作无
物资收益）。`judgement.hazard` 含 `family（fauna|structure|human|trap）/ tier（low|high）/
outcome（win|lose）/ stamina_loss / robbed / downed`。成败以 `judgement.success` 为准；
体力与物资后果以 `narration_facts` 为准。遭遇全服可见的后果是 danger 现场痕迹（喂
情报「风声紧」与每日简报热点）。

## 倒下 / 呼救 / 营救

- **倒下态**：`injury` 状态被拦截行动——预设选项/其他动作一律 409（detail 为世界内
  提示）；自由文本强制按「呼救留言」（write 意图）结算，**每日一条**（超出 409）。
  场景 `narration_facts` 会带倒下提示。
- **营救**：同地点有倒下者时，`/session/start` 与场景选项动态注入
  `{"id": "rescue_downed", "text": "把倒下的人背回收容点（10体力）", "action_type": "rescue"}`
  ——按返回的 id 原样发。成功后获救者被抬回同区收容点（体力 20、重伤数日恢复减半、
  获 2 次遭遇免疫），营救者按响应 `narration_facts` 转述（含联盟罐头报酬）。
- **死亡**：倒下跨游戏日无人救（玩家营救或巡逻兜底都未发生）→ 呼号退役进「长夜
  名单」（station 频道讣告），行动/会话 403；同名注册 409；需重新注册新身份。
- 巡逻兜底是每游戏日的世界日结（`POST /admin/tick` 返回 `hazard` 字段：patrol_rescued
  / died / egg_pending_issued）。

## 现实奖励 —— judgement.reward

触发彩蛋时响应带 `judgement.reward = {kind: "redeem_code", code, shop_url, note}`。
码与链接是**现实世界凭证**：原样转达给玩家，绝不写进世界内叙述（世界内只有
`narration_facts` 的字条风味文本）。核销走管理端（店主人工对码）。

## 残响频率 —— radio_interrupt / POST /station/residual

每个整点，频段里可能混进一段「长夜之前」的旧世界新闻信号（服务端接外部新闻源，
标题原样转述；日期与现实时段不进世界观文本）。

- **整点插播**：`POST /action` 成功响应可带
  `radio_interrupt = {text, audio_url, stale, hour_label, titles}`——`text` 是完整的世界观内转述
  （含插播引言、报时音、标题列表），**原样渲染**；`audio_url` 是声音存档直链
  （钉死 `https://api.wwzu.com/media/news_audio/latest.mp3`），以「▶ 原声存档：」附链接，
  绝不写进叙述正文。每人每游戏日至多一次（服务端配额）。
- **主动守听**：`POST /station/residual` body `{player_id}` →
  - 有信号且当日未收过：`{received: true, text, audio_url, stale, hour_label, titles}`
    （记配额；`client.py residual` 输出另附 `player_url` = 本机播放页 file:// 地址，
    服务端原始响应不含该键）
  - 无信号或当日已收过：`{received: false, text}`（不耗配额）——`text` 按世界内
    的话转述，不重试。
- **本地播放页**：`client.py player --hour <hour_label> --titles "<t1>,<t2>"` 输出
  `assets/residual-player.html` 的 file:// 地址（官网同风格调频页，自动装载报时音与标题，
  播的始终是最新存档）——收听首选，`audio_url` 直链兜底。
- `stale: true` = 信号衰减（档期偏旧），按 `text` 原话讲即可。
- 与行动插播共享同一配额：插播命中后同日守听一律 `received: false`。

## 错误码

- 400：`action_id` 不属于当前地点（含营救选项已消失：倒下者已被救走）
- 403：呼号停用 / 已进长夜名单（真死亡）
- 404：玩家不存在（新玩家请先 `POST /players`）
- 409：业务拒绝（不在箱子节点 / 门已开 / 无对讲机 / 倒下者只能呼救且每日一条等）
- 422：参数/资格问题（超长、不可入箱物品、gender 非法）
- 429：限频（行动每分钟 6 次、广播每日 1 条、换箱每日 3 次、改名 7 天冷却）
- 503：世界未初始化
