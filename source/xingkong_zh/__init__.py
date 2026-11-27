# -*- coding: utf-8 -*-
"""星空汉化 · Substance 3D Painter 中文显示插件。

设计原则：只翻译「绘制那一刻」的文本，不修改宿主控件、模型、输入或工程数据。
关闭插件或按 F1 后，界面完全恢复原样（包括 Adobe 官方中文）。
"""

import ctypes
import json
import os
import re
import tempfile
import time

from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import getCppPointer, isValid

try:
    import substance_painter.event as sp_event
    import substance_painter.resource as sp_resource
    import substance_painter.ui as sp_ui
except Exception:  # pragma: no cover - 非 Painter 环境
    sp_event = None
    sp_resource = None
    sp_ui = None

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NATIVE_PATH = os.path.join(PLUGIN_ROOT, "native", "xingkong_zh_qt6.dll")
TRANSLATIONS_DIR = os.path.join(PLUGIN_ROOT, "translations")
BILIBILI_URL = "https://space.bilibili.com/177308205"
APP_VERSION = "0.1.3"
API_VERSION = 1
HOST_NAME = "Substance 3D Painter"

_state = {
    "dll": None,
    "window": None,
    "menu": None,
    "shortcut": None,
    "key_filter": None,
    "dialog": None,
    "enabled": True,
    "fuzzy": True,
    "dictionary": {},
    "control_ids": {},
    "started": False,
    "log_path": os.path.join(tempfile.gettempdir(), "xingkong_sp.log"),
}


def _log(*parts):
    try:
        with open(_state["log_path"], "a", encoding="utf-8") as handle:
            handle.write(time.strftime("%Y-%m-%d %H:%M:%S ")
                         + " ".join(str(p) for p in parts) + "\n")
    except Exception:
        pass


def _settings():
    return QtCore.QSettings("XingKong", "xingkong_zh_sp")


def _load_preferences():
    settings = _settings()
    _state["enabled"] = settings.value("enabled", True, type=bool)
    _state["fuzzy"] = settings.value("fuzzy", True, type=bool)


def _save_preferences():
    settings = _settings()
    settings.setValue("enabled", bool(_state["enabled"]))
    settings.setValue("fuzzy", bool(_state["fuzzy"]))


def _main_window():
    if sp_ui is None:
        return None
    try:
        return sp_ui.get_main_window()
    except Exception as exc:
        _log("get main window failed:", exc)
        return None


def _load_control_ids():
    path = os.path.join(TRANSLATIONS_DIR, "control_ids_zh.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
        entries = data.get("translations", data) if isinstance(data, dict) else {}
        return {k: v for k, v in entries.items()
                if isinstance(k, str) and isinstance(v, str) and k.strip() and v}
    except Exception as exc:
        _log("control ids failed:", exc)
        return {}


def _load_dictionary():
    merged = {}
    if not os.path.isdir(TRANSLATIONS_DIR):
        return merged
    for name in sorted(os.listdir(TRANSLATIONS_DIR)):
        if not name.endswith("_zh.json") or name.startswith("control_ids"):
            continue
        path = os.path.join(TRANSLATIONS_DIR, name)
        try:
            with open(path, "r", encoding="utf-8-sig") as handle:
                data = json.load(handle)
            entries = data.get("translations", data) if isinstance(data, dict) else {}
            count = 0
            for source, target in entries.items():
                if (isinstance(source, str) and isinstance(target, str)
                        and source.strip() and target.strip()
                        and not target.startswith("_")):
                    merged[source] = target
                    count += 1
            _log(f"dictionary {name}: {count} entries")
        except Exception as exc:
            _log(f"dictionary {name} failed:", exc)
    return merged


def _load_native():
    dll = _state["dll"]
    if dll is not None:
        return dll
    if not os.path.isfile(NATIVE_PATH):
        _log("native engine missing:", NATIVE_PATH)
        return None
    try:
        dll = ctypes.CDLL(NATIVE_PATH)
        dll.xk_api_version.argtypes = []
        dll.xk_api_version.restype = ctypes.c_int
        version = dll.xk_api_version()
        if version != API_VERSION:
            raise RuntimeError(f"native API mismatch: {version} != {API_VERSION}")

        dll.xk_build_id.argtypes = []
        dll.xk_build_id.restype = ctypes.c_wchar_p
        dll.xk_install.argtypes = [ctypes.c_void_p]
        dll.xk_install.restype = ctypes.c_int
        dll.xk_uninstall.argtypes = []
        dll.xk_uninstall.restype = ctypes.c_int
        dll.xk_set_enabled.argtypes = [ctypes.c_int]
        dll.xk_set_enabled.restype = None
        dll.xk_set_fuzzy.argtypes = [ctypes.c_int]
        dll.xk_set_fuzzy.restype = None
        dll.xk_set_graph_enabled.argtypes = [ctypes.c_int]
        dll.xk_set_graph_enabled.restype = None
        dll.xk_add_translation.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        dll.xk_add_translation.restype = None
        dll.xk_add_id_translation.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        dll.xk_add_id_translation.restype = None
        dll.xk_clear_translations.argtypes = []
        dll.xk_clear_translations.restype = None
        dll.xk_translation_count.argtypes = []
        dll.xk_translation_count.restype = ctypes.c_int
        dll.xk_hook_count.argtypes = []
        dll.xk_hook_count.restype = ctypes.c_int
        dll.xk_combo_count.argtypes = []
        dll.xk_combo_count.restype = ctypes.c_int
        dll.xk_view_count.argtypes = []
        dll.xk_view_count.restype = ctypes.c_int

        _state["dll"] = dll
        _log("native engine:", dll.xk_build_id())
        return dll
    except Exception as exc:
        _log("native load failed:", exc)
        _state["dll"] = None
        return None


def _push_dictionary(dll):
    dictionary = _state["dictionary"]
    dll.xk_clear_translations()
    pushed = 0
    for source, target in dictionary.items():
        dll.xk_add_translation(source, target)
        pushed += 1
    ids = _state["control_ids"]
    for control_id, target in ids.items():
        dll.xk_add_id_translation(control_id, target)
    _log(f"dictionary pushed: {pushed}, control ids: {len(ids)}")
    return pushed


def _repaint_all():
    for widget in QtWidgets.QApplication.allWidgets():
        try:
            widget.update()
        except Exception:
            pass


def _install_native():
    dll = _load_native()
    if dll is None:
        return False
    app = QtWidgets.QApplication.instance()
    if app is None or not isValid(app):
        _log("QApplication unavailable")
        return False
    try:
        pointer = getCppPointer(app)[0]
        installed = dll.xk_install(ctypes.c_void_p(pointer)) == 1
        dll.xk_set_fuzzy(int(_state["fuzzy"]))
        dll.xk_set_graph_enabled(0)
        dll.xk_set_enabled(int(_state["enabled"]))
        # 钩子安装后强制重绘一次：启动时已绘制的菜单栏/工具栏才会走新钩子。
        _repaint_all()
        app.processEvents()
        _log("native install:", installed, "hooks:", dll.xk_hook_count(),
             "combos:", dll.xk_combo_count(), "views:", dll.xk_view_count(),
             "enabled:", _state["enabled"])
        return installed
    except Exception as exc:
        _log("native install failed:", exc)
        return False


def _set_enabled(enabled):
    _state["enabled"] = bool(enabled)
    dll = _state["dll"]
    if dll is not None:
        try:
            dll.xk_set_enabled(int(_state["enabled"]))
        except Exception as exc:
            _log("set enabled failed:", exc)
    _repaint_all()
    _save_preferences()
    _log("enabled:", _state["enabled"])


def _toggle_enabled():
    _set_enabled(not _state["enabled"])
    dialog = _state["dialog"]
    if dialog is not None and isValid(dialog):
        dialog.sync_state()


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("星空汉化 · 设置")
        self.setMinimumWidth(420)

        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel(
            f'<b style="font-size:15px;">星空汉化</b>'
            f'<span style="color:#888;"> · {HOST_NAME} {APP_VERSION}</span>'
        )
        layout.addWidget(title)

        self.enabled_box = QtWidgets.QCheckBox("启用中文显示（F1 切换）")
        self.enabled_box.setChecked(_state["enabled"])
        self.enabled_box.toggled.connect(_set_enabled)
        layout.addWidget(self.enabled_box)

        self.fuzzy_box = QtWidgets.QCheckBox("启用模糊匹配（大小写 / 下划线 / 空格）")
        self.fuzzy_box.setChecked(_state["fuzzy"])
        self.fuzzy_box.toggled.connect(self._on_fuzzy)
        layout.addWidget(self.fuzzy_box)

        self.count_label = QtWidgets.QLabel(self._count_text())
        layout.addWidget(self.count_label)

        link = QtWidgets.QLabel(
            f'<a href="{BILIBILI_URL}" style="color:#4da3ff;">{BILIBILI_URL}</a>'
        )
        link.setOpenExternalLinks(True)
        link.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(link)

        note = QtWidgets.QLabel(
            "翻译只作用于显示层：输入框内容、资源原名和工程数据保持原文。"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#888;")
        layout.addWidget(note)

        free_note = QtWidgets.QLabel("本插件完全免费，开源分享。")
        free_note.setWordWrap(True)
        free_note.setStyleSheet("color:#888;")
        layout.addWidget(free_note)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

    def _count_text(self):
        return f"已加载词条：{len(_state['dictionary'])} 条"

    def _on_fuzzy(self, checked):
        _state["fuzzy"] = bool(checked)
        dll = _state["dll"]
        if dll is not None:
            try:
                dll.xk_set_fuzzy(int(_state["fuzzy"]))
            except Exception:
                pass
        _repaint_all()
        _save_preferences()

    def sync_state(self):
        self.enabled_box.blockSignals(True)
        self.enabled_box.setChecked(_state["enabled"])
        self.enabled_box.blockSignals(False)
        self.count_label.setText(self._count_text())


def _show_settings():
    window = _state["window"] or _main_window()
    dialog = _state["dialog"]
    if dialog is None or not isValid(dialog):
        dialog = SettingsDialog(window)
        _state["dialog"] = dialog
    dialog.sync_state()
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()


class ToggleKeyFilter(QtCore.QObject):
    """应用级按键过滤器：F1 切换中英文。

    Painter 自身占用了 F1（帮助），QShortcut 会因快捷键歧义不触发，
    这里在事件分发阶段直接截获，命中后吞掉事件。
    """

    def eventFilter(self, watched, event):
        etype = event.type()
        if etype == QtCore.QEvent.Type.ShortcutOverride:
            # 先抢下快捷键绑定，避免被宿主 F1（帮助）截走。
            if event.key() == QtCore.Qt.Key.Key_F1:
                _log("F1 shortcutOverride accepted")
                event.accept()
                return True
        if etype == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_F1 and not event.modifiers():
                _log("F1 pressed via filter")
                _toggle_enabled()
                return True
            if event.key() == QtCore.Qt.Key.Key_F1:
                _log("F1 pressed with modifiers:", int(event.modifiers()))
        return False


def _add_actions(window):
    menu = QtWidgets.QMenu("星空汉化", window)

    link = QtWidgets.QWidgetAction(menu)
    label = QtWidgets.QLabel(
        f'<a href="{BILIBILI_URL}" style="color:#4da3ff;text-decoration:none;">'
        f'星空汉化 · B站主页</a>'
    )
    label.setOpenExternalLinks(True)
    label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
    label.setContentsMargins(10, 4, 10, 4)
    link.setDefaultWidget(label)
    menu.addAction(link)

    settings_action = QtGui.QAction("星空汉化设置", menu)
    settings_action.triggered.connect(_show_settings)
    menu.addAction(settings_action)

    if sp_ui is not None:
        sp_ui.add_menu(menu)
    _state["menu"] = menu

    app = QtWidgets.QApplication.instance()
    if app is not None and _state.get("key_filter") is None:
        key_filter = ToggleKeyFilter(app)
        app.installEventFilter(key_filter)
        _state["key_filter"] = key_filter
    _log("menu registered, F1 filter installed")


def _collect_untranslated(show_message=True):
    """内部调试用：采集当前界面未翻译的英文（不向用户提供入口）。"""
    items = set()
    stats = {"resources": 0, "model_items": 0, "widgets": 0}

    def add(value):
        if not isinstance(value, str):
            return
        text = " ".join(value.replace("\r", " ").replace("\n", " ").split())
        if not (2 <= len(text) <= 160):
            return
        if any("㐀" <= ch <= "鿿" for ch in text):
            return
        if not any(ch.isalpha() for ch in text):
            return
        if text.endswith((":", "：")):
            return
        if " " not in text:
            if len(text) > 24:
                return
            if re.search(r"[a-z][A-Z]", text):
                return  # CamelCase 内部标识
        if "_" in text and " " not in text:
            return
        if text.islower() and " " not in text:
            return
        if any(token in text for token in ("://", "\\", "<", ">", "=", "*", "%")):
            return
        if text in _state["dictionary"]:
            return
        items.add(text)

    # 1. 资源架（材质 / 智能材质 / 笔刷 / Alpha ...）
    if sp_resource is not None:
        try:
            for shelf in sp_resource.Shelves.all():
                for resource in shelf.resources():
                    try:
                        add(resource.gui_name())
                    except Exception:
                        pass
                    stats["resources"] += 1
        except Exception as exc:
            _log("collect resources failed:", exc)

    # 2. 可见模型
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, QtWidgets.QAbstractItemView):
            model = widget.model()
            if model is not None:
                try:
                    for row in range(model.rowCount()):
                        add(model.index(row, 0).data(
                            QtCore.Qt.ItemDataRole.DisplayRole))
                        stats["model_items"] += 1
                except Exception:
                    pass

    # 3. QAccessible 树
    seen = set()

    def walk(iface, depth=0):
        if iface is None or depth > 16 or id(iface) in seen:
            return
        seen.add(id(iface))
        try:
            for role in (QtGui.QAccessible.Text.Name,
                         QtGui.QAccessible.Text.Description,
                         QtGui.QAccessible.Text.Value,
                         QtGui.QAccessible.Text.Help):
                add(iface.text(role))
        except Exception:
            pass
        try:
            count = iface.childCount()
        except Exception:
            return
        for index in range(count):
            try:
                walk(iface.child(index), depth + 1)
            except Exception:
                pass

    try:
        for window in QtWidgets.QApplication.topLevelWidgets():
            walk(QtGui.QAccessible.queryAccessibleInterface(window))
    except Exception as exc:
        _log("accessible walk failed:", exc)

    # 4. 控件文本 / 菜单 / tooltip / 下拉项
    for widget in QtWidgets.QApplication.allWidgets():
        stats["widgets"] += 1
        for attribute in ("windowTitle", "text", "placeholderText", "toolTip"):
            try:
                add(getattr(widget, attribute)())
            except Exception:
                pass
        try:
            for action in widget.actions():
                add(action.text())
                add(action.toolTip())
        except Exception:
            pass
        if isinstance(widget, QtWidgets.QComboBox):
            try:
                for index in range(widget.count()):
                    add(widget.itemText(index))
            except Exception:
                pass
        if isinstance(widget, QtWidgets.QMenu):
            try:
                for action in widget.actions():
                    add(action.text())
            except Exception:
                pass

    path = os.path.join(os.path.expanduser("~"), "Desktop",
                        "xingkong_sp_untranslated.json")
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"metadata": stats,
                       "translations": {text: "" for text in
                                        sorted(items, key=str.casefold)}},
                      handle, ensure_ascii=False, indent=1)
        _log(f"collected {len(items)} untranslated -> {path}")
        if show_message:
            QtWidgets.QMessageBox.information(
                _state["window"], "星空汉化",
                f"已采集 {len(items)} 条未翻译文本：\n{path}\n\n"
                f"资源 {stats['resources']}，模型项 {stats['model_items']}，"
                f"控件 {stats['widgets']}")
    except Exception as exc:
        _log("collect failed:", exc)


def _watch_command_files():
    """运行期入口：轮询 %TEMP% 标记文件，不重启宿主即可采集/重载词库。"""
    flag = os.path.join(tempfile.gettempdir(), "xingkong_sp_collect.flag")
    if os.path.isfile(flag):
        try:
            os.remove(flag)
        except Exception:
            pass
        _log("runtime collect requested")
        _collect_untranslated(False)
    reload_flag = os.path.join(tempfile.gettempdir(), "xingkong_sp_reload.flag")
    if os.path.isfile(reload_flag):
        try:
            os.remove(reload_flag)
        except Exception:
            pass
        dll = _state.get("dll")
        if dll is not None:
            _state["dictionary"] = _load_dictionary()
            _state["control_ids"] = _load_control_ids()
            _push_dictionary(dll)
            _repaint_all()
            _log("runtime dictionary reload:", len(_state["dictionary"]))


def _start_engine():
    if _state["started"]:
        return
    window = _state["window"]
    if window is None or not isValid(window):
        window = _main_window()
        _state["window"] = window
    _state["dictionary"] = _load_dictionary()
    _state["control_ids"] = _load_control_ids()
    dll = _load_native()
    if dll is None:
        _log("engine start aborted: native missing")
        return
    _push_dictionary(dll)
    if _install_native():
        _state["started"] = True
        _log("engine started")
        watcher = QtCore.QTimer()
        watcher.timeout.connect(_watch_command_files)
        watcher.start(1000)
        _state["watcher"] = watcher
        flag = os.path.join(tempfile.gettempdir(), "xingkong_sp_collect.flag")
        if os.path.isfile(flag):
            QtCore.QTimer.singleShot(3000, lambda: _collect_untranslated(True))


def _initialize():
    # Painter 在插件启用时可能 start→close→start 连续调用，这里做重入保护，
    # 否则会装出两个菜单、重复调度引擎启动。
    if _state["started"] or _state["menu"] is not None:
        return
    window = _main_window()
    if window is None or not isValid(window):
        raise RuntimeError("Painter 的 Qt 界面尚未就绪")
    _state["window"] = window
    _load_preferences()
    _add_actions(window)
    QtCore.QTimer.singleShot(1500, _start_engine)
    _log("plugin initialized, engine scheduled")


def start_plugin():
    """Painter 入口：启用插件时调用。"""
    try:
        _initialize()
    except Exception as exc:
        _log("start_plugin failed:", exc)
        # 启动早期 UI 服务可能未就绪：等 GraphicalUserInterfaceStarted 再初始化。
        if sp_event is not None:
            try:
                sp_event.DISPATCHER.connect(
                    sp_event.GraphicalUserInterfaceStarted,
                    lambda _event: QtCore.QTimer.singleShot(0, _initialize))
                _log("deferred until GUI started")
            except Exception as inner:
                _log("defer failed:", inner)


def close_plugin():
    """Painter 出口：禁用插件时调用。"""
    dll = _state["dll"]
    try:
        if dll is not None:
            dll.xk_set_enabled(0)
            dll.xk_uninstall()
            dll.xk_clear_translations()
    except Exception as exc:
        _log("native uninstall failed:", exc)

    dialog = _state["dialog"]
    if dialog is not None and isValid(dialog):
        dialog.close()

    menu = _state["menu"]
    if menu is not None:
        try:
            if sp_ui is not None:
                sp_ui.delete_ui_element(menu)
            else:
                menu.deleteLater()
        except Exception as exc:
            _log("menu cleanup failed:", exc)

    watcher = _state.get("watcher")
    if watcher is not None:
        try:
            watcher.stop()
            watcher.deleteLater()
        except Exception:
            pass
        _state["watcher"] = None

    key_filter = _state.get("key_filter")
    if key_filter is not None:
        try:
            app = QtWidgets.QApplication.instance()
            if app is not None:
                app.removeEventFilter(key_filter)
            key_filter.deleteLater()
        except Exception:
            pass
        _state["key_filter"] = None

    _state.update({
        "menu": None,
        "shortcut": None,
        "dialog": None,
        "dll": None,
        "dictionary": {},
        "control_ids": {},
        "started": False,
        "window": None,
    })
    _log("plugin closed")


def reload_plugin():
    close_plugin()
    return start_plugin()
