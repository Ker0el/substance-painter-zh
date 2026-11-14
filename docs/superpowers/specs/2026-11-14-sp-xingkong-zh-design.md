# Substance 3D Painter 星空汉化插件 · 设计

日期：2026-11-14
状态：V1 实现完成，进入词库扩充阶段

## 1. 目标

为 Substance 3D Painter 12.2.0（Windows，Qt 6.8.7，Python 3.13）提供中文显示插件，
沿用 Designer 版（`E:\3D\SD_zh`）的架构与品牌规范：

- 纯显示层：不改控件文本、模型、输入、工程数据；卸载或 `F1` 关闭即完全还原
- 安装到 `%USERPROFILE%\Documents\Adobe\Adobe Substance 3D Painter\python\plugins\xingkong_zh`
- 菜单栏「星空汉化」（B 站链接 + 设置），`F1` 切换
- 词库独立产出：官方 `.qm` 提取 + 人工词条

## 2. 宿主事实（实测）

| 项 | 值 |
|---|---|
| 版本 | 12.2.0（Vulkan） |
| Qt | 6.8.7（与工程编译用 6.8.3 同 ABI） |
| Python / PySide6 | 3.13.9 / 内置 |
| 插件入口 | `python/plugins/<pkg>/__init__.py` 的 `start_plugin/close_plugin`，无 pluginInfo.json |
| 启用方式 | `Python` 菜单勾选；状态存 `HKCU\Software\Adobe\Adobe Substance 3D Painter\python_plugins\<name>\launch_at_start=on` |
| UI API | `substance_painter.ui.get_main_window() / add_menu(QMenu) / delete_ui_element()` |
| 主窗口 | `QMainWindow` 包装（C++ 类 `Alg::S4MainWindow`） |
| 界面语言 | 官方中文（`translation_zh.qm` 已内置）→ 插件定位为「增补」 |

## 3. 架构

```
xingkong_zh/
├── __init__.py                 Painter 垫片
├── xingkong_zh/__init__.py     生命周期、词库、菜单、F1、设置、内部采集器
├── native/xingkong_zh_qt6.dll  显示层引擎（自研，源自 Designer 版并适配 Painter）
└── translations/*.json         运行时词库
```

### 3.1 显示层（C++）

- `XingKongDelegate`：`displayText()` 翻译（仅 `typeid == QStyledItemDelegate` 的实例）
- `XingKongComboDelegate` + `ComboProxyModel`：包装宿主自定义 delegate 的下拉框与资源视图，
  用 `QIdentityProxyModel` 只替换 `DisplayRole`
- `QPainter::drawText` 8 个重载的 IAT 钩子（本机实测 16 个导入槽）：菜单、按钮、tooltip、自绘文本
- 跳过：离屏 device（QImage/QPixmap/打印）、QLineEdit 用户输入（只翻 placeholder）、含汉字原文
- `ResourceSearchFilter`：中文查询时本地 `setRowHidden` 过滤，英文查询交还宿主

### 3.2 Painter 适配点

- 资源架容器 `Alg::NewResourcesView`、资源选择器 `Alg::ResourcePickerWidget`
- 搜索框 `objectName == "search_field"`，资源视图 `objectName == "resources"`
- 资源视图 delegate 为宿主自绘（`Alg::ResourceItemDelegate`）→ 必须包装而不能替换
- 重入保护：Painter 启用插件时可能 `start → close → start`

## 4. 词库流水线

1. `tools/qm_extract.py`：解析 `.qm`（按哈希表偏移逐条读取）→ `translations/qm_official_zh.json`
   本机产量 5676 条，过滤（无译文/含占位符/路径/超长）后 3994 条
2. `translations/manual_assets_zh.json`：人工资源名与术语（当前 636 条）
3. `tools/build_dictionary.py`：合并 → `source/translations/{ui,assets,control_ids}_zh.json`

## 5. 验证记录（2026-11-14）

- 插件加载：`native install: True hooks: 16 combos: 56 views: 1`
- 资源清单：API 枚举 starter_assets 共 1485 个显示名（与界面一致）
- 词库：界面 3994 + 资源 1441 = 5435 条；资源名覆盖 1414/1485（95.2%），
  剩余 71 条为字体/着色器 ID/色彩空间专名，按 `docs/translations-2026-11-14.md` 的规则保留英文
- 材质资源架：中文名正常显示（秋日落叶、沥青混凝土、织物 · 蕾丝…）
- 中文搜索：`布料` → 16/106，`金属` → 8/106
- 开关：关闭后全部恢复英文（含 `All libraries`），再开启恢复中文
- 菜单栏出现「星空汉化」

## 6. 未完成 / 后续

- 其余资源分类（笔刷、Alpha、智能材质等）的显示名尚未采集与翻译
- Painter 参数面板 `Alg::ElidedLabel` 的省略文本还原（参考实现有此处理）
- 图层面板独立开关、Ctrl+右键改译、在线更新、安装包（Inno）
