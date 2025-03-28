from dotenv import load_dotenv
import os

load_dotenv()

# https://tempmail.plus/zh/ 申请的临时邮箱地址 例如：123456@mailto.plus
MAIL_ADDR_AT_TEMP_MAIL_PLUS = os.getenv("MAIL_ADDR_AT_TEMP_MAIL_PLUS")

# 临时邮箱的PIN
MAIL_PIN_AT_TEMP_MAIL_PLUS = os.getenv("MAIL_PIN_AT_TEMP_MAIL_PLUS", "")

# 自建邮箱域名
MAIL_DOMAIN = os.getenv("MAIL_DOMAIN", "")

# 浏览器 UA
BROWSER_USER_AGENT = os.getenv(
    "BROWSER_USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
# 浏览器代理
BROWSER_PROXY = os.getenv("BROWSER_PROXY", '')
# 使用使用无头浏览器
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", 'false') == 'true'
