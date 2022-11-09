import nonebot
from nonebot import on_command

import hoshino
from .f import *

global farm_count_api, farm_last_api, farm_awawi
farm_last_api = 0
farm_count_api = 0
farm_await_api = 1  # 等待时间


@on_command("农场邀我", only_to_me=False)
async def invite_me(session):
    global farm_count_api, farm_last_api, farm_await_api
    now_time = int(time.time())

    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    text, num, uids = get_uids(qq)
    if num > 1:
        n = session.get("n", prompt=text)
        n = 0 if n == "全部选择" else int(n)
    else:
        n = 1
    ##################################################
    # 因为每一次session.get都会重新执行一遍函数，所以说冷却时间判断只能直接放在api的最前面
    if (
        farm_last_api + farm_await_api < now_time
        or session.event.group_id == 790121399
        or session.event.user_id in hoshino.config.SUPERUSERS
    ):
        farm_last_api = now_time
    else:
        await session.finish(
            f"[CQ:at,qq={qq}]请{farm_last_api+farm_await_api-now_time}s后再添加"
        )
    ####################################################
    if num >= n >= 0:
        text = await invite(uids, session.event.user_id, n)
    else:
        await session.finish(f"[CQ:at,qq={qq}]输入错误")
    farm_count_api = farm_count_api + 1
    text = "ID:" + str(farm_count_api) + "- \n" + text
    await session.finish(text)


null_clan_json = """{"info":{"list":[]}}\n"""
ban_clan_name = r'{"info":"\u5185\u5bb9\u5305\u542b\u654f\u611f\u8bcd"}' + "\n"


@on_command("农场改名", only_to_me=False)
async def change_clan(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    name = session.get("name", prompt="请输入你的新农场的名字")
    # farm_search_clan("登录")
    search_json = str(check(farm_search_clan(name), True, 1))
    text = str_image_generate(f"可能重名，\n不甘心的话再试试吧\n")
    if search_json != null_clan_json:
        await session.finish(text)
    text, num, uids = get_uids(qq)
    if num > 1:
        n = session.get("n", prompt=text)
        if n == "全部选择":
            await session.finish("全部选择不可用")
    else:
        n = str(1)
    user = get_n(uids, n)
    response = save_response_info(
        user.uid, farm_change_clan_name(user.account, user.password, name)
    )
    qrcode_img = response_to_url(response, to_qrcode=True)
    await session.send(f"[CQ:at,qq={session.event.user_id}] 正在改名，预计需要60秒 {qrcode_img} ")
    await asyncio.sleep(60)
    state = str(check(response, True))
    if state == ban_clan_name:
        await session.finish(f"[CQ:at,qq={session.event.user_id}] 您的名字包含违禁词")
    try:
        state_json = json.loads(state)
        clan_id = state_json["info"]
        info, get_name = farm_search_clanid(num_text_to_num(clan_id))
    except:
        await session.finish("未知错误,请带着刚刚的二维码私聊管理员")
    if name != get_name:
        await session.finish(f"[CQ:at,qq={session.event.user_id}] 未知错误")
    text = f"新的名字:[{name}]\n旧名字:[{user.clanbattle_name}]\n"
    text_image = update_user_info_text(user, text)
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=1234567890, message=text_image)
    # 更新新名字
    FarmUser.update({FarmUser.clanbattle_name: name}).where(
        FarmUser.uid == user.uid
    ).execute()
    await session.finish(
        f"[CQ:at,qq={session.event.user_id}] 改名{get_name}完成完成，发送[检查状态]查询状态，如果不是成功改名请联系管理"
    )


@on_command("农场创建", only_to_me=False)
async def create_clan(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    name = session.get("name", prompt="请输入你的农场的名字")
    search_json = str(check(farm_search_clan(name), True, 1))
    text = str_image_generate(f"可能重名，\n不甘心的话再试试吧\n")
    if search_json != null_clan_json:
        await session.finish(text)
    try:
        text, num, uids = get_uids(qq)
    except:
        await session.finish("没有找到你的信息")
    if num > 1:
        n = session.get("n", prompt=text)
        if n == "全部选择":
            await session.finish("全部选择不可用")
    else:
        n = str(1)
    user = get_n(uids, n)
    response = save_response_info(
        user.uid, farm_clan_create(user.account, user.password, name)
    )
    qrcode_img = response_to_url(response, to_qrcode=True)
    await session.send(f"[CQ:at,qq={session.event.user_id}] 正在创建，预计需要60秒 {qrcode_img} ")
    await asyncio.sleep(60)
    state = str(check(response, True))
    if state == ban_clan_name:
        await session.finish(f"[CQ:at,qq={session.event.user_id}] 您的名字包含违禁词")
    try:
        state_json = json.loads(state)
        clan_id = state_json["info"]["clan_id"]
        info, get_name = farm_search_clanid(num_text_to_num(clan_id))
    except:
        await session.finish("未知错误,请带着刚刚的二维码私聊管理员")
    if name != get_name:
        await session.finish(f"[CQ:at,qq={session.event.user_id}] 未知错误")
    text = f"新的名字:[{name}]\n旧名字:[{user.clanbattle_name}]\n"
    text_image = update_user_info_text(user, text)
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=1234567890, message=text_image)
    FarmUser.update({FarmUser.clanbattle_name: name}).where(
        FarmUser.uid == user.uid
    ).execute()
    await session.finish(
        f"[CQ:at,qq={session.event.user_id}] 创建{get_name}完成，发送[检查状态]查询状态，如果不是成功改名请联系管理"
    )

@on_command("农场强制改名", only_to_me=False)
async def change_clan_force(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    name = session.get("name", prompt="请输入你的新农场的名字")
    # search_json = str(check(farm_search_clan(name), True, 1))
    # text = str_image_generate(f"可能重名，\n不甘心的话再试试吧\n")
    # if search_json != null_clan_json:
    #     await session.finish(text)
    text, num, uids = get_uids(qq)
    if num > 1:
        n = session.get("n", prompt=text)
        if n == "全部选择":
            await session.finish("全部选择不可用")
    else:
        n = str(1)
    user = get_n(uids, n)
    text = f"(强制改名)新的名字:[{name}]\n旧名字:[{user.clanbattle_name}]\n"
    text_image = update_user_info_text(user, text)
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=1234567890, message=text_image)
    # 更新新名字
    FarmUser.update({FarmUser.clanbattle_name: name}).where(
        FarmUser.id == user.id
    ).execute()
    await session.finish(
        f"[CQ:at,qq={session.event.user_id}] 改名{name}完成,请确认名字正确.否则农场将无法加入农奴"
    )