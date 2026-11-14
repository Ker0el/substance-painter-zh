# -*- coding: utf-8 -*-
"""星空汉化 · Substance 3D Painter 插件入口垫片。

Painter 从 ``python/plugins/<包名>/__init__.py`` 加载插件，调用
``start_plugin`` / ``close_plugin``。实现主体在同包的 ``xingkong_zh`` 模块。
"""


def start_plugin():
    from .xingkong_zh import start_plugin as _entry
    return _entry()


def close_plugin():
    from .xingkong_zh import close_plugin as _entry
    return _entry()


def reload_plugin():
    from .xingkong_zh import reload_plugin as _entry
    return _entry()
