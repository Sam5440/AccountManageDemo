from nonebot import on_command

import hoshino
from .SqlClass import *
from .config import __version__, Sqlinfo

"""
 * **************************************************************************
 *                                                                          *
 *                                   _oo8oo_                                *
 *                                  o8888888o                               *
 *                                  88" . "88                               *
 *                                  (| -_- |)                               *
 *                                  0\  =  /0                               *
 *                                ___/'==='\___                             *
 *                              .' \/|     |// '.                           *
 *                             / \/|||  :  |||// \                          *
 *                            / _||||| -:- |||||_ \                         *
 *                           |   | \/\  -  /// |   |                        *
 *                           | \_|  ''\---/''  |_/ |                        *
 *                           \  .-\__  '-'  __/-.  /                        *
 *                         ___'. .'  /--.--\  '. .'___                      *
 *                      ."" '<  '.___\_<|>_/___.'  >' "".                   *
 *                     | | :  `- \`.:`\ _ /`:.`/ -`  : | |                  *
 *                     \  \ `-.   \_ __\ /__ _/   .-` /  /                  *
 *                 =====`-.____`.___ \_____/ ___.`____.-`=====              *
 *                                   `=---=`                                *
 * **************************************************************************
 * ********************       佛祖保佑 永远无BUG 			 ********************
 * **************************************************************************
"""


@on_command("农场帮助", only_to_me=False)
async def check_new_ver_chat(session):
    # if session.event.user_id not in hoshino.config.SUPERUSERS:
    #     return
    await session.finish(
        f"当前版本v{__version__}\nMSG={session.self_id}"
    )


@on_command("初始化f", only_to_me=False)
async def check_new_ver_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    await session.finish(f"初始化完成,当前版本v{__version__}")
