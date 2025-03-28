import logging

_log_format = "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"

# 配置基本日志
logging.basicConfig(
    level=logging.INFO,
    format=_log_format,
    handlers=[
        # 控制台输出
        logging.StreamHandler()
    ],
)

logging.getLogger("requests").setLevel(logging.WARNING)


_logger = logging.getLogger()


def info(message):
    _logger.info(message)


def warning(message):
    _logger.warning(message)


def error(message):
    _logger.error(message)


def debug(message):
    _logger.debug(message)
