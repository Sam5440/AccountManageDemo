from nonebot import *

from .SqlClass import *
from .f import *


@on_command('农场充值', only_to_me=False)
async def key_use(session):
    qq = session.event.user_id
    key = session.get("key", prompt="请输入KEY")
    state, key_info = check_card(key)
    if state != "该卡密应使用[农场充值]":
        await session.finish(state)
    # 卡密检查完成，开始充值 ↑
    uid = session.get("uid", prompt=f"请输入UID,卡密为套餐{str(key_info.farm_type)}")
    try:
        uid_info = FarmUser.get(FarmUser.uid == uid)
        expires_time = uid_info.expires
    except:
        expires_time = 0
    new_time, now = new_time_calculate(key_info.add_time, expires_time)

    if expires_time != 0:
        if uid_info.farm_type == key_info.farm_type:
            if delete_key(key, qq, now):
                FarmUser.update({FarmUser.expires: new_time}).where(FarmUser.uid == uid).execute()
                await session.finish(f'续费成功')
            else:
                admin_log(key, qq)
                await session.finish(f'违规使用')
        else:
            await session.finish(f'与首次购买套餐{str(uid_info.farm_type)}不一致，请联系发卡方更换，或使用删除农场，删除后重新购买')
    # 续费操作完成
    else:
        try:
            account_info = get_min_farm(key_info.farm_type, key_info.owner)  # 获得最小编号农场
            # account_info = FarmAccount.get(FarmAccount.farm_type == key_info.farm_type,
            #                                FarmAccount.owner == key_info.owner)
            FarmAccount.delete().where(FarmAccount.id == account_info.id).execute()
        except:
            await session.finish(f'套餐{str(key_info.farm_type)}没有货了，请联系发卡方')
        if delete_key(key, qq, now):
            new_farm_user_add(qq, uid, account_info.clanname, account_info.account, account_info.password,
                              key_info.farm_type, new_time, key_info.owner)
            await session.finish(f'创建成功，在{account_info.clanname}，请使用 农场邀我 加入')
        else:
            admin_log(key, qq)
            await session.finish(f'违规使用')


@on_command('好友充值', only_to_me=False)
async def key_use_friend(session):
    qq = session.event.user_id
    key = session.get("key", prompt="请输入KEY")
    state, key_info = check_card(key)
    if state != "该卡密应使用[好友充值]":
        await session.finish(state)
    uid = session.get("uid", prompt=f"请输入UID")
    try:
        uid_info = FriendFarm.get(FriendFarm.uid == uid)
        expires_time = uid_info.expires
    except:
        expires_time = 0
    new_time, now = new_time_calculate(key_info.add_time, expires_time)

    if expires_time != 0:
        if delete_key(key, qq, now):
            FriendFarm.update({FriendFarm.expires: new_time}).where(FriendFarm.uid == uid).execute()
            await session.finish(f'续费成功')
        else:
            admin_log(key, qq)
            await session.finish(f'违规使用')
    else:
        try:
            friend_count()
            FriendSlave_info = FriendSlave.get(FriendSlave.friend_num < 10, FriendSlave.owner == key_info.owner)
        except:
            await session.finish(f'好友农场没有货了，请联系发卡方')
        if delete_key(key, qq, now):
            new_friend_user_add(qq, uid, FriendSlave_info.group, new_time, key_info.owner)
            friend_count()
            await session.finish(f'创建成功，在F:{str(FriendSlave_info.group)}，请使用 好友加我 加入')
        else:
            admin_log(key, qq)
            await session.finish(f'违规使用')


@on_command('查询农场卡密', only_to_me=False)
async def key_info_get(session):
    key = session.get("key", prompt="请输入KEY")
    state, key_info = check_card(key)
    msg = "卡密未找到"
    if state != msg:
        msg = f"卡密状态为：{state}\n" \
              f"套餐{key_info.farm_type}\n" \
              f"时效{key_info.add_time}\n" \
              f"发卡人{key_info.owner}\n" \
              f"感谢使用"
    await session.finish(msg)


def new_time_calculate(add_time, old_time):
    now = int(time.time())
    if old_time > now:
        new_time = old_time + add_time
    else:
        new_time = now + add_time
    return new_time, now


def check_card(key):
    """
    返回卡密的state
    """
    try:
        key_info = FarmKeys.get(FarmKeys.key == key)
        if key_info.is_used:
            return "卡密已使用", key_info
    except:
        return "卡密未找到", 0
    state = "该卡密应使用[好友充值]" \
        if key_info.farm_type == 12 else "该卡密应使用[农场充值]"
    return state, key_info
