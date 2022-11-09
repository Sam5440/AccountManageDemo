import random

from nonebot import on_command

from hoshino import util


@on_command('抽奖', only_to_me=True)
async def kou_ball_draw(session):
    ctx = session.ctx
    user_id = session.event.user_id
    msg_from = str(user_id)
    msg_from += f'@[群:{ctx["group_id"]}]'
    kou_ball_time = random.randint(60, 360)
    await session.send(f"哼，你抽奖，我抽你，给你塞{kou_ball_time}秒口球", at_sender=True)
    await util.silence(session.ctx, kou_ball_time)
