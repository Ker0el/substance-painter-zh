# -*- coding: utf-8 -*-
"""组装免安装包：source/ -> dist/xingkong_zh/ + dist/xingkong_zh.zip。"""
import hashlib
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "source")
DIST = os.path.join(ROOT, "dist")
TARGET = os.path.join(DIST, "xingkong_zh")
SKIP = {"__pycache__"}


def copy_tree():
    if os.path.isdir(TARGET):
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET,
                    ignore=shutil.ignore_patterns(*SKIP, "*.pyc"))
    readme = os.path.join(ROOT, "installer", "安装说明.txt")
    if os.path.isfile(readme):
        shutil.copy2(readme, os.path.join(TARGET, "说明.txt"))


def make_zip():
    archive = os.path.join(DIST, "xingkong_zh.zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        for folder, _, files in os.walk(TARGET):
            for name in files:
                full = os.path.join(folder, name)
                rel = os.path.relpath(full, TARGET)
                handle.write(full, os.path.join("xingkong_zh", rel))
    return archive


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    copy_tree()
    archive = make_zip()
    print("dist:", TARGET)
    print("zip :", archive)
    print("sha256:", sha256(archive))


if __name__ == "__main__":
    main()
