import os
import sys
import time
from DrissionPage import ChromiumOptions, Chromium
from conf import BROWSER_USER_AGENT, BROWSER_PROXY, BROWSER_HEADLESS
import logger


class BrowserManager:

    def __init__(self) -> None:
        pass

    @staticmethod
    def _default_options() -> ChromiumOptions:
        co = ChromiumOptions()
        # 获取项目根目录（当前脚本所在目录的父目录）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        extension_path = os.path.join(project_root, "turnstilePatch")
        if os.path.exists(extension_path):
            co.add_extension(extension_path)
        co.set_user_agent(BROWSER_USER_AGENT)
        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        if BROWSER_PROXY:
            co.set_proxy(BROWSER_PROXY)

        # 禁用自动化特征（关键参数）
        co.set_argument("--disable-blink-features=AutomationControlled")
        co.set_argument("--disable-features=AutomationControlled")
        co.set_argument("--disable-automation-extension")

        # 随机化指纹参数
        co.set_pref("webgl.vendor", "NVIDIA Corporation")
        co.set_pref("webgl.renderer", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)")
        co.set_pref("navigator.plugins.length", 5)
        co.set_pref("navigator.hardwareConcurrency", 8)

        # 覆盖自动化特征（关键）
        co.set_pref("dom.webdriver.enabled", False)
        co.set_pref("useAutomationExtension", False)

        # 设置时区参数
        co.set_argument("--timezone=Asia/Shanghai")
        co.set_pref("timezone.override", "Asia/Shanghai")

        # 设置更真实的屏幕参数
        co.set_pref("screen.width", 1920)
        co.set_pref("screen.height", 1080)
        co.set_pref("screen.pixelDepth", 24)
        co.auto_port()
        co.headless(BROWSER_HEADLESS)

        # Mac 系统特殊处理
        if sys.platform == "darwin" or sys.platform == "linux":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")
        return co

    @staticmethod
    def new_browser() -> Chromium:
        return Chromium(BrowserManager._default_options())

    @staticmethod
    def bypass_turnstile(tab) -> bool:
        turnstile = tab.run_js("try { return turnstile } catch(e) { }")
        if not turnstile:
            return True

        challengeSolution = tab.ele("@name=cf-turnstile-response")
        if not challengeSolution:
            return True
        tab.run_js("try { return turnstile.reset() } catch(e) { }")

        challengeWrapper = challengeSolution.parent()
        challengeIframe = challengeWrapper.shadow_root.ele("tag:iframe")
        challengeIframeBody = challengeIframe.ele("tag:body").shadow_root
        challengeButton = challengeIframeBody.ele("tag:input")
        challengeButton.click()
        for _ in range(5):
            try:
                turnstileResponse = tab.run_js("try { return turnstile.getResponse() } catch(e) { return null }")
                if turnstileResponse:
                    return True
                time.sleep(2)
            except:
                pass
        return False
