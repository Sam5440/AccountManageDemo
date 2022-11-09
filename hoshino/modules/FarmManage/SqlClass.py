from peewee import *

from .config import Sqlinfo

db = MySQLDatabase(Sqlinfo.Database, host=Sqlinfo.Host, user=Sqlinfo.user, passwd=Sqlinfo.Passwd, port=3306)


class FarmKeys(Model):
    key = CharField()
    farm_type = IntegerField()
    add_time = IntegerField()
    used_time = IntegerField()
    is_used = BooleanField()
    user_qq = CharField()
    owner = CharField()

    class Meta:
        database = db


class FarmUser(Model):
    qq = CharField()
    uid = CharField()
    clanbattle_name = CharField()
    account = CharField()
    password = CharField()
    farm_type = IntegerField()
    expires = IntegerField()
    state = CharField()
    owner = CharField()
    other = CharField()
    text = CharField()

    class Meta:
        database = db


class FarmAccount(Model):
    clanname = CharField()
    account = CharField()
    password = CharField()
    farm_type = IntegerField()
    owner = CharField()
    not_work = BooleanField()

    class Meta:
        database = db


class FriendFarm(Model):
    qq = CharField()
    uid = CharField()
    slaves_group = CharField()
    expires = IntegerField()
    owner = CharField()

    class Meta:
        database = db


class FriendSlave(Model):
    account = CharField()
    password = CharField()
    group = CharField()
    email_account = CharField()
    email_password = CharField()
    friend_num = IntegerField()
    owner = CharField()

    class Meta:
        database = db


class Log(Model):
    text = CharField()
    time = CharField()

    class Meta:
        database = db


class AdminLog(Model):
    text = CharField()
    qq = CharField()
    time = CharField()

    class Meta:
        database = db

class CardLog(Model):
    key = CharField()
    qq = CharField()
    time = CharField()

    class Meta:
        database = db

class NameToUID(Model):
    name = CharField()
    uid = CharField()

    class Meta:
        database = db

class KickMany(Model):
    ac = CharField()
    pw = CharField()
    text = CharField()

    class Meta:
        database = db
