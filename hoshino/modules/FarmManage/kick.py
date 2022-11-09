from nonebot import on_command

import hoshino
from .f import *


@on_command('我要踢出农场所有人呀', only_to_me=False)
async def kick_all(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f'你踢nm呢')
        return
    msg = f"※请确认后，回复“确认”来完成本次操作。"
    ensure = session.get("ensure", prompt=msg)
    if ensure != "确认":
        session.finish("已取消")
    user = FarmUser.select().where(FarmUser.id >= 0)
    num = 0
    for k in user:
        if str(k.state) == "1":
            log(num)
            response = farm_api(k.account, k.password, k.uid, "kick")
            log(response)
            num = num + 1
            save_response_info(k.uid, response)
            time.sleep(19)
            log(check(response))
    await session.finish(f'踢了{num}人')


@on_command('农场踢我', only_to_me=False)
async def kick_me(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    text, num, uids = get_uids(qq)
    if num > 1:
        n = session.get('n', prompt=text)
        n = 0 if n == "全部选择" else int(n)
    else:
        n = 1
    if num >= n >= 0:
        text = kick(uids, qq, n)
    else:
        await session.finish(f'[CQ:at,qq={qq}]输入错误')
    await session.finish(text)


@on_command('踢野人', only_to_me=False)
async def kick_sb(session):
    """
    等待改为get n
    """
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
    text = "错误"
    if num >= int(n) > 0:
        num = 0
        for k in uids:
            num = num + 1
            if n == str(num) or n == "全部选择":
                uid = session.get('uid', prompt="输入你要踢出的UID")
                try:
                    response = farm_api(k.account, k.password, uid, "kick")
                    save_response_info(k.uid, response)
                    text = f'[CQ:at,qq={qq}]正在踢出，请稍后使用 检查踢出状态 查询(一小时内有效）'
                except:
                    text = f'[CQ:at,qq={qq}]啊哦~有点问题,再试试吧'
    else:
        await session.finish(f'[CQ:at,qq={session.event.user_id}]输入错误')
    await session.finish(text)
