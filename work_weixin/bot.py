from httpx import AsyncClient

from .config import Config
from .log import logger
from .message import Message


class Bot:
    """机器人"""

    _client: AsyncClient
    """发送消息客户端"""
    config: Config
    """配置文件"""

    def __init__(self, config: Config):
        headers = {"Content-Type": "application/json"}
        self._client = AsyncClient(headers=headers)
        self.config = config

    async def send_message(self, message: Message) -> str:
        """
        说明：
            向webhook地址发送消息。

        参数:
            * `data`：Message类型，从workweixin.message构造
        """
        try:
            response = await self._client.post(
                url=self.config.webhook, data=message.to_json()
            )
            logger.debug(f"发送消息：{message}")
            return response.text
        except Exception as e:
            logger.opt(exception=e).error("发送消息失败：")
            return f"发送消息失败：{str(e)}"
