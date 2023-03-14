from nonebot import on_command

import hoshino
from .f import *


@on_command("查询好友信息", aliases=("好友时间", "好友农场时间"), only_to_me=False)
async def friend_time_check(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    text, num, uids = get_uids_friend(qq)
    if num > 1:
        n = session.get("n", prompt=text)
    else:
        n = str(1)
    if str(num) >= n > "0":
        user = get_n(uids, n)
        info, user = get_user_info(user.uid, "friend")
    else:
        await session.finish(f"[CQ:at,qq={str(qq)}]输入错误或未查询到信息")
    await session.finish(info)


global friend_count_api, friend_last_api
friend_last_api = 0
friend_count_api = 0
friend_await_api = 30


@on_command("添加好友", aliases=("好友加我", "加好友"), only_to_me=False)
async def friend_add(session):
    """
    按照数据库标记群组添加好友
    """
    # if session.event.group_id == 1159681413 and session.event.user_id not in hoshino.config.SUPERUSERS:
    #     await session.finish('正在后台处理中，指令不可用,如果真的急的话加群790121399直接添加')

    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入qq")
        qq = cqcode_to_QQ(qq_raw)
    text, num, uids = get_uids_friend(qq)
    # # # # # # # # # # # # # # #
    if num > 1:
        n = session.get("n", prompt=text)
    else:
        n = str(1)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # 因为每一次session.get都会重新执行一遍函数，所以说冷却时间判断只能直接放在api的最前面
    global friend_count_api, friend_last_api, friend_await_api
    now_time = int(time.time())
    if (
        friend_last_api + friend_await_api < now_time
        or session.event.group_id == 790121399
        or session.event.user_id in hoshino.config.SUPERUSERS
    ):
        friend_last_api = now_time
    else:
        await session.finish(f"请{friend_last_api+friend_await_api-now_time}s后再添加")
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    if str(num) >= n > "0":
        num = 0
        for k in uids:
            num = num + 1
            if n == str(num):
                if friend_count_api <= 999:
                    get_slaves_to_control(k.slaves_group, k.uid, "request")
                    friend_count_api += 1
                else:
                    print(f"friend_count_api----{friend_count_api} is Max")
                    await session.finish("登录设备已经最大，请联系管理员重启")
            print(f"friend_count_api----{friend_count_api}")
    else:
        await session.finish(f"[CQ:at,qq={qq}]输入错误或未查询到信息")
    await session.finish(f"添加成功:{friend_count_api}")


def get_uids_friend(qq):
    """
    获得这个qq的全部uid
    其中text是uids的json文本，num是uid数量，uids返回列表，有这些uid的详细信息
    text, num, uids = get_uids(qq)
    """
    uids = FriendFarm.select().where(FriendFarm.qq == qq)
    uid_list = []
    num = 0
    for k in uids:
        num = num + 1
        uid = f"{str(num)}:{str(k.uid)}(好友)\n"
        uid_list.append(uid)
    text = f"[CQ:at,qq={qq}],请回复需要选择的UID序号即可：）\n" + "\n".join(uid_list)
    num = int(num)
    return text, num, uids


def get_slaves_to_control(group, uid, state):
    """
    通过group和state指定来对uid执行命令
    调用friend_api
    """
    if state == "remove":
        n = -1
    elif state == "request":
        n = 1
    else:
        n = 0
    slaves = FriendSlave.select().where(FriendSlave.group == group)
    for k in slaves:
        print(response_to_url(friend_api(k.account, k.password, uid, state)))
    for k in slaves:
        n_new = k.friend_num + n
        q = FriendSlave.update({FriendSlave.friend_num: n_new}).where(
            FriendSlave.account == k.account
        )
        q.execute()
    return 0


def friend_api(account, password, uid, state):
    """
    通过api 发送账号密码操作好友
    """
    headers = {
        "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
        "Content-Type": "application/json",
    }
    data = (
        '{ "account": "'
        + account
        + '", "password": "'
        + password
        + '", "target_viewer_id":'
        + uid
        + " }"
    )
    log(data)
    response = requests.post(
        f"https://example.com/friend/{state}", headers=headers, data=data
    )
    resp = response.text
    return resp
