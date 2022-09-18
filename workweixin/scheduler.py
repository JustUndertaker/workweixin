from apscheduler.schedulers.asyncio import AsyncIOScheduler

from workweixin.log import logger

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
"""
异步定时器，用于创建定时任务，使用方法：
```
from workweinxin import scheduler

@scheduler.scheduled_job('cron', hour=0, minute=0)
async def _():
    pass
```
"""


def start_scheduler():
    global scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info("定时器模块已开启...")


def shout_down_scheduler():
    global scheduler
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时器模块已关闭...")
