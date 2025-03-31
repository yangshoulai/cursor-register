import os
import conf
import cursor_helper
import logger
import platform


def _check_platform():
    if platform.system() == "Linux":
        logger.error("❌ 不支持的系统")
        exit()


def _check_conf():
    if not conf.APP_PATH:
        logger.error("❌ APP_PATH 未设置")
        exit()
    if not os.path.exists(conf.APP_PATH):
        logger.error(f"❌ APP_PATH 不存在: {conf.APP_PATH}")
        exit()
    if not os.path.exists(conf.APP_PATH / "out" / "main.js"):
        logger.error(f"❌ Cursor main.js 不存在: {conf.APP_PATH}")
        exit()
    if not conf.MAIL_ADDR_AT_TEMP_MAIL_PLUS:
        logger.error("❌ MAIL_ADDR_AT_TEMP_MAIL_PLUS 未设置")
        exit()
    if not conf.MAIL_DOMAIN:
        logger.error("❌ MAIL_DOMAIN 未设置")
        exit()
    if not conf.BROWSER_USER_AGENT:
        logger.error("❌ BROWSER_USER_AGENT 未设置")
        exit()


if __name__ == "__main__":
    _check_platform()
    _check_conf()
    logger.info("👋 开始")
    try:
        re = cursor_helper.generate_random_registration()
        logger.info(f"✅ 随机生成注册信息")
        acc = cursor_helper.signup(re)
        if acc:
            logger.info(f"{'*'*20} 注册成功 {'*'*20}")
            logger.info(f"{'{:<18}'.format('First Name:')} {acc.first_name}")
            logger.info(f"{'{:<18}'.format('Last Name:')} {acc.last_name}")
            logger.info(f"{'{:<18}'.format('Email:')} {acc.mail_addr}")
            logger.info(f"{'{:<18}'.format('Password:')} {acc.password}")
            logger.info(f"{'{:<18}'.format('Verification Code:')} {acc.verification_code}")
            logger.info(f"{'*'*50}")
            cursor_helper.update_cursor_auth(acc.mail_addr, acc.token, acc.token)
            logger.info(f"✅ 更新认证信息成功")
            # cursor_helper.reset_cursor_machine_id()
            # logger.info(f"✅ 重置机器码成功")
            cursor_helper.patch_cursor()
            logger.info(f"✅ 补丁成功")
            file_path = cursor_helper.save_account(acc)
            logger.info(f"✅ 账号信息保存成功 => {file_path}")
            logger.info(f"✅ 请重启 Cursor 查看注册结果")
        else:
            raise RuntimeError("注册失败")
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
    finally:
        logger.info("👋 结束")
