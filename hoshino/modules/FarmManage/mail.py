import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from random import *
from random import *


def mail(qq, url):
    ret = True
    n = randint(1, 10)
    my_sender = ''
    my_pass = ''
    mail_url = ''
    my_user = str(qq) + '@qq.com'  # 收件人邮箱账号，我这边发送给自己
    try:

        msg = MIMEText(url, 'plain', 'utf-8')
        msg['From'] = formataddr(["猫猫服务中心", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["User", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "猫猫酱的通知"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL(mail_url, 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except BaseException:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


