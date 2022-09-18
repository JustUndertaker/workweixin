import json
from base64 import b64encode
from dataclasses import field
from hashlib import md5
from io import BytesIO
from pathlib import Path
from typing import Any, Union


class MessageSegment:
    """部分消息段"""

    @staticmethod
    def article(
        title: str,
        url: str,
        description: str = None,
        picurl: str = None,
    ) -> dict:
        """
        说明:
            图文消息段，一个图文消息支持1到8条图文

        参数:
            * `title`：标题，不超过128个字节，超过会自动截断
            * `url`：点击后跳转的链接。
            * `description`：描述，不超过512个字节，超过会自动截断
            * `picurl`：图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。
        """
        data = {"title": title, "url": url}
        if description:
            data["description"] = description
        if picurl:
            data["picurl"] = picurl
        return data

    @staticmethod
    def template_card_source(icon_url: str, desc: str, desc_color: int) -> dict:
        """
        说明:
            模板消息.卡片来源样式信息，不需要来源样式可不填写

        参数:
            * `icon_url`：来源图片的url
            * `desc`：来源图片的描述，建议不超过13个字
            * `desc_color`：来源文字的颜色，目前支持：0(默认) 灰色，1 黑色，2 红色，3 绿色
        """
        return {"icon_url": icon_url, "desc": desc, "desc_color": desc_color}

    @staticmethod
    def template_card_main_title(title: str, desc: str) -> dict:
        """
        说明:
            模板消息.模版卡片的主要内容，包括一级标题和标题辅助信息

        参数:
            * `title`：一级标题，建议不超过26个字。模版卡片主要内容的一级标题main_title.title和二级普通文本sub_title_text必须有一项填写
            * `desc`：标题辅助信息，建议不超过30个字
        """
        return {"title": title, "desc": desc}

    @staticmethod
    def template_card_emphasis_content(title: str, desc: str) -> dict:
        """
        说明:
            模板消息.关键数据样式

        参数:
            * `title`：关键数据样式的数据内容，建议不超过10个字
            * `desc`：关键数据样式的数据描述内容，建议不超过15个字
        """
        return {"title": title, "desc": desc}

    @staticmethod
    def template_card_quote_area(
        type: int = 0,
        url: str = "",
        appid: str = "",
        pagepath: str = "",
        title: str = "",
        quote_text: str = "",
    ) -> dict:
        """
        说明:
            模板消息.引用文献样式，建议不与关键数据共用

        参数:
            * `type`：引用文献样式区域点击事件，0或不填代表没有点击事件，1 代表跳转url，2 代表跳转小程序
            * `url`：点击跳转的url，quote_area.type是1时必填
            * `appid`：点击跳转的小程序的appid，quote_area.type是2时必填
            * `pagepath`：点击跳转的小程序的pagepath，quote_area.type是2时选填
            * `title`：引用文献样式的标题
            * `quote_text`：引用文献样式的引用文案
        """
        data = {"type": type, "title": title, "quote_text": quote_text}
        if type == 1:
            data["url"] = url
        elif type == 2:
            data["appid"] = appid
            if pagepath:
                data["pagepath"] = pagepath
        return data

    @staticmethod
    def template_card_horizontal_content(
        type: int, keyname: str, value: str, url: str, media_id: str, userid: str
    ) -> dict:
        """
        说明:

        """
        ...


class Message:
    """消息类"""

    msgtype: str
    """消息类型"""
    data: dict[str, Any] = field(default_factory=dict)
    """消息数据"""

    def __init__(self, msgtype: str, data: dict):
        self.msgtype = msgtype
        self.data = data

    def __str__(self) -> str:
        match self.msgtype:
            case "text":
                return f"[文字消息] {self.data.__str__()}"
            case "markdown":
                return f"[markdown消息] {self.data.__str__()}"
            case "image":
                return "[图片消息]"
            case "news":
                return "[图文消息]"
            case "file":
                return f"[文件消息]:{self.data.__str__()}"
            case _:
                return "[其他消息]"

    def to_dict(self) -> dict:
        return {"msgtype": self.msgtype, self.msgtype: self.data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def text(
        content: str,
        mentioned_list: list[str] = None,
        mentioned_mobile_list: list[str] = None,
    ) -> "Message":
        """
        说明:
            文本消息。

        参数:
            * `content`：文本内容，最长不超过2048个字节，必须是utf8编码
            * `mentioned_list`：userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人，如果开发者获取不到userid，可以使用mentioned_mobile_list
            * `mentioned_mobile_list`：手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        """
        data = {"content": content}
        if mentioned_list:
            data["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            data["mentioned_mobile_list"] = mentioned_mobile_list
        return Message(msgtype="text", data=data)

    @staticmethod
    def markdown(content: str) -> "Message":
        """
        说明:
            markdown类型消息

        参数:
            * `content`：markdown内容，最长不超过4096个字节，必须是utf8编码
        """
        return Message(msgtype="markdown", data={"content": content})

    @staticmethod
    def image(file: Union[bytes, BytesIO, Path]) -> "Message":
        """
        说明:
            图片类型消息

        参数:
            * `file`：图片文件，支持bytes，BytesIO，Path
        """
        if isinstance(file, Path):
            file = file.open(mode="rb").read()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return Message(
            msgtype="image", data={"base64": b64encode(file), "md5": md5(file)}
        )

    @staticmethod
    def news(articles: list[dict]) -> "Message":
        """
        说明:
            图文类型消息

        参数:
            * `articles`：图文消息列表，构造消息段需要使用`MessageSegment.article`
        """
        return Message(msgtype="news", data={"articles": articles})

    @staticmethod
    def file(media_id: str) -> "Message":
        """
        说明:
            文件类型消息

        参数:
            * `media_id`：文件id，通过文件上传接口获取
        """
        return Message(msgtype="file", data={"media_id": media_id})
