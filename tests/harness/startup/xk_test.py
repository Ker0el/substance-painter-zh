# -*- coding: utf-8 -*-
"""测试启动模块：随 Painter 启动自动加载，启用 xingkong_zh 并落状态 JSON。
不属于发布内容，仅用于本机验证。"""
import json
import os
import tempfile
import time

OUT = os.path.join(tempfile.gettempdir(), "xingkong_sp_harness.json")


def start_plugin():
    from PySide6 import QtCore
    QtCore.QTimer.singleShot(10000, _start)


def close_plugin():
    pass


def _start():
    from PySide6 import QtCore
    start, dump = _bootstrap()
    QtCore.QTimer.singleShot(6000, dump)


def _bootstrap():
    import importlib
    import substance_painter_plugins

    result = {"ts": time.strftime("%H:%M:%S")}
    try:
        module = importlib.import_module("xingkong_zh")
        if not substance_painter_plugins.is_plugin_started(module):
            substance_painter_plugins.start_plugin(module)
        result["started"] = True
    except Exception:
        import traceback
        result["started"] = False
        result["error"] = traceback.format_exc()

    def dump():
        try:
            impl = importlib.import_module("xingkong_zh.xingkong_zh")
            state = impl._state
            dll = state.get("dll")
            result.update({
                "engine_started": state.get("started"),
                "dictionary": len(state.get("dictionary") or {}),
                "enabled": state.get("enabled"),
                "hooks": dll.xk_hook_count() if dll else None,
                "combos": dll.xk_combo_count() if dll else None,
                "views": dll.xk_view_count() if dll else None,
                "translations": dll.xk_translation_count() if dll else None,
            })
        except Exception:
            import traceback
            result["dump_error"] = traceback.format_exc()
        with open(OUT, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=1)

    return result, dump
