import importlib
import os

from urh import constants
from urh.plugins.Plugin import Plugin, ProtocolPlugin
from urh.util.Logger import logger


class PluginManager(object):
    def __init__(self):
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self.installed_plugins = self.load_installed_plugins()

    @property
    def protocol_plugins(self):
        return [p for p in self.installed_plugins if isinstance(p, ProtocolPlugin)]

    def load_installed_plugins(self):
        """ :rtype: list of Plugin """
        result = []
        plugin_dirs = [d for d in os.listdir(self.plugin_path) if os.path.isdir(os.path.join(self.plugin_path, d))]
        settings = constants.SETTINGS

        for d in plugin_dirs:
            if d == "__pycache__":
                continue
            try:
                class_module = self.load_plugin(d)
                plugin = class_module()
                plugin.plugin_path = os.path.join(self.plugin_path, plugin.name)
                plugin.load_description()
                plugin.enabled = settings.value(plugin.name, type=bool) if plugin.name in settings.allKeys() else False
                result.append(plugin)
            except ImportError as e:
                logger.warning("Could not load plugin {0} ({1})".format(d, e))
                continue

        return result

    @staticmethod
    def load_plugin(plugin_name):
        classname = plugin_name + "Plugin"
        module_path = "urh.plugins." + plugin_name + "." + classname

        module = importlib.import_module(module_path)
        return getattr(module, classname)

    def is_plugin_enabled(self, plugin_name: str):
        return any(plugin_name == p.name for p in self.installed_plugins if p.enabled)

    def get_plugin_by_name(self, plugin_name):
        for plugin in self.installed_plugins:
            if plugin.name == plugin_name:
                return plugin
        return None
