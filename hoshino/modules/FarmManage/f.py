import asyncio
import csv
import json
import random
import re
import string
import time
from io import StringIO

import pandas as pd
import requests

from .SqlClass import *
from .config import BeginStr
from .ttf import *


def log(texts):
    print(texts)
    now = int(time.time())
    # 转换为其他日期格式
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # log(otherStyleTime)
    p = Log(text=str(texts), time=otherStyleTime)
    p.save()
    return 0


def admin_log(texts, qqid):
    print(texts)
    now = int(time.time())
    # 转换为其他日期格式
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # log(otherStyleTime)
    p = AdminLog(text=str(texts), qq=str(qqid), time=otherStyleTime)
    p.save()
    return 0


def query_time(uids, qq, n):
    """
    旧版查询时间函数，过渡时期用
    """
    num = 0
    text = "error 404"
    for k in uids:
        num = num + 1
        if n == str(num):
            expires_time = round((k.expires - int(time.time())) / 86400, 1)
            if expires_time > 0:
                text = f"[CQ:at,qq={qq}] 还有{expires_time}天到期"
            else:
                text = f"[CQ:at,qq={qq}] 到期了"
    return text  # ,k.expires


def get_uids(qq):
    """
    获得这个qq的全部uid(农场)
    其中text是uids的json文本，num是uid数量，uids返回列表，有这些uid的详细信息
    text, num, uids = get_uids(qq)
    """
    uids = FarmUser.select().where(FarmUser.qq == qq)
    uid_list = []
    num = 0
    for k in uids:
        num = num + 1
        uid = f"【{str(num)}】:{str(k.uid)}({k.clanbattle_name})\n"
        uid_list.append(uid)
    text = f"请回复需要选择的UID【序号】\n 或发送全部选择（仅邀请和踢出可用）\n" + "\n".join(uid_list)
    text = f"[CQ:at,qq={qq}]{str_image_generate(text)}"
    num = int(num)
    return text, num, uids


def get_n(uids, n):
    """_summary_

    Args:
        uids (_type_): 数据库获得的该qq的数据
        n (_type_): 第n个

    Returns:
        _type_: 第n个信息
    """
    num = 0
    for k in uids:
        num = num + 1
        if str(n) == str(num):
            user = k
    return user


def farm_api(account, password, uid, state, logs=True):
    """_summary_
        通过api 发送账号密码uid踢人
    Args:
        account (_str_): account
        password (_str_): password
        uid (_str_): uid 
        state (_str_): api操作
        logs (bool, optional): 是否输出日志

    Returns:
        _json_: 返回信息
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
        + '", "uid":'
        + uid
        + " }"
    )
    if logs:
        log(data)
    response = requests.post(
        f"https://pcrd.tencentbot.top/{state}", headers=headers, data=data
    )
    resp = response.text
    return resp


def farm_clan_create(account, password, name):
    """
    公会创建
    """
    name = name.encode("unicode-escape").decode()
    description = "买bot找猫猫鸭~"
    description = description.encode("unicode-escape").decode()
    headers = {
        "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
        "Content-Type": "application/json",
    }
    data = (
        '{ "account": "'
        + account
        + '", "password": "'
        + password
        + '", "clanname":"'
        + name
        + '","description":"'
        + description
        + '" }'
    )
    log(data)
    response = requests.post(
        f"https://pcrd.tencentbot.top/createclan", headers=headers, data=data
    )
    resp = response.text
    return resp


def farm_change_clan_name(account, password, name, join_condition=0):
    """
    公会改名
    """
    name = name.encode("unicode-escape").decode()
    headers = {
        "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
        "Content-Type": "application/json",
    }
    data = (
        '{ "account": "'
        + account
        + '", "password": "'
        + password
        + '", "name":"'
        + name
    )
    if join_condition == 0:
        data = data + '" }'
    else:
        data = data + '", "join_condition": ' + str(join_condition) + " }"
    log(data)
    response = requests.post(
        f"https://pcrd.tencentbot.top/changeclanname", headers=headers, data=data
    )
    resp = response.text
    return resp


def farm_search_clan(name):
    """
    搜索公会，返回一个带结果的json
    如{'info":{"list":[]}} 代表无结果
    """
    name = name.encode("unicode-escape").decode()
    headers = {
        "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
        "Content-Type": "application/json",
    }
    data = '{ "name": "' + name + '" }'
    log(data)
    response = requests.post(
        f"https://pcrd.tencentbot.top/searchclan", headers=headers, data=data
    )
    resp = response.text
    return resp


def farm_search_clanid(clanid):
    headers = {
        "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
        "Content-Type": "application/json",
    }
    data = '{ "clanid": ' + str(clanid) + " }"
    log(data)
    response = requests.post(
        "https://pcrd.tencentbot.top/getclaninfo", headers=headers, data=data
    )
    resp = response.text
    info = check(resp, True, 1)
    infos = json.loads(info)
    print(infos)
    name = infos["info"]["clan"]["detail"]["clan_name"]
    name = name.encode("utf8").decode()
    return info, name


def kick(uids, qq, n):
    """
    踢出uids中的第n项，并生成@qq文本返回
    """
    num = 0
    text = "error 404"
    for k in uids:
        num = num + 1
        if n == num or n == 0:
            try:
                response = farm_api(k.account, k.password, k.uid, "kick")
                save_response_info(k.uid, response)
                text = f"[CQ:at,qq={qq}]正在踢出，请稍后使用 检查踢出状态 查询(一小时内有效）"
            except:
                text = f"[CQ:at,qq={qq}]啊哦~有点问题,再试试吧"
    return text


async def invite(uids, qq, n):
    """
    注意,该函数为async函数,需要使用await调用
    邀请uids中的第n项，并生成@qq文本返回
    """
    num = 0
    now = int(time.time())
    text = "error 404"
    for k in uids:
        num = num + 1
        if n == num or n == 0:
            try:
                if k.expires != now:
                    response = farm_api(k.account, k.password, k.uid, "invite")
                    save_response_info(k.uid, response)
                    text = f"[CQ:at,qq={qq}]正在邀请，请稍后使用 检查状态 查询(一小时内有效）"
                    await_time = 1 if n != 0 else 5
                    await asyncio.sleep(await_time)
                    """
                    if str(k.state) != "0":
                        new_time = k.expires - 86400
                        q = FarmUser.update({FarmUser.expires: new_time}).where(FarmUser.uid == k.uid)
                        q.execute()
                        text = f'第二次邀请了呀，扣你1天吧[CQ:at,qq={qq}]正在邀请，请稍后使用 检查状态 查询(一小时内有效）'
                        """
                else:
                    text = f"[CQ:at,qq={qq}]好像 过期了呀"
            except:
                text = f"[CQ:at,qq={qq}]啊哦~有点问题,再试试吧"
    return text


def save_response_info(saver_uid, response):
    """
    保存队列信息到数据库
    """
    q = FarmUser.update({FarmUser.state: response}).where(FarmUser.uid == saver_uid)
    q.execute()
    return response


def update_user_info_text(user, text, append=True):
    """
    在text内添加新信息,并返回变更后信息（base64CqCode形式)
    """
    # 保存旧名字到text
    if append:
        text = f"{text}\n[旧]:\n{user.text}"
    FarmUser.update({FarmUser.text: text}).where(FarmUser.uid == user.uid).execute()
    text = f"QQ:{user.qq}\nUID{user.uid}\n{text}"
    return str_image_generate(text)


def check(response, raw=False, sleep_time=0):
    """
    检查队列执行状态
    """
    time.sleep(sleep_time)
    response_json = json.loads(response)
    uuid = response_json["uuid"]
    response = requests.get(f"https://pcrd.tencentbot.top/check/{uuid}").content.decode(
        "utf8"
    )
    log(response)
    # num = 5
    # log(json.loads(requests.get(f'https://pcrd.tencentbot.top/queue').content.decode('utf8')))
    #
    # while num != 0:
    #     num_json = json.loads(requests.get(f'https://pcrd.tencentbot.top/queue').content.decode('utf8'))
    #     num = int(num_json["num"])
    #     sleep(num*2)
    if raw:
        return response
    else:
        infos = json.loads(response)
        try:
            info = infos["info"]
            try:
                clan_id = info["clan_id"]
                clan_state = info["clan_status"]
                info = f"ID{clan_id}({clan_state})的公会已经成功创建)"
                return info
            except:
                info = info.replace("is not in", "此UID已经不在公会")
                info = info.replace("success kick", "已踢出UID")
                info = info.replace("in running", "正在过验证码")
                info = info.replace("success change name for clanid", "成功改名")
        except:
            num = str(infos["queue_num"])
            info = f"排队中，位于队伍第{num}位"
        return info


def generate_key():
    """
    生成卡密随机字符串
    """
    begin = BeginStr  # 从config.py获得卡密开头
    new_key = "".join(
        random.sample(string.ascii_letters + string.digits, 16 - len(begin))
    )
    new_key = begin + new_key
    return new_key


def add_key(farmtype, qq, addtimes):
    """
    卡密加入数据库
    """
    new_key = generate_key()
    # 入库
    time_today = int(time.time())
    p = FarmKeys(
        key=new_key,
        farm_type=farmtype,
        add_time=addtimes,
        key_time=time_today,
        is_used=False,
        user_qq="0",
        owner=str(qq),
    )
    p.save()
    return new_key


def time_change(begin, end, changetime):
    user = FarmUser.select().where(FarmUser.id >= 0)
    response = "TIME CHANGE " + str(changetime)
    num = 0
    for k in user:
        if begin <= k.expires <= end:
            n = k.expires + changetime
            p = FarmUser.update({FarmUser.expires: n}).where(FarmUser.uid == k.uid)
            p.execute()
            num += 1
            log(k.uid)
            save_response_info(k.uid, response)
    return num


def new_farm_user_add(
    qq_, uid_, clanbattle_name_, account_, password_, farm_type_, expires_, owner_
):
    """
    new_farm_user_add(qq_, uid_, clanbattle_name_, account_, password_, farm_type_, expires_, owner_)
    """
    p = FarmUser(
        qq=qq_,
        uid=uid_,
        clanbattle_name=clanbattle_name_,
        account=account_,
        password=password_,
        farm_type=farm_type_,
        expires=expires_,
        state="0",
        owner=owner_,
        other="0",
        text="无",
    )
    p.save()
    return 0


def new_friend_user_add(qq_, uid_, slaves_group_, expires_, owner_):
    """
    new_friend_user_add(qq_, uid_, slaves_group_, expires_, owner_)
    """
    p = FriendFarm(
        qq=qq_, uid=uid_, slaves_group=slaves_group_, expires=expires_, owner=owner_
    )
    p.save()
    return 0


def delete_key(key, qq, now):
    key_info = FarmKeys.get(FarmKeys.key == key)
    if not key_info.is_used:
        p = FarmKeys.update(
            {FarmKeys.is_used: 1, FarmKeys.used_time: now, FarmKeys.user_qq: qq}
        ).where(FarmKeys.key == key)
        p.execute()
        key_info = FarmKeys.get(FarmKeys.key == key)
        # 记录充值

        if int(key_info.user_qq) == int(qq) and key_info.used_time == now:
            return True
        else:
            print(key_info.user_qq)
            print(qq)
            print(2000)
            return False
    else:
        return False


def get_user_info(uid, type_f="farm"):
    """
    获得用户信息  默认获得farm
    输入uid，和类型
    获得该uid基本信息文本以及具体信息列表user、
    """
    if type_f == "farm":
        user = FarmUser.get(FarmUser.uid == uid)
        clanname = user.clanbattle_name.replace(user.account, "[敏感信息屏蔽]")
        info = f"账号UID:{user.uid}[#{user.id}]\n位于【套餐{user.farm_type}】的《{clanname}》农场\n还有{round((user.expires - int(time.time())) / 86400, 1)}天到期，\n预计到期时间是{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(user.expires + 1)))}"
    else:
        user = FriendFarm.get(FriendFarm.uid == uid)
        info = f"账号UID:{user.uid}[#{user.id}]\n位于好友农场[{user.slaves_group}]\n还有{round((user.expires - int(time.time())) / 86400, 1)}天到期，\n预计到期时间是{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(user.expires + 1)))} "
    info = f"[CQ:at,qq={user.qq}]" + str_image_generate(info)
    return info, user


def get_min_farm(farm_type, owner):
    farms = FarmAccount.select().where(
        FarmAccount.farm_type == farm_type, FarmAccount.owner == owner
    )
    min_farm_id = 999
    for k in farms:
        clanname = k.clanname
        clanname = re.sub(r"\D", "", clanname)
        clanname = int(clanname)
        if clanname < min_farm_id:
            min_farm_id = clanname
            account_info = k
    return account_info


def friend_count(owner=10001):
    n = 0
    count_list = []
    # owner = 3373919223
    if owner != 10001:
        friend_slaves = FriendSlave.select().where(FriendSlave.owner == owner)
        friend_user = FriendFarm.select().where(FriendFarm.owner == owner)
    else:
        friend_slaves = FriendSlave.select().where(FriendSlave.id != 0)
        friend_user = FriendFarm.select().where(FriendFarm.id != 0)
    # start_id = 500 if owner == 295309297 else 1
    start_id = 1
    for k in friend_slaves:
        if int(k.group) > n:
            n = int(k.group)
    for i in range(start_id, n + 1):
        if 50 < i < 500:
            continue
        try:
            FriendSlave.get(FriendSlave.group == i)
            num = 0
            for k in friend_user:
                if k.slaves_group == str(i):
                    num += 1
            count_list.append(f"-{i}好友场:{num}\n")
            FriendSlave.update({FriendSlave.friend_num: str(num)}).where(
                FriendSlave.group == str(i)
            ).execute()
        except:
            print(f"{i} is None")
    text = f"{owner}使用计数\n" + "".join(count_list)
    return text


def csv_to_xls(csv_path, xls_path):
    """
    FutureWarning：由于不再维护 xlwt 包，xlwt 引擎将在未来版本的 pandas 中删除。
    这是 pandas 中唯一支持 xls 格式写入的引擎。安装 openpyxl 并改为写入 xlsx 文件。
    您可以将选项 io.excel.xls.writer 设置为 'xlwt' 以消除此警告。
    虽然此选项已弃用并且还会引发警告，但可以全局设置并抑制警告。
    writer = pd.ExcelWriter(ls_path) 进程已结束，退出代码0
    """
    with open(csv_path, "r", encoding="gb18030", errors="ignore") as f:
        data = f.read()
    data_file = StringIO(data)
    print(data_file)
    csv_reader = csv.reader(data_file)
    list_csv = []
    for row in csv_reader:
        list_csv.append(row)
    df_csv = pd.DataFrame(list_csv).applymap(str)
    """
    这部分是不将csv装换为xls，而是过滤后再写入csv文件
    df_csv = df_csv[(df_csv[4] == '') | (df_csv[4] == 'name')]      # 过滤出第四列包含空值和name的数据
    df_csv.to_csv(csv_path, index=0, header=0, encoding='gb18030')  # 写入csv文件中
    """
    writer = pd.ExcelWriter(xls_path)
    # 写入Excel
    df_csv.to_excel(excel_writer=writer, index=False, header=False)
    writer.save()


def time_to_int_val(str_time: str):
    # str_time = session.get("str_time", prompt="请输入时间，如2022-03-16")
    str_time_format = str_time
    str_time_format = str_time_format.replace("年", "-")
    str_time_format = str_time_format.replace("月", "-")
    str_time_format = str_time_format.replace("日", "")
    print(str_time_format)
    time_int_val = int(time.mktime(time.strptime(str_time_format, "%Y-%m-%d")))
    return time_int_val


def cqcode_to_QQ(qq_raw):
    qq_raw = str(qq_raw)
    qq = re.sub(r"\D", "", qq_raw)
    return qq


def num_text_to_num(text):
    return cqcode_to_QQ(text)


def uids_rawtext_to_list(raw_text: str, interval_str="@"):
    raw_text = raw_text.replace(r"\r", "")
    raw_text = raw_text.replace("\r", "")
    raw_text = raw_text.replace("#", "@")  # 兼容#号分割
    raw_text = raw_text.split("\n")
    split_info = []
    for split_text in raw_text:
        split_info += [split_text.split(interval_str)]
    return split_info


def response_to_url(response, to_qrcode=False, to_short_url=True):
    response_json = json.loads(response)
    uuid = response_json["uuid"]
    url = f"https://pcrd.tencentbot.top/check/{uuid}"
    if to_short_url:
        url = short_url(url)
    if to_qrcode:
        url = qrcode_url(url)
    return url


def short_url(url):
    # headers = {
    #     "User-Agent": "Apipost client Runtime/+https://www.apipost.cn/",
    # }

    # data = {"url": f"{url}"}
    # response = requests.post("", headers=headers, data=data)
    # response_json = json.loads(response.text)
    # shorturl = response_json["shorturl"]
    # return shorturl
    return url
