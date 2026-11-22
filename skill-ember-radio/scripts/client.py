"""Ember Radio Skill 客户端（WorkBuddy 发布版，v2 闲沐市）。

环境变量：
    EMBER_RADIO_URL              后端地址；不设置时默认官方服务器
                                 https://game.wwzu.com。仅允许 http/https，
                                 默认拒绝 localhost/环回/私有/保留地址
    EMBER_RADIO_PLAYER           玩家 UUID（优先级最高）
    EMBER_RADIO_ALLOW_PRIVATE_NET=1   仅本地联调时显式放开内网限制

首次使用：python scripts/client.py register --name 你的名字
（player_id 会保存到 ~/.ember-radio.json，之后的 start/action/recap 自动使用）

v2 命令：玩家分散在闲沐市 11 个区，场景由所在地点决定。
  start    进入当前地点的场景（首次进入含出生揭示）
  action   自由文本行动（撬/搜/看/修/睡……服务端分类与判定）
  move     移动到相邻地点（说名字即可，如「步行街中段」）
  map      城市地图（沙盘修复程度决定可见范围）
  nearby   本区最近活跃的人
  broadcast 城市广播（每日 1 条，≤80 字）
  residual  守听残响（整点旧世界信号；每日 1 次）
  player   残响本地播放页地址（--hour/--titles，收听首选）
  box      公共物资箱 exchange/donate（需站在箱子节点）
  quests   托付清单（进行中/可交割/已交割）
  quest-accept / quest-turn-in --id  接下/交割一桩托付（办妥步骤后交割领回礼）
  version  查看本地技能包版本，并联网核对官网直链是否已更新
  bug-report 上报缺陷反馈给电台管理员（玩家明确要求时才用）
"""
from __future__ import annotations
# v1.5.0（四批实施）：新增 quests / quest-accept / quest-turn-in / commission / intel
# 五组命令——托付链、委托板、城市情报（对应服务端 v2.6.0 四批实施）；
# 下载直链改版本化 downloads/ember-radio-skill-<version>.zip（官网话术同步），
# 无版本别名 /downloads/ember-radio.zip 保留给自更新核对与旧话术兼容；
# min_server_version 随本包对齐 2.6.0（内测期技能包与服务端同批发布）
# v1.4.3（版本治理 P0-01）：新增最低服务端版本契约——SKILL.md 声明
# min_server_version，register 前核对 /health 版本、低于下限拒绝注册，
# version 命令附带服务端版本提示（服务端未知/不可达不阻断）
# v1.4.2（反馈 #FAZIdnON #B/#C）：register 撞名 409 时 KeyError 崩溃——
# 业务拒绝现在拦在写本机配置之前，detail 原样转述；新增 version 子命令，
# 玩家可自查本地是否最新（直链 zip 内 SKILL.md 的 version 为线上事实源）
# v2.4.1（试玩报告2 #A）：注解里的 `dict | None` 在 Python 3.7 上是运行时
# TypeError——future import 让旧解释器不在函数签名上炸；下方版本守卫负责
# 给出人话报错（httpx>=0.27 本身也不支持 3.7，所以门槛定在 3.8）
import argparse
import io
import ipaddress
import json
import os
import re
import socket
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlencode, urlsplit

if sys.version_info < (3, 8):
    sys.stderr.write(
        "余烬电台客户端需要 Python 3.8 及以上（当前 %d.%d.%d）。\n"
        "请升级 Python 后重试；httpx>=0.27 也不支持 3.7 及更早版本。\n"
        % sys.version_info[:3]
    )
    raise SystemExit(2)

try:
    import httpx
except ModuleNotFoundError:
    sys.stderr.write(
        "缺少依赖 httpx。请先执行：pip install httpx（或 pip3 install httpx），\n"
        "然后重试本命令。安装失败时把报错如实转述给玩家。\n"
    )
    raise SystemExit(2)

CONFIG_PATH = Path.home() / ".ember-radio.json"
DEFAULT_SERVER = "https://game.wwzu.com"

# 技能包版本：与 SKILL.md frontmatter 的 version 必须一致
# （build_skill_zip.py 自检把关，改版本时两处一起改）
__version__ = "1.9.0"
# 技能包契约要求的最低服务端版本：低于此版本不保证接口齐备
# （托付/委托板/情报等接口随本包上线；register 时强校验，version 时仅提示。
#  内测期技能包与服务端同批发布，下限直接对齐当前服务端版本）
MIN_SERVER_VERSION = "2.11.0"
# 稳定地址：官网话术内嵌的版本化直链会随发版改名，旧话术/旧包仍可用这条别名
# （build_skill_zip.py 同时产出 downloads/ember-radio-skill-<version>.zip 与别名）
SKILL_ZIP_PATH = "/downloads/ember-radio.zip"


def skill_zip_url(version: str) -> str:
    """版本化下载直链（向玩家展示用；别名只用于本机自更新核对）。"""
    return f"{BASE}/downloads/ember-radio-skill-{version}.zip"


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
    return {}


def _save_config(data: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _host_allowed(hostname: str) -> bool:
    """解析并校验主机：环回/私有/链路本地/保留/未指定/多播地址一律拒绝。"""
    try:
        infos = socket.getaddrinfo(hostname, None)
    except OSError as exc:
        raise SystemExit(f"无法解析主机 {hostname!r}: {exc}")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_unspecified
            or ip.is_multicast
        ):
            return False
    return True


def _validate_base(url: str) -> str:
    if not url.strip():
        raise SystemExit("请先设置 EMBER_RADIO_URL（余烬电台后端地址）")
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise SystemExit(
            f"EMBER_RADIO_URL 协议必须为 http/https，收到: {parts.scheme!r}"
        )
    hostname = parts.hostname
    if not hostname:
        raise SystemExit("EMBER_RADIO_URL 缺少主机名")
    if os.environ.get("EMBER_RADIO_ALLOW_PRIVATE_NET") != "1":
        if not _host_allowed(hostname):
            raise SystemExit(
                f"拒绝连接到 localhost/内网/保留地址: {hostname}；"
                "本地联调请显式设置 EMBER_RADIO_ALLOW_PRIVATE_NET=1"
            )
    return url.rstrip("/")


BASE = _validate_base(
    os.environ.get("EMBER_RADIO_URL", "").strip() or DEFAULT_SERVER
)
PLAYER = os.environ.get("EMBER_RADIO_PLAYER", "").strip() or str(
    _load_config().get("player_id", "")
).strip()

# follow_redirects=False：不做跨源跳转
_client = httpx.Client(base_url=BASE, timeout=20, follow_redirects=False)


def _player_id() -> str:
    if PLAYER:
        return PLAYER
    raise SystemExit(
        "尚未绑定玩家身份：先运行 python scripts/client.py register --name 你的名字"
    )


def get_json(path: str, params: dict | None = None) -> dict:
    r = _client.get(path, params=params)
    return _as_result(r)


def post_json(path: str, body: dict) -> dict:
    r = _client.post(path, json=body)
    return _as_result(r)


def _as_result(r: httpx.Response) -> dict:
    """业务拒绝（409/422/429 等）的 detail 是面向玩家的事实，原样返回给叙事层。

    响应带 "error" 键 = 本次操作未发生；叙事 AI 应把 detail 转述给玩家。
    """
    if r.status_code < 400:
        return r.json()
    try:
        data = r.json()
        detail = data.get("detail") if isinstance(data, dict) else None
    except ValueError:
        detail = r.text[:200]
    return {"error": r.status_code, "detail": detail or "请求失败"}


def check_server_version(strict: bool):
    """核对服务端版本是否满足技能包契约（/health 的 version 字段）。

    低于 MIN_SERVER_VERSION 时：strict=True（注册前）直接退出并给出人话
    说明——旧服务端可能缺接口，注册成功也玩不全；strict=False 只提示不拦。
    /health 不可达时不阻断（误配置会在首个真实请求处报错，不在这里误伤）。
    返回服务端版本字符串（核对失败时返回 None）。
    """
    try:
        r = _client.get("/health")
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code}")
        server = str(r.json().get("version", "")).strip()
    except Exception as exc:
        print(f"（服务端版本核对失败：{exc}，继续）")
        return None
    sv, mv = _vtuple(server), _vtuple(MIN_SERVER_VERSION)
    if server and sv is not None and mv is not None and sv < mv:
        msg = (
            f"服务端版本 {server} 低于技能包要求的最低版本 {MIN_SERVER_VERSION}，"
            "托付/委托板/城市情报等接口可能不可用"
        )
        if strict:
            sys.stderr.write(
                msg + "；已停止注册。请联系服务方升级服务端，或改用与其匹配的旧版技能包。\n"
            )
            raise SystemExit(1)
        print(f"（提示：{msg}）")
    return server or None


def cmd_register(args):
    check_server_version(strict=True)
    body = {"display_name": args.name}
    if args.gender:
        body["gender"] = args.gender
    if args.district:
        body["preferred_district"] = args.district  # 指定区消耗 1 份罐头；不填走出生盲盒
    data = post_json("/players", body)
    # 注册是唯一在客户端写本机身份的命令，业务拒绝（409 重名等）必须拦在
    # 写配置之前——否则 KeyError 崩溃会让玩家误以为服务器坏了而反复重试。
    if data.get("error"):
        sys.stderr.write(f"{data.get('detail')}\n")
        raise SystemExit(1)
    _save_config(
        {"player_id": data["player_id"], "display_name": data["display_name"]}
    )
    print(json.dumps(data, ensure_ascii=False))


def cmd_start(args):
    data = get_json("/session/start", {"player_id": _player_id()})
    print(json.dumps(data, ensure_ascii=False))


def cmd_action(args):
    body: dict = {"player_id": _player_id()}
    if args.action_id:
        body["action_id"] = args.action_id
    if args.text:
        body["free_text"] = args.text[:200]
    if not args.action_id and not args.text:
        raise SystemExit("自由行动请给 --text，预设选项给 --action-id（二选一）")
    print(json.dumps(post_json("/action", body), ensure_ascii=False))


def cmd_move(args):
    """移动：走自由行动管线（服务端校验邻接与体力）。"""
    body = {
        "player_id": _player_id(),
        "free_text": f"去{args.to}",
        "params": {"intent": "move", "to": args.to},
    }
    print(json.dumps(post_json("/action", body), ensure_ascii=False))


def cmd_map(args):
    params = {"player_id": _player_id()}
    if args.scope:
        params["scope"] = args.scope  # city | building
    print(json.dumps(get_json("/city/map", params), ensure_ascii=False))


def cmd_nearby(args):
    print(json.dumps(get_json("/location/players", {"player_id": _player_id()}), ensure_ascii=False))


def cmd_broadcast(args):
    print(json.dumps(post_json("/broadcasts", {"player_id": _player_id(), "text": args.text[:80]}), ensure_ascii=False))


def cmd_broadcasts(args):
    params = {"player_id": _player_id()}
    if args.channel:
        params["channel"] = args.channel  # city | remote | walkie
    print(json.dumps(get_json("/broadcasts", params), ensure_ascii=False))


def cmd_residual(args):
    """守听残响：主动入口，与行动响应里的 radio_interrupt 共享每日配额。"""
    data = post_json("/station/residual", {"player_id": _player_id()})
    if data.get("received"):
        url = residual_player_url(data.get("hour_label"), data.get("titles") or [])
        if url:
            data["player_url"] = url  # 本地播放页（官网风格，打开即调频收听）
    print(json.dumps(data, ensure_ascii=False))


def residual_player_url(hour: str | None = None, titles=None) -> str | None:
    """本地播放页的 file:// 地址（assets/residual-player.html，与官网同风格）。

    页面自包含单文件；hour/titles 经查询参数传给页面渲染报时音与标题。
    打包后与 client.py 的 scripts/ 同级；源码运行同样按相对结构解析。
    """
    page = Path(__file__).resolve().parent.parent / "assets" / "residual-player.html"
    if not page.is_file():
        return None
    query: dict = {}
    if hour:
        query["hour"] = str(hour)[:10]
    if titles:
        joined = "‖".join(str(t).strip() for t in titles if str(t).strip())[:600]
        if joined:
            query["titles"] = joined
    url = page.as_uri()
    if query:
        url = f"{url}?{urlencode(query)}"
    return url


def cmd_player(args):
    """输出本地播放页地址（供助手在整点插播后引导玩家打开收听）。"""
    titles = [t.strip() for t in (args.titles or "").split(",") if t.strip()] or None
    url = residual_player_url(args.hour, titles)
    if not url:
        print(json.dumps({"error": 404, "detail": "本机技能文件缺 assets/residual-player.html——请重新下载技能包。"}, ensure_ascii=False))
        return
    print(url)


def cmd_box(args):
    if args.mode == "show":
        print(json.dumps(get_json("/public-box", {"player_id": _player_id()}), ensure_ascii=False))
        return
    body = {"player_id": _player_id(), "item": args.item}
    path = "/public-box/exchange" if args.mode == "exchange" else "/public-box/donate"
    print(json.dumps(post_json(path, body), ensure_ascii=False))


def cmd_recap(args):
    print(json.dumps(get_json("/session/recap", {"player_id": _player_id()}), ensure_ascii=False))


def cmd_quests(args):
    print(json.dumps(get_json("/quests", {"player_id": _player_id()}), ensure_ascii=False))


def cmd_quest_accept(args):
    body = {"player_id": _player_id(), "quest_id": args.id}
    print(json.dumps(post_json("/quests/accept", body), ensure_ascii=False))


def cmd_quest_turn_in(args):
    body = {"player_id": _player_id(), "quest_id": args.id}
    print(json.dumps(post_json("/quests/turn-in", body), ensure_ascii=False))


def cmd_commission(args):
    if args.mode == "list":
        print(json.dumps(get_json("/commissions", {"player_id": _player_id()}), ensure_ascii=False))
        return
    if args.mode == "create":
        body = {"player_id": _player_id(), "title": args.title, "reward_item": args.item,
                "reward_count": int(args.count or 1)}
        if args.to:
            body["target_location"] = args.to
        if args.kind:
            body["kind"] = args.kind
        print(json.dumps(post_json("/commissions", body), ensure_ascii=False))
        return
    body = {"player_id": _player_id(), "commission_id": args.id, "action": args.mode}
    print(json.dumps(post_json("/commissions/act", body), ensure_ascii=False))


def cmd_intel(args):
    print(json.dumps(get_json("/intel", {"player_id": _player_id()}), ensure_ascii=False))


_VERSION_RE = re.compile(r"^[vV]?(\d+(?:\.\d+)*)")


def _vtuple(version: str):
    """版本号转元组：容忍前导 v 与后缀（v2.7.0 / 2.7.0-rc1），缺位补 0。

    服务端 /health 返回 v2.7.0 而 min_server_version 写 2.7.0，不剥离前导 v
    会让版本门永不生效（曾因此长期空转）。无法解析时返回 None，调用方按
    「版本未知」处理——健康检查失败本就不该阻断玩家。
    """
    match = _VERSION_RE.match(str(version).strip())
    if not match:
        return None
    parts = [int(part) for part in match.group(1).split(".")]
    return tuple(parts + [0] * max(0, 3 - len(parts)))


def cmd_version(args):
    """自查本地技能包是否最新：拉官网直链 zip，读包内 SKILL.md 的 version 比对。

    线上事实源=已部署的 zip 本身（nginx 静态直出），服务端零改动、无第二处版本号可漂移。
    """
    print(f"本地技能包版本：{__version__}")
    server = check_server_version(strict=False)
    if server:
        print(f"服务端版本：{server}")
    if args.offline:
        return
    try:
        r = _client.get(SKILL_ZIP_PATH)
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code}")
        if len(r.content) > 5_000_000:
            raise RuntimeError("响应体积不像技能包")
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            text = zf.read("SKILL.md").decode("utf-8")
        match = re.search(r"^version:\s*([0-9][\w.\-]*)\s*$", text, re.M)
        if not match:
            raise RuntimeError("包内 SKILL.md 缺 version 字段")
        remote = match.group(1).strip()
    except Exception as exc:
        print(f"（联网核对最新版失败：{exc}。可稍后重试，或加 --offline 只看本地版本）")
        return
    if remote == __version__:
        print(f"线上最新：{remote} —— 本地已是最新")
        return
    local_v, remote_v = _vtuple(__version__), _vtuple(remote)
    if local_v is not None and remote_v is not None and remote_v > local_v:
        print(
            f"线上最新：{remote} —— 本地不是最新！请重新下载技能包并整体替换本地文件"
            f"（{skill_zip_url(remote)}）；~/.ember-radio.json 里的身份不受影响，无需重新注册"
        )
    elif local_v is not None and remote_v is not None and local_v > remote_v:
        print(f"线上最新：{remote} —— 本地比线上还新（直链尚未更新，属正常过渡）")
    else:
        print(f"线上最新：{remote} —— 与本地不一致，建议重新下载：{skill_zip_url(remote)}")


def cmd_bug_report(args):
    """代玩家上报缺陷反馈：detail 用玩家原话蒸馏，client_version 自动带上本地版本。"""
    body = {
        "player_id": _player_id(),
        "title": args.title.strip(),
        "detail": args.detail.strip(),
        "client_version": __version__,
    }
    data = post_json("/bug-reports", body)
    if data.get("error"):
        # 业务拒绝（停用 403/限额 429/校验 422）的人话 detail 原样转述
        sys.stderr.write(f"{data.get('detail')}\n")
        raise SystemExit(1)
    print(json.dumps(data, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    rp = sub.add_parser("register", help="注册新玩家并保存到本机")
    rp.add_argument("--name", required=True, help="显示名")
    rp.add_argument("--gender", default=None, choices=["male", "female", "secret"], help="性别（默认 secret）")
    rp.add_argument("--district", default=None, help="指定出生区（消耗 1 份罐头；不填走出生盲盒）")
    rp.set_defaults(func=cmd_register)

    sp = sub.add_parser("start", help="进入当前地点的场景")
    sp.set_defaults(func=cmd_start)

    a = sub.add_parser("action", help="执行动作（自由文本或预设选项）")
    a.add_argument("--action-id", default=None)
    a.add_argument("--text", default=None)
    a.set_defaults(func=cmd_action)

    mp = sub.add_parser("move", help="移动到相邻地点（说名字即可）")
    mp.add_argument("--to", required=True, help="目的地名称或区名")
    mp.set_defaults(func=cmd_move)

    cp = sub.add_parser("map", help="城市地图（scope=building 看楼内平面图）")
    cp.add_argument("--scope", default=None, choices=["city", "building"])
    cp.set_defaults(func=cmd_map)

    np = sub.add_parser("nearby", help="本区最近活跃的人")
    np.set_defaults(func=cmd_nearby)

    bp = sub.add_parser("broadcast", help="发一条城市广播（每日 1 条，≤80 字）")
    bp.add_argument("--text", required=True)
    bp.set_defaults(func=cmd_broadcast)

    blp = sub.add_parser("broadcasts", help="读广播频道（city/remote/walkie/station）")
    blp.add_argument(
        "--channel", default=None, choices=["city", "remote", "walkie", "station"]
    )
    blp.set_defaults(func=cmd_broadcasts)

    rp = sub.add_parser("residual", help="守听残响（整点旧世界信号；每日 1 次）")
    rp.set_defaults(func=cmd_residual)

    pl = sub.add_parser("player", help="本地播放页地址（残响频率收听页）")
    pl.add_argument("--hour", default=None, help="报时音（如 15点），页面按世界观读法渲染")
    pl.add_argument("--titles", default=None, help="标题列表（英文逗号分隔，原样展示）")
    pl.set_defaults(func=cmd_player)

    xp = sub.add_parser("box", help="公共物资箱（需站在箱子节点）")
    xp.add_argument("--mode", default="show", choices=["show", "exchange", "donate"])
    xp.add_argument("--item", default=None, help="物品 id（exchange/donate 时必填）")
    xp.set_defaults(func=cmd_box)

    r = sub.add_parser("recap", help="离线期间发生了什么")
    r.set_defaults(func=cmd_recap)

    qsp = sub.add_parser("quests", help="托付清单：进行中/可交割/已交割")
    qsp.set_defaults(func=cmd_quests)

    qa = sub.add_parser("quest-accept", help="接下一桩托付（本版多为自动派发）")
    qa.add_argument("--id", required=True, help="托付 id")
    qa.set_defaults(func=cmd_quest_accept)

    qti = sub.add_parser("quest-turn-in", help="交割托付领回礼（办妥步骤后）")
    qti.add_argument("--id", required=True, help="托付 id")
    qti.set_defaults(func=cmd_quest_turn_in)

    cm = sub.add_parser("commission", help="委托板：list/create/accept/deliver/settle/cancel")
    cm.add_argument("--mode", required=True,
                    choices=["list", "create", "accept", "deliver", "settle", "cancel"])
    cm.add_argument("--title", default=None, help="create：一句话说明（≤40 字）")
    cm.add_argument("--item", default=None, help="create：回礼物品 id")
    cm.add_argument("--count", default=None, help="create：回礼数量（默认 1）")
    cm.add_argument("--to", default=None, help="create：目标地点（可选）")
    cm.add_argument("--kind", default=None, help="create：类型标签（可选）")
    cm.add_argument("--id", default=None, help="accept/deliver/settle/cancel：委托 id")
    cm.set_defaults(func=cmd_commission)

    ip = sub.add_parser("intel", help="本区与全城的在传情报（带来源与可信度）")
    ip.set_defaults(func=cmd_intel)

    vp = sub.add_parser("version", help="查看本地技能包版本并核对线上最新")
    vp.add_argument("--offline", action="store_true", help="只看本地版本，不联网")
    vp.set_defaults(func=cmd_version)

    bp = sub.add_parser("bug-report", help="上报缺陷反馈给电台管理员")
    bp.add_argument("--title", required=True, help="一句话概括（≤60 字）")
    bp.add_argument("--detail", required=True, help="现象/期望/复现步骤，用玩家原话蒸馏（≤2000 字）")
    bp.set_defaults(func=cmd_bug_report)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
