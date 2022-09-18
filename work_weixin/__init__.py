from typing import Any

from fastapi import FastAPI

from workweixin.bot import Bot
from workweixin.config import Config, Env
from workweixin.driver import Driver
from workweixin.log import default_filter, logger
from workweixin.scheduler import shout_down_scheduler, start_scheduler

_driver: Driver = None
"""后端驱动实例"""


def get_driver() -> Driver:
    """获取Dricer实例"""
    if _driver is None:
        raise ValueError("未获取到Driver实例，可能是没有init.")
    return _driver


def get_bot() -> Bot:
    """获取bot实例"""
    driver = get_driver()
    return driver.bot


def get_app() -> FastAPI:
    """
    获取fastapi的APP对象
    """
    driver = get_driver()
    return driver.server_app


def init():
    """初始化"""
    global _driver
    if not _driver:
        env = Env()
        config = Config(_common_config=env.dict())
        default_filter.level = config.log_level
        logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
        logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")
        _driver = Driver(config)
        _driver.on_startup(start_scheduler)
        _driver.on_shutdown(shout_down_scheduler)


def run(*args: Any, **kwargs: Any):
    """启动机器人服务"""
    driver = get_driver()
    logger.info("正在启动机器人...")
    driver.run(*args, **kwargs)


from workweixin.plugin import load_plugin as load_plugin
from workweixin.plugin import load_plugins as load_plugins
from workweixin.scheduler import scheduler as scheduler
