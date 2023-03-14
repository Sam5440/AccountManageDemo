#import
import os
import anyio
from nonebot import on_command

import hoshino
from .f import *
from .friend import get_slaves_to_control
from .mail import *
from .ttf import qrcode_url


@on_command("更改全部时间", only_to_me=False)
async def admin_farm_time_change_all(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"无权限")
        return
    begin_time = session.get("begin_time", prompt="请输入开始时间，如2022-03-16 ")
    begin_time = time_to_int_val(begin_time)
    end_time = session.get("end_time", prompt="请输入结束时间，如2022-03-22")
    end_time = time_to_int_val(end_time)
    change_time = int(session.get("change_time", prompt="请输入变更时间(天)，如果为-负数，请使用英文负号"))
    change_time = change_time * 6
    msg = f"""※注意！！！变更前如果条件尽量备份数据库\n※你正在变更\n从{str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(begin_time)))}\n到{str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))}\n到期的用户时间增加{str(round(change_time / 86000, 1))}天\n※请确认后，回复“确认”来完成本次操作。"""
    ensure = session.get("ensure", prompt=msg)
    if ensure != "确认":
        session.finish("已取消")
    admin_log(msg, session.event.user_id)
    num = time_change(begin_time, end_time, change_time)
    admin_log(f"用户{session.event.user_id}变更时间完成", session.event.user_id)
    await session.finish(f"完成变更{str(num)}人")


@on_command("更改state", only_to_me=False)
async def admin_change_state(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"无权限")
        return
    response = session.get("change_time", prompt="请输入变更后state，此操作会更改全部state")
    user = FarmUser.select().where(FarmUser.id >= 0)
    msg = f"变跟state为{response}"
    admin_log(msg, session.event.user_id)
    for k in user:
        save_response_info(k.uid, response)
    admin_log("变更state完成", session.event.user_id)
    await session.finish(f"完成变更")


@on_command("好友清理", only_to_me=False)
async def friend_clean_all(session):
    """
    清理过期好友
    """
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    admin_log("好友清理", session.event.user_id)
    user = FriendFarm.select().where(FriendFarm.id >= 0)
    num = 0
    remove_list = []
    now = int(time.time())
    for k in user:
        if k.expires < now:
            get_slaves_to_control(k.slaves_group, k.uid, "remove")
            num = num + 1
            FriendFarm.delete().where(FriendFarm.uid == k.uid).execute()
            text = f"[{num}:{k.uid}({k.qq})]"
            log(text)
            remove_list.append(text)
    admin_log(f"好友清理{num}人success", session.event.user_id)
    try:
        mail(session.event.user_id, "\n".join(remove_list))
    except:
        await session.finish(f"(邮件发送失败)清理{num}人" + "\n".join(remove_list))
    await session.finish(f"清理{num}人" + "\n".join(remove_list))


# @on_command('时间戳换算', only_to_me=False)
# async def timeline_to_data(session):
#     if session.event.user_id not in hoshino.config.SUPERUSERS:
#         await session.finish(f'滚啊')
#     admin_log("时间戳换算", session.event.user_id)
#     user = FriendFarm.select().where(FriendFarm.id >= 0)
#     for k in user:
#         if k.expires < now:
#             get_slaves_to_control(k.slaves_group, k.uid, "remove")
#             num = num + 1
#             FriendFarm.delete().where(FriendFarm.uid == k.uid).execute()
#             log(num)
#             log(k.uid)
#     admin_log(f"时间戳换算", session.event.user_id)
#     await session.finish(f'时间戳换算ok')


@on_command("农场清理", only_to_me=False)
async def farm_clean_all(session):
    """
    清理过期农场老板
    """
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    # # # # # # # # # # # # #
    admin_log("农场清理", session.event.user_id)
    user = FarmUser.select().where(FarmUser.id >= 0)
    num = 0
    now = int(time.time())
    kicking_list = []
    kicked_list = []
    check_list = []
    for k in user:
        if 1 < k.expires - now < 100000:
            kicking_list.append(
                f"[CQ:at,qq={k.qq}]你UID{k.uid}的农场时间只有"
                f"{str(round((k.expires - int(time.time())) / 86400, 1))}天了"
            )
        if k.expires < now:
            num = num + 1
            response = farm_api(k.account, k.password, k.uid, "kick")
            # save_response_info(k.uid, response)
            check_list.append([k.clanbattle_name, k.uid, response])
            p = FarmAccount(
                clanname=k.clanbattle_name,
                account=k.account,
                password=k.password,
                farm_type=k.farm_type,
                owner=k.owner,
                not_work=0,
            )
            p.save()
            FarmUser.delete().where(FarmUser.uid == k.uid).execute()
            kicked_list.append(f"[CQ:at,qq={k.qq}]你UID{k.uid}过期啦")
    check_await_time = len(check_list)*25+25
    msg = (
        f"({check_await_time}s后检查踢出状态)到期提醒:\n"
        + "\n".join(kicking_list)
        + "\n---到期名单---"
        + "\n".join(kicked_list)
    )
    admin_log(msg, session.event.user_id)
    try:
        mail(session.event.user_id, msg)
    except:
        msg += "(邮件发送失败)"
    await session.send(msg)
    # check kick state
    ## print(len(check_list))
    await anyio.sleep(check_await_time)
    check_state = []
    for check_now in check_list:
        check_msg = f"农场【{check_now[0]}[{check_now[1]}]-{check(check_now[2])}】"
        check_state.append(check_msg)
    msg = "check_msg:\n" + "\n".join(check_state)
    await session.finish(msg)


# @on_command('变更农场时间', only_to_me=False)
# async def admin_farm_time_change(session):
#     if session.event.user_id not in hoshino.config.SUPERUSERS:
#         await session.finish(f'无权限')
#         return
#     uid = session.get("uid", prompt="请输入操作UID")
#     info, user = get_user_info(uid)
#     change_time = int(session.get("change_time", prompt="请输入增加时间(天)，如果为-负数，请使用英文负号"))
#     change_time = change_time * 86400
#     msg = f"""※为此用户时间增加{str(round(change_time / 86400, 1))}天\n※请确认后，回复“确认”来完成本次操作。\n{info}"""
#     log_msg = f"""※为此{uid}用户时间增加{str(round(change_time / 86400, 1))}天"""
#     ensure = session.get("ensure", prompt=msg)
#     if ensure != "确认":
#         session.finish("已取消")
#     new_time = user.expires + change_time
#     q = FarmUser.update({FarmUser.expires: new_time}).where(FarmUser.uid == uid)
#     q.execute()
#     admin_log(f"{log_msg}", session.event.user_id)
#     info, user = get_user_info(uid)
#     await session.finish(f'完成变更{info}')


@on_command("变更农场时间", only_to_me=False)
async def admin_farm_time_change(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"无权限")
        return
    msg, log_msg, carry_list = "※请确认后，回复“确认”来完成本次操作。\n", "", []
    uids_info_raw = session.get(
        "uids_time_raw", prompt="请输入uid@时间，换行切换，如1234567890123@100 "
    )
    info_list = uids_rawtext_to_list(uids_info_raw)
    for uid_info in info_list:
        uid, change_time = uid_info[0], int(uid_info[1])
        info, user = get_user_info(uid)
        change_time = change_time * 86400
        msg += f"""{info}※为上方↑用户时间增加{str(round(change_time / 86400, 1))}天\n"""
        log_msg += f"""农场{uid}+{str(round(change_time / 86400, 1))}天"""
        new_time = user.expires + change_time
        carry_list += [
            [
                uid,
                FarmUser.update({FarmUser.expires: new_time}).where(
                    FarmUser.uid == uid
                ),
            ]
        ]
    ensure = session.get("ensure", prompt=msg)
    if ensure != "确认":
        await session.finish("已取消")
    msg = ""
    for carry in carry_list:
        carry[1].execute()
        info, user = get_user_info(carry[0])
        msg += info
    admin_log(f"{log_msg}", session.event.user_id)
    await session.finish(f"完成变更{msg}")


# @on_command('变更好友时间', only_to_me=False)
# async def admin_friend_time_change(session):
#     if session.event.user_id not in hoshino.config.SUPERUSERS:
#         await session.finish(f'无权限')
#         return
#     uid = session.get("uid", prompt="请输入操作UID")
#     info, user = get_user_info(uid, "friend")
#     change_time = int(session.get("change_time", prompt="请输入增加时间(天)，如果为-负数，请使用英文负号"))
#     change_time = change_time * 86400
#     msg = f"""※为此用户时间增加{str(round(change_time / 86400, 1))}天\n※请确认后，回复“确认”来完成本次操作。\n{info}"""
#     log_msg = f"""※为此{uid}用户时间增加{str(round(change_time / 86400, 1))}天"""
#     ensure = session.get("ensure", prompt=msg)
#     if ensure != "确认":
#         session.finish("已取消")
#     new_time = user.expires + change_time
#     q = FriendFarm.update({FriendFarm.expires: new_time}).where(FriendFarm.uid == uid)
#     q.execute()
#     admin_log(f"{log_msg}", session.event.user_id)
#     info, user = get_user_info(uid, "friend")
#     await session.finish(f'完成变更{info}')


@on_command("变更好友时间", only_to_me=False)
async def admin_friend_time_change(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"无权限")
        return
    msg, log_msg, carry_list = "※请确认后，回复“确认”来完成本次操作。\n", "", []
    uids_info_raw = session.get(
        "uids_time_raw", prompt="请输入uid@时间，换行切换，如1234567890123@100 "
    )
    info_list = uids_rawtext_to_list(uids_info_raw)
    for uid_info in info_list:
        uid, change_time = uid_info[0], int(uid_info[1])
        info, user = get_user_info(uid, "friend")
        change_time = change_time * 86400
        msg += f"""{info}※为上方↑用户时间增加{str(round(change_time / 86400, 1))}天\n"""
        log_msg += f"""好友{uid}+{str(round(change_time / 86400, 1))}天"""
        new_time = user.expires + change_time
        carry_list += [
            [
                uid,
                FriendFarm.update({FriendFarm.expires: new_time}).where(
                    FriendFarm.uid == uid
                ),
            ]
        ]
    ensure = session.get("ensure", prompt=msg)
    if ensure != "确认":
        session.finish("已取消")
    # msg += '-'*50
    msg = ""
    for carry in carry_list:
        carry[1].execute()
        info, user = get_user_info(carry[0], "friend")
        msg += info
    admin_log(f"{log_msg}", session.event.user_id)
    await session.finish(f"完成变更\n{msg}")


@on_command("添加农场用户", only_to_me=False)
async def admin_add_farm_user(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"无权限")
    owner_ = session.event.user_id
    msg, log_msg, carry_list = "", "", []
    uids_info_raw = session.get(
        "uids_time_raw",
        prompt="请输入qq@uid@农场名@时间，换行切换，\n如12345@1234567890123@捣蛋屋111@2022-03-16",
    )
    info_list = uids_rawtext_to_list(uids_info_raw)
    for uid_info in info_list:
        clanbattle_name_, str_time = uid_info[2], uid_info[3]
        try:
            n = "农场未找到"
            farm_info = FarmAccount.get(FarmAccount.clanname == clanbattle_name_)
            n = "时间错误"
            expires_ = time_to_int_val(str(str_time))
            n = "未知错误"
        except:
            await session.finish(f"{n} 信息：{clanbattle_name_}/{str_time}")
    for uid_info in info_list:
        qq_, uid_, clanbattle_name_, expires_ = (
            cqcode_to_QQ(uid_info[0]),
            uid_info[1],
            uid_info[2],
            time_to_int_val(uid_info[3]),
        )
        try:
            farm_info = FarmAccount.get(FarmAccount.clanname == clanbattle_name_)
            account_ = farm_info.account
            password_ = farm_info.password
            farm_type_ = farm_info.farm_type
            FarmAccount.delete().where(FarmAccount.id == farm_info.id).execute()
            new_farm_user_add(
                qq_,
                uid_,
                clanbattle_name_,
                account_,
                password_,
                farm_type_,
                expires_,
                owner_,
            )
            info, user = get_user_info(uid_)
        except:
            info = f"在添加{uid_}/{clanbattle_name_}的时候发生错误，请检查该uid是否添加"
            await session.send(info)
        msg += info
    await session.send("完成")
    await session.finish(f"{msg}")


@on_command("添加好友用户", only_to_me=False)
async def admin_add_friend_user(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"无权限")
    owner_ = session.event.user_id
    msg, log_msg, carry_list = "", "", []
    uids_info_raw = session.get(
        "uids_time_raw",
        prompt="请输入qq@uid@好丽友几@时间，换行切换，\n如12345@1234567890123@1@2022-03-16",
    )
    info_list = uids_rawtext_to_list(uids_info_raw)
    for uid_info in info_list:
        try:
            expires_test = time_to_int_val(uid_info[3])
        except:
            await session.finish(f"时间转换失败或农场名未找到 信息：{uid_info[1]}/{uid_info[2]}")
    for uid_info in info_list:
        qq_, uid_, slaves_group_, expires_ = (
            cqcode_to_QQ(uid_info[0]),
            uid_info[1],
            uid_info[2],
            time_to_int_val(uid_info[3]),
        )
        try:
            new_friend_user_add(qq_, uid_, slaves_group_, expires_, owner_)
            info, user = get_user_info(uid_, "friend")
        except:
            info = f"在添加uid{uid_}的时候发生错误，请检查该uid是否添加"
            await session.send(info)
        msg += info
    await session.send("完成")
    await session.finish(f"{msg}")


@on_command("换场", only_to_me=False)
async def change_farm(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    uid = session.get("uid", prompt=f"enter uid ")
    try:
        info, k = get_user_info(uid)
    except:
        await session.finish("uid is not found")
    # new_type = session.get("farm_type", prompt=f"请输入新农场套餐，时间不变。\n{info}")
    # try:
    #     account_info = get_min_farm(new_type)
    #     FarmAccount.delete().where(FarmAccount.id == account_info.id).execute()
    # except:
    #     await session.finish(f'套餐{str(new_type)}没有货了')
    clanbattle_name_ = session.get("clanbattle_name_", prompt="请输入用户新农场名字")
    print(clanbattle_name_)
    try:
        account_info = FarmAccount.get(FarmAccount.clanname == clanbattle_name_)
        FarmAccount.delete().where(FarmAccount.id == account_info.id).execute()
    except:
        await session.finish("404 not  fount")
    response = farm_api(k.account, k.password, k.uid, "kick")
    # response_json = json.loads(response)
    # uuid = response_json["uuid"]
    # qrcode_img = qrcode_url(f'https://example.com/check/{uuid}')
    p = FarmAccount(
        clanname=k.clanbattle_name,
        account=k.account,
        password=k.password,
        farm_type=k.farm_type,
        owner=k.owner,
        not_work=0,
    )
    p.save()
    FarmUser.update(
        {
            FarmUser.clanbattle_name: account_info.clanname,
            FarmUser.account: account_info.account,
            FarmUser.password: account_info.password,
            FarmUser.farm_type: account_info.farm_type,
        }
    ).where(FarmUser.uid == uid).execute()
    msg = f"{response_to_url(response,to_qrcode=True)} 更换成功"
    await session.finish(f"{msg}")


@on_command("删除农场UID", only_to_me=False)
async def delete_uid_farm(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    uid = session.get("uid", prompt=f"enter uid")
    info, k = get_user_info(uid)
    p = FarmAccount(
        clanname=k.clanbattle_name,
        account=k.account,
        password=k.password,
        farm_type=k.farm_type,
        owner=k.owner,
        not_work=0,
    )
    p.save()
    response = farm_api(k.account, k.password, k.uid, "kick")
    FarmUser.delete().where(FarmUser.uid == k.uid).execute()
    response_json = json.loads(response)
    uuid = response_json["uuid"]
    await session.finish(f"成功,https://example.com/check/{uuid}")


@on_command("更换农场UID", only_to_me=False)
async def change_uid_farm(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    uid = session.get("uid", prompt=f"输入旧uid")
    try:
        info, k = get_user_info(uid)
    except:
        await session.finish("uid 404 not found")
    new_uid = session.get("new_uid", prompt=f"输入新的uid")
    response = farm_api(k.account, k.password, k.uid, "kick")
    FarmUser.update({FarmUser.uid: new_uid}).where(FarmUser.id == k.id).execute()
    response_json = json.loads(response)
    uuid = response_json["uuid"]
    await session.finish(f"成功,https://example.com/check/{uuid}")


@on_command("更换农场QQ", only_to_me=False)
async def change_qq_farm(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    uid = session.get("uid", prompt=f"输入uid")
    try:
        info, k = get_user_info(uid)
    except:
        await session.finish("uid 404 not found")
    new_QQ = session.get("new_QQ", prompt=f"输入新的QQ")
    FarmUser.update({FarmUser.qq: new_QQ}).where(FarmUser.id == k.id).execute()
    await session.finish(f"成功")


@on_command("农场剩余", only_to_me=False)
async def count_farm_accounts(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"滚啊")
    farm_name_list = []
    count_list = []
    farm_accounts = FarmAccount.select().where(
        FarmAccount.owner == session.event.user_id
    )
    for i in range(1, 14 + 1):
        num = 0
        farm_name_list.append(f"套餐{i}:\n")
        for k in farm_accounts:
            if k.farm_type == i:
                num += 1
                farm_name_list.append(f"{k.clanname}[{k.account}]")
        count_list.append(f"套餐{i}:{num}")
    num_text = "农场剩余:\n" + "\n".join(count_list)
    name_text = "名字是\n" + "\n".join(farm_name_list) + "\n-----=-=-----"
    text = str_image_generate(num_text) + str_image_generate(name_text)
    text += str_image_generate(f"\n好友已使用:\n{friend_count(session.event.user_id)}")
    await session.finish(text)


@on_command("农场UID踢出", only_to_me=False)
async def kick_uid(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish(f"不是管理员")
        return
    uid = str(session.get("uid", prompt="输入你要踢出的UID"))
    user = FarmUser.select().where(FarmUser.uid == uid)
    for k in user:
        try:
            response = farm_api(k.account, k.password, k.uid, "kick")
            save_response_info(k.uid, response)
        except:
            await session.finish(f"[CQ:at,qq={session.event.user_id}]啊哦~有点问题,再试试吧")
    await session.finish(
        f"[CQ:at,qq={session.event.user_id}]正在踢出，请稍后使用 检查踢出状态 查询(一小时内有效）"
    )


@on_command("农场名踢野人", only_to_me=False)
async def kick_sb_by_farm_name(session):
    """
    等待改为get n
    """
    qq = session.event.user_id
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish("无权限")
    name = session.get("name", prompt="请输入农场名字")
    try:
        k = FarmAccount.get(FarmAccount.clanname == name)
    except:
        try:
            k = FarmUser.get(FarmUser.clanbattle_name == name)
        except:
            await session.finish("未找到")
    uid = session.get("uid", prompt="输入你要踢出的UID")
    try:
        response = farm_api(k.account, k.password, uid, "kick")
        text = f"[CQ:at,qq={qq}]正在踢出，{response_to_url(response)}"
    except:
        text = f"[CQ:at,qq={qq}]啊哦~有点问题,再试试吧"
    await session.finish(text)


@on_command("检查UID状态", only_to_me=False)
async def state_check_uid(session):
    UID = "0"
    if session.event.user_id in hoshino.config.SUPERUSERS:
        UID = str(session.get("UID", prompt="请输入UID"))
    k = FarmUser.get(FarmUser.uid == UID)
    try:
        state = str(check(k.state))
    except:
        state = "err"
    await session.finish(f"[CQ:at,qq={session.event.user_id}]队伍状态:{state}")


@on_command("用户清单", only_to_me=False)
async def count_farm_user(session):
    qq = session.event.user_id
    if session.event.user_id in hoshino.config.SUPERUSERS:
        qq_raw = session.get("qq_raw", prompt="请输入你的qq")
        qq = cqcode_to_QQ(qq_raw)
    else:
        return
    count_list = []
    table = """"id","qq","uid","公会名","账号","密码","套餐","到期时间","owner","other","text" """
    count_list.append(table)
    farm_user = FarmUser.select().where(FarmUser.owner == qq)
    for k in farm_user:
        text  = str(k.text)
        text = text.replace("\n", "-")
        table = f"""{k.id},{str(k.qq)},{str(k.uid)},{k.clanbattle_name}, {k.account}, {k.password},{str(k.farm_type)},{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(k.expires)))},{k.owner},{k.other}, {text}"""
        count_list.append(table)
    # table = str.replace('\n'.join(count_list), "\n\n", "\n")
    table = "\n".join(count_list)
    # print(table)

    try:
        os.mkdir("farm")
    except:
        print("文件夹farm已存在")
    table_dir = f"farm\\{str(qq)}user"
    with open(f"{table_dir}.csv", "w") as f:
        f.write(table)
    csv_to_xls(f"{table_dir}.csv", f"{table_dir}.xls")
    text = "文档已经输出"
    await session.send(text)
    # await session.send(str_image_generate(table))
