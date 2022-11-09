from nonebot import on_command

import hoshino
from .f import *


@on_command('查询农场信息', aliases=('查询时间', '查询到期时间'), only_to_me=False)
async def farm_check(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    text, num, uids = get_uids(qq)
    if num > 1:
        n = session.get('n', prompt=text)
        if n == "全部选择":
            await session.finish("全部选择不可用")
    else:
        n = str(1)
    if num >= int(n) > 0:
        user = get_n(uids, n)
        info, user = get_user_info(user.uid)
    else:
        await session.finish(f'[CQ:at,qq={qq}]输入错误或未查询到信息')
    await session.finish(info)


@on_command('检查状态', aliases=('检查踢出状态', '检查邀请状态', '查询状态'), only_to_me=False)
async def state_check(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    state = "1"
    text, num, uids = get_uids(qq)
    if num > 1:
        n = session.get('n', prompt=text)
        if n == "全部选择":
            await session.finish("全部选择不可用")
    else:
        n = str(1)
    if num >= int(n) > 0:
        k = get_n(uids, n)
    else:
        await session.finish(f'[CQ:at,qq={qq}]输入错误或未查询到信息')
    try:
        state = str(check(k.state))
    except:
        log(n)
    await session.finish(f'[CQ:at,qq={k.qq}]\n队伍状态:{state}')
