from dataclasses import dataclass


@dataclass
class Registration:
    """注册信息"""
    # 名字
    first_name: str
    # 姓氏
    last_name: str
    # 邮箱地址
    mail_addr: str
    # 邮箱密码
    password: str
    # 验证码
    verification_code: str


@dataclass
class Account(Registration):
    token: str
