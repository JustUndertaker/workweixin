import importlib
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable, Optional

from workweixin.log import logger

_plugins: dict[str, "Plugin"] = {}
"""已加载插件集"""


@dataclass(eq=False)
class Plugin:
    """插件"""

    name: str
    """插件名"""
    module: ModuleType
    """插件模块对象"""


class PluginManager:
    """插件管理器"""

    def __init__(
        self,
        plugins: Optional[Iterable[str]] = None,
        search_path: Optional[Iterable[str]] = None,
    ):
        self.plugins: set[str] = set(plugins or [])
        self.search_path: set[str] = set(search_path or [])
        self.searched_plugins: dict[str, Path] = {}
        self.search_plugin()

    def _path_to_module_name(self, path: Path) -> str:
        rel_path = path.resolve().relative_to(Path(".").resolve())
        if rel_path.stem == "__init__":
            return ".".join(rel_path.parts[:-1])
        else:
            return ".".join(rel_path.parts[:-1] + (rel_path.stem,))

    def search_plugin(self):
        """搜索插件"""
        for module_info in pkgutil.iter_modules(self.search_path):
            # ignore if startswith "_"
            if module_info.name.startswith("_"):
                continue

            module_spec = module_info.module_finder.find_spec(module_info.name, None)
            if not module_spec:
                continue
            module_path = module_spec.origin
            if not module_path:
                continue
            self.searched_plugins[module_info.name] = Path(module_path).resolve()

    def load_plugin(self, name: str) -> Optional[Plugin]:
        """
        加载一个插件
        """
        try:
            if name in self.plugins:
                module = importlib.import_module(name)
            elif name in self.searched_plugins:
                module = importlib.import_module(
                    self._path_to_module_name(self.searched_plugins[name])
                )
            else:
                raise RuntimeError(f"该插件未找到: {name}! 请检查你的插件名称")
            logger.success(f'导入插件成功： "<y>{name}</y>"')
            plugin = Plugin(name=name, module=module)
            _plugins[name] = plugin
            return plugin
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                f'<r><bg #f8bbd0>导入插件失败： "{name}"</bg #f8bbd0></r>'
            )


def load_plugin(module_path: str):
    """
    加载一个插件
    """
    manager = PluginManager([module_path])
    manager.load_plugin(module_path)


def load_plugins(*plugin_dir: str):
    """
    加载文件夹下所有的插件
    """
    manager = PluginManager(search_path=plugin_dir)
    for name in manager.searched_plugins:
        manager.load_plugin(name)


def get_plugin(name: str) -> Optional["Plugin"]:
    """
    获取已经导入的某个插件。
    """
    return _plugins.get(name)


def get_loaded_plugins() -> set["Plugin"]:
    """获取当前已导入的所有插件。"""
    return set(_plugins.values())
