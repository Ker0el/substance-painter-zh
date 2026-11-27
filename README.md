# Substance 3D Painter 中文插件

为 Adobe Substance 3D Painter（Windows，12.x）提供界面与资源名的中文显示。

## 功能

- 菜单栏「星空汉化」入口：B 站主页链接 + 设置窗口
- `F1` 全局切换中文显示（设置持久化）
- 界面文本翻译：菜单、按钮、参数标签、标签页、下拉框、列表/树/表格、资源架、tooltip
- 资源架名称翻译：材质、笔刷、Alpha 等（词库持续扩充）
- 中文搜索：资源架搜索框输入中文时本地过滤，英文查询保持宿主原生搜索

## 安装

1. 把本目录（`xingkong_zh`）复制到：
   `%USERPROFILE%\Documents\Adobe\Adobe Substance 3D Painter\python\plugins\xingkong_zh`
2. 启动 Painter → 菜单 `Python` → `Plugins` → 勾选 `xingkong_zh`
3. 菜单栏出现「星空汉化」即安装成功

卸载：在 Python 菜单取消勾选，或删除插件目录。

## 目录结构

```
xingkong_zh/
├── __init__.py              Painter 入口垫片（start_plugin / close_plugin）
├── xingkong_zh/__init__.py  Python 主体：生命周期、词库、菜单、F1、设置
├── native/xingkong_zh_qt6.dll  自研 Qt6 显示引擎（delegate + drawText IAT 钩子）
└── translations/
    ├── ui_zh.json           界面词条（官方 .qm 提取 + 人工覆盖）
    ├── assets_zh.json       资源名与术语
    └── control_ids_zh.json  控件专项（_skip_ / 位点译法）
```

## 版本记录

### v0.1.3（2026-11-27）

- 术语统一：`Mask` 统一「遮罩」（原遮罩/蒙版混用）、`Base Color` 统一「基础颜色」（官方「底色」）、`Base Surface`「基础表面」（官方「底面」）
- 官方错译修正（`manual_official_overrides_zh.json` 扩至 197 条）：
  `Grunge` 垃圾摇滚→脏旧、`Count` 计算→数量、`Alignment` 校准→对齐、`Environment` 背景→环境、
  `Metallic` 金属光泽→金属度、`channel` 频道→通道、`Alpha` 透贴→Alpha、`Opacity` 透明度→不透明度、
  `Filter` 过滤器→滤镜、`Specular` 镜面→高光、`Dilation + diffusion` 漫反射→扩散、
  `Bilinear` 两次线性→双线性、`Hard light` 硬光→强光、`Levels - Mask` 级别→色阶
- 词库总数保持 **8120 条**（界面 4061 + 资源 4059），文档术语表同步更新
- Python/native/installer 版本号同步至 0.1.3
- 安装完成页默认勾选「启动 Substance 3D Painter」，插件目录改为可选操作

### v0.1.1（2026-11-26）

- 词库扩充至 **8120 条**（界面 4061 + 资源 4059），补全生成器/滤镜参数标签、混合模式、环境与灯光参数
- 新增官方 `.qm` 译文覆盖机制（`translations/manual_official_overrides_zh.json`），修正 `切线 | Wrap包裹`、`Tri-planar三面映射` 等夹英文的官方译法
- 新增参数标签自动组合词条（`translations/manual_auto_params_zh.json`，已人工复核）
- 翻译范围：参数与界面文本中文化；材质/选项专名按行业习惯保留英文
- 安装包更名为 `SP_zh-CN_v0.1.1_Setup.exe`

## 词库

词库为 JSON，格式见文件头 `$schema: xk-translation-v1`，`translations` 为 `原文 -> 译文`。
插件按文件名排序加载 `translations/*_zh.json`，后加载覆盖先加载；含汉字的原文默认跳过。

本工程的人工词条在 `translations/manual_*.json`，用脚本合成为运行时词库：

```bash
python -I tools/qm_extract.py translations/qm_official_zh.json "<Painter安装目录>/resources/translation/"*_zh.qm
python -I tools/build_dictionary.py
```

## 构建

```bat
build.bat
```

要求：Visual Studio 2022/2026（MSVC x64）、Ninja、Qt 6.8.x msvc2022_64 SDK。
默认读取 `_ThirdParty\Qt\6.8.3\msvc2022_64`，也可用环境变量 `QT_ROOT` 指定。

## 设计边界

- 只替换「绘制那一刻」的文本：`QStyledItemDelegate::displayText`、宿主自定义 delegate 的
  `QIdentityProxyModel` 包装、`QPainter::drawText` 的 IAT 钩子
- 离屏绘制（`QImage/QPixmap/打印`）一律不翻译，避免导出图片带中文
- `QLineEdit` 只翻译 placeholder，用户输入永不翻译
- 中文搜索只在输入含汉字时接管，清空后恢复宿主原生行为

## 许可

MIT。

## 安装包

```bat
build.bat                                 :: 编译引擎
python -I tools/package.py                :: 组装 dist/xingkong_zh 与 zip
installer\build.bat                       :: Inno Setup 生成安装包（默认 ISCC 路径可用 ISCC 环境变量覆盖）
```

安装包只写入当前用户目录 `Documents\Adobe\Adobe Substance 3D Painter\python\plugins\xingkong_zh`，
并写入 `HKCU\Software\Adobe\Adobe Substance 3D Painter\python_plugins\xingkong_zh\launch_at_start=on`
让插件随 Painter 启动；卸载时删除该键与插件文件，不触碰宿主文件。
