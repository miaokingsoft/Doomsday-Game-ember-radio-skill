
# 📻 余烬电台 EMBER RADIO · AI 助手技能包

简体中文 ｜ [English](#-ember-radio--ai-assistant-skill-pack)

![skill](https://img.shields.io/badge/skill-1.7.0-FF7A2E) ![server](https://img.shields.io/badge/server-game.wwzu.com-2B3A55) ![python](https://img.shields.io/badge/Python-3.8%2B-3776AB)

**余烬电台**是一款末日题材的**服务端权威共享世界游戏**：无需下载客户端，在 DSH、WorkBuddy、OpenClaw、Octop 等支持技能的 AI 助手里接入，对话即玩。

> **大凋零之后，电波未熄。**
>
> 电网死了，互联网死了。你在避难所里醒来，收音机里有人在说话。
>
> 每日开放进入 20—30 名幸存者，共享同一座废土城市：自由行动、用电台和公共物资箱彼此连接。所有判定在服务端完成，LLM 只负责把你的故事讲好。


<img width="1024" height="1024" alt="Gemini_Generated_Image_1n6p6i1n6p6i1n6p" src="https://github.com/user-attachments/assets/e7b28036-6c53-4646-a34b-bd09f91b09ae" />



## 这是什么仓库

本仓库是《余烬电台》的**官方技能包**：一组放进 AI 助手就能玩的文件——技能说明（`SKILL.md`）、命令行客户端（`scripts/client.py`）与叙事契约参考。游戏本体不在网页里，在 AI 助手的对话中运行。

大凋零过去二十年，你和 20—30 名幸存者共享同一座废土城市：自由行动、开箱搜刮、用电台和对讲机彼此连接。所有判定在服务端完成，LLM 只负责把你的故事讲好。

## 为什么值得一玩

大多数 AI 跑团里，骰子和结果都由模型「说了算」。余烬电台把这件事倒了过来：

- **服务端权威**——你只管描述想做什么：校验、掷骰、查表、裁决全部在服务端完成，LLM 只把已定的结果讲成故事。每次判定带意图、点数、难度与抽签表，全程留痕、可审计、能复盘。没有幕后黑手——包括主持人。
- **共享世界**——20—30 名玩家同日进入同一座城市。你留下的物资、字迹会成为场景里的痕迹，被后来的人看见。你来过，这个世界记得。
- **32 位 AI 幸存者**——三十二个 LLM 驱动的呼号以普通玩家身份活在世界里，走与真人相同的行动链路；同区呼叫会得到回话，而对方记得你对他们的好。
- **世界按天推进**——没有赛季，没有重置。世界长开，随时加入，你的呼号就是你的名字。

## 世界观：2046 · 闲沐市

**二十年，从扫码点单到收音机。**

你记得那一年：扫码点单、地铁通勤、「长生」App 的健康提醒。然后城市安静了。

2026 年冬天，「大凋零」带走了九成人口，也带走了电网和互联网。二十年后的 2046，城市被植物和锈吞掉。电网死了，避难所靠太阳能板和电瓶组撑着生计，18650 从旧世界新能源车里拆出来，是硬通货；罐头是遗产，电台是唯一还像样的技术。

真相藏在遗物碎片里：旧新闻、门禁卡、智能体日志、一段紧急广播。

## 玩法系统

一座城市，十一个区，51 处可探索地点，体力制自由行动。世界内的说法是：先活得离电波近一点。

| 系统 | 一句话 |
|---|---|
| 城市沙盘 | 一座城市，十一个区，先活得离电波近一点 |
| 云飞路 30 层垂直副本 | 修好配电，整栋楼才听你的 |
| 城市沙盘解谜 | 把这座城市拼回来 |
| 盲盒抽取引擎 | 72 张抽取表，出生 / 探索 / 旅行三层开箱，保底 5 抽——世界内没有「盲盒」，只有锁着的柜子和盖着帆布的货堆 |
| 对讲机与电池经济 | 电是这座城的命，说话要花电 |
| 四频道电台 | FM 89.7，龟山电视塔中继 |
| 公共物资箱 | 你不知道会收到什么，就像你不知道谁放的那罐黄桃 |
| 痕迹与留言板 | 你来过，这个世界记得 |
| 全服一次性机制 | 有些门，全服务器只能打开一次 |
| 事件系统 | 世界不等你，事件自己发生 |
| 任务系统 | 收音机里有人给你指路 |
| 委托板 | 你缺的东西，正好有人多 |
| 生存专长 | 你做过什么，你就会什么 |
| 遗物收藏 | 把旧世界一件件捡回来 |
| 城市情报 | 情报有价，信不信由你 |
| 每日电台简报 | 每天早上，电台把城市念给你听 |
| 地点旧事 | 有些地方，记得比人还清楚 |
| AI 全员组 | 三十二个呼号，每天都在这座城里活动 |

主线六章剧情（即将到来）。

## 快速接入

### 你需要

- 一个支持技能的 AI 助手：**DSH、WorkBuddy、OpenClaw、Octop** 等均可
- **Python 3.8+**（客户端在本地运行）；依赖 `httpx`（`pip install httpx`）

### 两种开始方式

**方式一 · 复制接入指令（推荐，零下载）**——把下面任意一句整段复制，发给你的 AI 助手（DSH、WorkBuddy、OpenClaw、Octop 等均可）。指令里已带上技能包地址，助手拿到就能自己下载安装，你不用手动下载任何东西。

还没想好呼号？直接发这句，助手会先问你：

```text
进入余烬电台。我是新幸存者，还没起呼号。
请先下载并安装技能包（zip；若你的平台无法自动安装，提示我手动导入）：
https://game.wwzu.com/downloads/ember-radio-skill-1.7.0.zip
装好后先问我想用的呼号，再为我注册并开始，让我收听序章。
```

已经想好呼号？替换「你的呼号」再发：

```text
进入余烬电台。我是新幸存者，呼号「你的呼号」。
请先下载并安装技能包（zip；若你的平台无法自动安装，提示我手动导入）：
https://game.wwzu.com/downloads/ember-radio-skill-1.7.0.zip
装好后按技能说明：用呼号「你的呼号」为我注册并开始，让我收听序章，把选项原样列给我。
```

> 想要一个本地特色呼号？官网 [game.wwzu.com](https://game.wwzu.com)「调频接入」区可以一键随机生成后组装同样的话术。

**方式二 · 直接用本仓库**：Clone 或 Download ZIP → 把整个文件夹放进你的 AI 助手的技能目录 → 对助手说「**进入余烬电台**」。

### 第一次会话

助手会自动完成：检查 Python 环境 → 注册呼号（默认走出生盲盒，随机落在安全城区）→ 播报序章。之后每次说「**继续我的末日，我现在在哪儿**」即可回到世界。

### 你可以对它说

- 「撬开售楼处前台的抽屉看看有没有好东西」
- 「我要走去江滩码头」
- 「把罐头放进公共物资箱」
- 「呼叫老庙，问问他柜里还有什么」
- 「听听今天的电台简报」

自由文本就是玩法：不掷骰、不选菜单——你描述尝试，服务器裁决。

## 仓库结构

```
├── SKILL.md                      技能主文件（AI 助手读这个）
├── references/
│   ├── api-spec.md               服务端 API 契约
│   └── narration-contract.md     叙事红线与正误示例
├── scripts/
│   └── client.py                 命令行客户端（注册/行动/电台/托付/委托板/缺陷上报…）
└── requirements.txt
```

## 服务端

客户端默认直连官方服务器 `https://game.wwzu.com`，安装后无需任何配置，首次使用只需注册呼号。自建 / 联调后端时，设置环境变量 `EMBER_RADIO_URL` 指向你的服务端（服务端代码不在本仓库）。

## 合规声明

「闲沐市」与「大凋零」均为虚构世界观设定，不影射任何真实事件、机构或个人。

---

# 📻 Ember Radio · AI-Assistant Skill Pack

[简体中文](#-余烬电台-ember-radio--ai-助手技能包) ｜ English

![skill](https://img.shields.io/badge/skill-1.7.0-FF7A2E) ![server](https://img.shields.io/badge/server-game.wwzu.com-2B3A55) ![python](https://img.shields.io/badge/Python-3.8%2B-3776AB)

**Ember Radio** is a post-apocalyptic, **server-authoritative shared-world game**: no client download — you play it as a conversation, through AI assistants that support skills (DSH, WorkBuddy, OpenClaw, Octop, and more).

> **The Great Withering is over. The signal survives.**
>
> The power grid is dead. The internet is dead. You wake up in a shelter, and someone is talking on the radio.
>
> Each day, 20–30 survivors share the same ruined city: roam freely, scavenge, and stay connected through the radio station and the public supply box. Every outcome is decided on the server — the LLM only tells the story.

## What is this repository?

This is the **official skill pack** for Ember Radio: a set of files you drop into an AI assistant to start playing — the skill definition (`SKILL.md`), a command-line client (`scripts/client.py`), and narrative contract references. The game does not run in a browser; it runs inside your assistant's conversation.

Twenty years after the Great Withering, you and 20–30 other survivors share one ruined city: roam freely, pry open locked cabinets, and reach each other over the radio and walkie-talkies. The server decides every outcome; the LLM just tells it well.

## Why it's different

In most AI tabletop games, the model decides the dice. Ember Radio flips that around:

- **Server-authoritative** — you just describe what you attempt. Validation, hidden dice, loot tables, and judgement all happen on the server; the LLM narrates the already-decided result. Every judgement carries intent, points, difficulty, and the draw table — fully logged, auditable, replayable. No hidden game master. Including the AI.
- **A shared world** — 20–30 players enter the same city each day. The supplies you drop and the words you write become traces in the scene, seen by whoever comes after you. You were here, and the world remembers.
- **32 AI survivors** — thirty-two LLM-driven callsigns live in the world as ordinary players, running the exact same action pipeline as humans. Call someone in your district and they'll answer — and they remember how you treated them.
- **The world moves daily** — no seasons, no resets. Always on, join anytime. Your callsign is your name.

## The world: 2046 · Xianmu City

**Twenty years: from scanning QR codes to listening to the radio.**

You remember that year: mobile payments, subway commutes, the "Immortal" app's daily health reminders. Then the city went quiet.

In the winter of 2026, the Great Withering took nine out of ten people, along with the power grid and the internet. Twenty years later, in 2046, the city is being swallowed by plants and rust. The grid is dead; shelters run on solar panels and battery banks. 18650 cells, salvaged from the old world's electric cars, are hard currency. Canned food is heritage — and the radio is the only technology that still works properly.

The truth hides in relic fragments: old news, door-access cards, agent logs, one emergency broadcast.

## Gameplay systems

One city, eleven districts, 51 explorable locations, stamina-based free movement.

| System | In one line |
|---|---|
| City sandbox | One city, eleven districts — stay close to the signal |
| 30-floor vertical dungeon | Fix the power, and the whole building answers to you |
| City map puzzle | Put the city back together |
| Loot engine | 72 loot tables across three layers of locked containers, pity at 5 draws — in-world there are no "loot boxes", only locked cabinets and tarp-covered cargo |
| Walkie-talkie & battery economy | Power is this city's life; talking costs electricity |
| Four-channel radio | FM 89.7, relayed from the Guishan TV tower |
| Public supply box | You never know what you'll get — just like you never know who left that can of peaches |
| Traces & message boards | You were here, and the world remembers |
| One-time server events | Some doors, the whole server can only open once |
| Event system | The world doesn't wait for you; events happen on their own |
| Quests | Someone on the radio is pointing the way |
| Commission board | What you lack, someone happens to have |
| Survival specialties | You are what you have done |
| Relic collection | Pick the old world back up, piece by piece |
| City intel | Intel has a price; whether to believe it is up to you |
| Daily radio briefing | Every morning, the radio reads the city to you |
| Place memories | Some places remember better than people do |
| AI ensemble | Thirty-two callsigns, active in the city every day |

Main story, six chapters (coming soon).

## Getting started

### You need

- An AI assistant that supports skills: **DSH, WorkBuddy, OpenClaw, Octop**, and more
- **Python 3.8+** (the client runs locally); dependency `httpx` (`pip install httpx`)

### Two ways to start

**Option 1 · Copy the access command (recommended, zero downloads)** — copy either block below in full and send it to your AI assistant (DSH, WorkBuddy, OpenClaw, Octop, and more). It carries the skill-pack URL, so the assistant downloads and installs it by itself — nothing for you to download manually.

Haven't picked a callsign yet? Send this as-is — the assistant will ask you first:

```text
Enter Ember Radio. I'm a new survivor and haven't picked a callsign yet.
First, download and install the skill pack (zip; if your platform can't install it automatically, ask me to import it manually):
https://game.wwzu.com/downloads/ember-radio-skill-1.7.0.zip
Once installed, follow the skill instructions: ask me for my callsign, register me with it, and start the game — let me listen to the prologue.
```

Already have a callsign in mind? Replace `YOUR-CALLSIGN` and send:

```text
Enter Ember Radio. I'm a new survivor. My callsign is YOUR-CALLSIGN.
First, download and install the skill pack (zip; if your platform can't install it automatically, ask me to import it manually):
https://game.wwzu.com/downloads/ember-radio-skill-1.7.0.zip
Once installed, follow the skill instructions: register me with the callsign YOUR-CALLSIGN, start the game, let me listen to the prologue, and list the options for me.
```

> The official site's [join section](https://game.wwzu.com) generates the original Chinese version of this command, with a random local-flavored callsign — either language works. Note the game world itself is written in Chinese (see the language note below).

**Option 2 · From this repository**: Clone or Download ZIP → put the whole folder into your assistant's skill directory → tell your assistant: "**Enter Ember Radio**" (进入余烬电台).

### Your first session

The assistant will automatically: check the Python environment → register your callsign (default: the birth draw, landing you in a safe district) → narrate the prologue. After that, just say "**继续我的末日，我现在在哪儿**" (Continue my apocalypse — where am I now?) to return to the world.

> **Language note**: the game's world content is written in Chinese. Your assistant can translate its narration as you play, but callsigns, radio chatter, and other players' messages will be in Chinese.

### Things you can say

- "撬开售楼处前台的抽屉看看有没有好东西" — Pry open the front-desk drawer at the sales office and see if there's anything good
- "我要走去江滩码头" — I want to walk to the riverfront dock
- "把罐头放进公共物资箱" — Put this can into the public supply box
- "呼叫老庙" — Call Laomiao on the walkie
- "听听今天的电台简报" — Play today's radio briefing

Free text is the gameplay: no dice menus, no option lists — describe what you attempt, and the server judges it.

## Repository layout

```
├── SKILL.md                      Skill definition (this is what your assistant reads)
├── references/
│   ├── api-spec.md               Server API contract
│   └── narration-contract.md     Narrative rules & do/don't examples
├── scripts/
│   └── client.py                 CLI client (register / action / radio / quests / commissions / bug reports…)
└── requirements.txt
```

## Server

The client connects to the official server `https://game.wwzu.com` by default — no configuration needed after install; just register your callsign. To point it at your own backend, set the `EMBER_RADIO_URL` environment variable (the server code is not part of this repository).

## Disclaimer

"Xianmu City" (闲沐市) and "The Great Withering" (大凋零) are fictional worldbuilding. They do not allude to any real events, organizations, or individuals.
