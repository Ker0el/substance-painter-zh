# -*- coding: utf-8 -*-
"""生成运行时词库。

输入：
  translations/qm_official_zh.json   官方 .qm 提取（tools/qm_extract.py 产出）
  translations/manual_*.json         人工词条（人工优先）
输出：
  source/translations/ui_zh.json     界面词条（.qm 基础层 + 人工覆盖）
  source/translations/assets_zh.json 资源/术语词条（人工）
  source/translations/control_ids_zh.json  控件专项词条
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATIONS = os.path.join(ROOT, "translations")
SOURCE_TRANSLATIONS = os.path.join(ROOT, "source", "translations")

HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
FORMATTED = re.compile(r"%[0-9]+|\{[0-9]+\}")
UNWANTED = ("://", "\\", "<", ">", "{{", "${")
DRIVE_ROOT = re.compile(r"^[A-Za-z]:[\/]")


def load(path):
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    entries = data.get("translations", data) if isinstance(data, dict) else {}
    return {k: v for k, v in entries.items()
            if isinstance(k, str) and isinstance(v, str)}


def acceptable(source, target):
    source = source.strip()
    target = target.strip()
    if not source or not target:
        return False
    if len(source) > 140:
        return False
    if HAN.search(source) or not HAN.search(target):
        return False
    if FORMATTED.search(source):
        return False
    if any(token in source for token in UNWANTED):
        return False
    if DRIVE_ROOT.match(source) or source.startswith("/"):
        return False
    if target == source:
        return False
    return True


def merge(target, entries, label):
    added = kept = 0
    for source, translation in entries.items():
        if not acceptable(source, translation):
            kept += 1
            continue
        target[source] = translation.strip()
        added += 1
    print(f"  {label}: +{added} (skipped {kept})")
    return target


def dump(path, identifier, entries, description):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"$schema": "xk-translation-v1", "id": identifier,
                   "language": "zh-CN", "description": description,
                   "translations": dict(sorted(entries.items(),
                                               key=lambda kv: kv[0].casefold()))},
                  handle, ensure_ascii=False, indent=1)
    print(f"  -> {os.path.relpath(path, ROOT)} ({len(entries)} entries)")


def main():
    print("build dictionary")
    official = load(os.path.join(TRANSLATIONS, "qm_official_zh.json"))
    manual_ids = load(os.path.join(TRANSLATIONS, "manual_control_ids_zh.json"))

    ui = {}
    merge(ui, official, "official qm")
    merge(ui, load(os.path.join(TRANSLATIONS, "manual_ui_zh.json")), "manual ui")
    # 官方 .qm 的个别译法夹带英文（如「切线 | Wrap包裹」）：允许源文含中文，
    # 直接覆盖，不做 acceptable() 过滤。ui_zh.json 运行时最后加载，优先级最高。
    overrides = load(os.path.join(TRANSLATIONS, "manual_official_overrides_zh.json"))
    for source, target in overrides.items():
        if source.strip() and target.strip():
            ui[source.strip()] = target.strip()
    if overrides:
        print(f"  official overrides: {len(overrides)}")

    assets = {}
    # 人工词条按文件名顺序合并，后加载覆盖先加载。
    for name in sorted(os.listdir(TRANSLATIONS)):
        if not (name.startswith("manual_") and name.endswith("_zh.json")):
            continue
        if name in ("manual_control_ids_zh.json",
                    "manual_official_overrides_zh.json"):
            continue
        merge(assets, load(os.path.join(TRANSLATIONS, name)), name)

    dump(os.path.join(SOURCE_TRANSLATIONS, "ui_zh.json"), "sp-ui", ui,
         "Substance 3D Painter 界面词条（官方 .qm 基础层 + 人工覆盖）")
    dump(os.path.join(SOURCE_TRANSLATIONS, "assets_zh.json"), "sp-assets", assets,
         "Substance 3D Painter 资源与术语词条")
    dump(os.path.join(SOURCE_TRANSLATIONS, "control_ids_zh.json"), "sp-control-ids",
         manual_ids, "控件专项词条（_skip_ 与位点译法）")

    total = len(ui) + len(assets)
    print(f"total runtime entries: {total}")


if __name__ == "__main__":
    main()
