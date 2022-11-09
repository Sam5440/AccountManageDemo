import re

from nonebot import on_command

import hoshino
from .f import *


@on_command('生成农场兑换券', only_to_me=False)
async def creat_key_chat(session):
    # 权限检查
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('？？？你也配？')
        return
    # 是否为私聊
    '''if session.event.detail_type == 'group':
        # 群聊生成卡密你可真是个小天才
        await session.finish('群聊生成nm')
        return'''
    # 提取关键字
    pattern = re.compile(r'^(\d{1,2})\*(\d{1,5})\*(\d{1,2})$')
    origin = session.current_arg.strip()
    m = pattern.match(origin)
    if m is None:
        await session.finish('请按照“生成农场兑换券 类型*天数*数量”进行输入！')
    farmtype = int(m.group(1))
    addtimes = int(m.group(2)) * 86400
    key_num = int(m.group(3))
    # 检查num
    if key_num <= 0:
        await session.finish('生成成功)bushi')
    # 生成卡密
    key_list = []
    for _ in range(key_num):
        new_key = add_key(farmtype, session.event.user_id, addtimes)
        hoshino.logger.info(f'已生成新兑换券{new_key}, 类型:{farmtype}')
        key_list.append(new_key)
    await session.send(f'已生成{key_num}份套餐{farmtype}的卡密：\n' + '\n'.join(key_list))
