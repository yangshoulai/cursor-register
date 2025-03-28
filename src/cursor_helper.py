import datetime
import hashlib
import json
import os
import random
import sqlite3
import sys
import time
import uuid
from conf import MAIL_DOMAIN
import logger
from model import Account, Registration
from browser_helper import BrowserManager
import temp_mail_helper


def generate_random_mail_addr(length=6) -> str:
    """生成随机邮箱地址"""
    random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
    timestamp = str(int(time.time()))[-4:]  # 使用时间戳后4位
    return f"{random_str}{timestamp}@{MAIL_DOMAIN}"


def generate_random_password(length=12) -> str:
    """生成随机密码 - 改进密码生成算法，确保包含各类字符"""
    chars = "abcdefghijklmnopqrstuvwxyz"
    upper_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    special = "!@#$%^&*"

    # 确保密码包含至少一个大写字母、一个数字和一个特殊字符
    password = [
        random.choice(chars),
        random.choice(upper_chars),
        random.choice(digits),
        random.choice(special)
    ]

    # 添加剩余随机字符
    password.extend(random.choices(chars + upper_chars + digits + special, k=length-4))

    # 打乱密码顺序
    random.shuffle(password)
    return "".join(password)


def generate_random_username(length=6) -> str:
    """生成随机用户名"""
    first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    rest_letters = "".join(
        random.choices("abcdefghijklmnopqrstuvwxyz", k=length - 1)
    )
    return first_letter + rest_letters


def generate_random_registration() -> Registration:
    """生成随机注册信息"""
    return Registration(
        first_name=generate_random_username(),
        last_name=generate_random_username(),
        mail_addr=generate_random_mail_addr(),
        password=generate_random_password(),
        verification_code=None,
    )


def get_cursor_storage_json_path() -> str:
    """获取cursor存储json路径"""
    # 判断操作系统
    if sys.platform == "win32":  # Windows
        appdata = os.getenv("APPDATA")
        if appdata is None:
            raise EnvironmentError("APPDATA 环境变量未设置")
        return os.path.join(
            appdata, "Cursor", "User", "globalStorage", "storage.json"
        )
    elif sys.platform == "darwin":  # macOS
        return os.path.abspath(
            os.path.expanduser(
                "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
            )
        )
    elif sys.platform == "linux":  # Linux 和其他类Unix系统
        return os.path.abspath(
            os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
        )
    else:
        raise NotImplementedError(f"不支持的操作系统: {sys.platform}")


def get_cursor_state_db_path() -> str:
    # 判断操作系统
    if sys.platform == "win32":  # Windows
        appdata = os.getenv("APPDATA")
        if appdata is None:
            raise EnvironmentError("APPDATA 环境变量未设置")
        return os.path.join(
            appdata, "Cursor", "User", "globalStorage", "state.vscdb"
        )
    elif sys.platform == "darwin":  # macOS
        return os.path.abspath(os.path.expanduser(
            "~/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
        ))
    elif sys.platform == "linux":  # Linux 和其他类Unix系统
        return os.path.abspath(os.path.expanduser(
            "~/.config/Cursor/User/globalStorage/state.vscdb"
        ))
    else:
        raise NotImplementedError(f"不支持的操作系统: {sys.platform}")


def generate_new_cursor_machine_id():
    """生成新的机器ID"""
    # 生成新的UUID
    dev_device_id = str(uuid.uuid4())

    # 生成新的machineId (64个字符的十六进制)
    machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

    # 生成新的macMachineId (128个字符的十六进制)
    mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

    # 生成新的sqmId
    sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

    return {
        "telemetry.devDeviceId": dev_device_id,
        "telemetry.macMachineId": mac_machine_id,
        "telemetry.machineId": machine_id,
        "telemetry.sqmId": sqm_id,
    }


def reset_cursor_machine_id():
    """重置机器ID"""
    storage_json_path = get_cursor_storage_json_path()
    if not os.path.exists(storage_json_path):
        raise RuntimeError(f"配置文件不存在: {storage_json_path}")
    if not os.access(storage_json_path, os.R_OK | os.W_OK):
        raise RuntimeError(f"配置文件不可读写: {storage_json_path}")
    with open(storage_json_path, 'r', encoding="utf-8") as f:
        storage = json.load(f)

    new_machine_id = generate_new_cursor_machine_id()
    storage.update(new_machine_id)
    with open(storage_json_path, 'w') as f:
        json.dump(storage, f, indent=4)


def update_cursor_auth(email: str, access_token: str, refresh_token: str):
    """
    更新Cursor的认证信息
    :param email: 新的邮箱地址
    :param access_token: 新的访问令牌
    :param refresh_token: 新的刷新令牌
    """

    updates = []
    # 登录状态
    updates.append(("cursorAuth/cachedSignUpType", "Auth_0"))

    if email is not None:
        updates.append(("cursorAuth/cachedEmail", email))
    if access_token is not None:
        updates.append(("cursorAuth/accessToken", access_token))
    if refresh_token is not None:
        updates.append(("cursorAuth/refreshToken", refresh_token))

    conn = None
    try:
        state_db_path = get_cursor_state_db_path()
        conn = sqlite3.connect(state_db_path)
        cursor = conn.cursor()

        for key, value in updates:
            check_query = f"SELECT COUNT(*) FROM itemTable WHERE key = ?"
            cursor.execute(check_query, (key,))
            if cursor.fetchone()[0] == 0:
                insert_query = "INSERT INTO itemTable (key, value) VALUES (?, ?)"
                cursor.execute(insert_query, (key, value))
            else:
                update_query = "UPDATE itemTable SET value = ? WHERE key = ?"
                cursor.execute(update_query, (value, key))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()


def signup(registration: Registration) -> Account:
    try:
        browser = BrowserManager.new_browser()
        tab = browser.new_tab("https://authenticator.cursor.sh/sign-up")
        browser.activate_tab(tab)
        logger.info(f"✅ 访问注册页面")
        if not BrowserManager.bypass_turnstile(tab):
            raise RuntimeError("无法越过 Cloudflare Turnstile")
        if tab.ele("@name=first_name"):
            # First Name
            tab.actions.click("@name=first_name").input(registration.first_name)
            logger.info(f"✅ 填写 First Name")
            time.sleep(random.uniform(1, 3))
            # Last Name
            tab.actions.click("@name=last_name").input(registration.last_name)
            logger.info(f"✅ 填写 Last Name")
            time.sleep(random.uniform(1, 3))
            # EMAIL
            tab.actions.click("@name=email").input(registration.mail_addr)
            time.sleep(random.uniform(1, 3))
            logger.info(f"✅ 填写 Email")
            # Submit
            tab.actions.click("@type=submit")
            logger.info(f"✅ 提交注册信息")
        else:
            raise RuntimeError('填写注册信息失败')

        if tab.ele("@name=password"):
            tab.ele("@name=password").input(registration.password)
            time.sleep(random.uniform(1, 2))
            tab.ele("@type=submit").click()
            logger.info(f"✅ 填写登录密码")
        else:
            raise RuntimeError('填写登录密码失败')

        if tab.ele("This email is not available."):
            raise RuntimeError(f"邮箱[{registration.mail_addr}]已被使用")
        if tab.ele("Sign up is restricted."):
            raise RuntimeError(f"注册被限制")
        verification_code = None
        tries = 0
        while tries < 5 and not verification_code:
            logger.info(f"🔍 第[{tries + 1}]次尝试获取验证码")
            verification_code = temp_mail_helper.get_latest_cursor_verification_code(registration.mail_addr)
            tries += 1
            if not verification_code:
                time.sleep(2)
        if not verification_code:
            raise RuntimeError(f"获取验证码失败")
        logger.info(f"✅ 成功获取验证码[{verification_code}]")
        registration.verification_code = verification_code
        for i in range(len(verification_code)):
            tab.ele(f"@data-index={i}").input(verification_code[i])
            time.sleep(random.uniform(0.3, 0.6))
        logger.info(f"✅ 填写验证码")
        time.sleep(random.uniform(3, 5))
        if not tab.ele("Account Settings"):
            raise RuntimeError("验证码验证失败")
        token = None
        for cookie in tab.cookies():
            if cookie.get("name") == "WorkosCursorSessionToken":
                token = cookie["value"].split("%3A%3A")[1]
                break
        if not token:
            raise RuntimeError("获取用户 token 失败")
        logger.info(f"✅ 成功获取用户 token")
        return Account(
            first_name=registration.first_name,
            last_name=registration.last_name,
            mail_addr=registration.mail_addr,
            password=registration.password,
            verification_code=registration.verification_code,
            token=token
        )
    except Exception as e:
        raise e
    finally:
        browser.quit()


def save_account(acc: Account) -> str:
    '''保存账户信息'''
    dir = os.path.join(os.getcwd(), 'accounts')
    if not os.path.exists(dir):
        os.makedirs(dir)
    file = os.path.join(dir, acc.mail_addr)

    with open(file, 'w') as f:
        json.dump(acc.__dict__, f, indent=4)
    return file
