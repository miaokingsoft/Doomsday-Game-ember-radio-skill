"""余烬电台 Octop 插件入口（skill 型壳）。

Octop 框架 import 本文件后只调用 setup(ctx)：skill 型插件把 skills/<名字>/
SKILL.md（连同同目录的 references、scripts）同步进 Agent 工作区，玩法全部由
技能包 client.py 走服务端 API 完成——本壳不注册任何工具或中间件。
"""
from __future__ import annotations


def setup(ctx) -> None:
    # 防呆：ctx.skills 是 skill 型插件的挂载接口；若当前 Octop 版本没有
    # 该接口，宁可在此报人话错误，也不要静默装了个空壳。
    if not hasattr(ctx, "skills"):
        raise RuntimeError(
            "当前 Octop 的插件上下文没有 skills() 接口：请核对你安装的 "
            "Octop 版本是否支持 kind: skill 型插件（本壳只做技能同步，"
            "不做工具型封装）"
        )
    ctx.skills("skills")
