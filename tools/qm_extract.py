# -*- coding: utf-8 -*-
"""从 Qt .qm 文件提取 source -> translation 词条（自有实现，无第三方依赖）。

.qm 结构（Qt 6，qtranslator.cpp）：16 字节魔数 + 若干 {u8 tag, u32be len, payload} 段。
消息段（0x69）由记录组成，记录内为 {tag, u32be len, payload} 序列，Tag_End(1) 结束。
本工具只取 Translation(3) / SourceText(6) / Context(7) / Comment(8)。
"""
import json
import os
import struct
import sys

MAGIC = bytes([0x3c, 0xB8, 0x64, 0x18, 0xCA, 0xEF, 0x9C, 0x95,
               0xCD, 0x21, 0x1C, 0xBF, 0x60, 0xA1, 0xBD, 0xDD])
TAG_END, TAG_TRANSLATION, TAG_SOURCE, TAG_CONTEXT, TAG_COMMENT = 1, 3, 6, 7, 8


def read_sections(path):
    data = open(path, "rb").read()
    if data[:16] != MAGIC:
        raise ValueError(f"not a .qm file: {path}")
    pos, sections = 16, {}
    while pos + 5 <= len(data):
        tag = data[pos]
        length = struct.unpack(">I", data[pos + 1:pos + 5])[0]
        pos += 5
        if tag == 0 or length == 0:
            break
        sections[tag] = (pos, length)
        pos += length
    return data, sections


def parse_messages(data, section):
    start, length = section
    pos, end = start, start + length
    record = {"source": None, "context": None, "comment": None, "translations": []}
    while pos < end:
        tag = data[pos]
        pos += 1
        if tag == TAG_END:
            if record["source"] is not None:
                yield record
            record = {"source": None, "context": None, "comment": None, "translations": []}
            continue
        if tag in (5, 9):  # Obsolete1 / Obsolete2：跳过 4 字节
            pos += 4
            continue
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
        payload = data[pos:pos + size]
        pos += size
        if tag == TAG_TRANSLATION:
            record["translations"].append(payload.decode("utf-16-be", "replace"))
        elif tag == TAG_SOURCE:
            record["source"] = payload.decode("utf-8", "replace")
        elif tag == TAG_CONTEXT:
            record["context"] = payload.decode("utf-8", "replace")
        elif tag == TAG_COMMENT:
            record["comment"] = payload.decode("utf-8", "replace")


def iter_records(data, sections):
    """按哈希表偏移逐条解析；顺序遍历会在未知标签处失步，哈希表才是权威索引。"""
    if 0x42 in sections and 0x69 in sections:
        table, table_len = sections[0x42]
        message_start, message_len = sections[0x69]
        seen = set()
        for index in range(table_len // 8):
            offset = struct.unpack(
                ">I", data[table + index * 8 + 4: table + index * 8 + 8])[0]
            if offset in seen or offset >= message_len:
                continue
            seen.add(offset)
            pos = message_start + offset
            end = message_start + message_len
            record = {"source": None, "context": None, "comment": None,
                      "translations": []}
            while pos < end:
                tag = data[pos]
                pos += 1
                if tag == TAG_END:
                    break
                if tag in (5, 9):
                    pos += 4
                    continue
                size = struct.unpack(">I", data[pos:pos + 4])[0]
                pos += 4
                payload = data[pos:pos + size]
                pos += size
                if tag == TAG_TRANSLATION:
                    record["translations"].append(payload.decode("utf-16-be", "replace"))
                elif tag == TAG_SOURCE:
                    record["source"] = payload.decode("utf-8", "replace")
                elif tag == TAG_CONTEXT:
                    record["context"] = payload.decode("utf-8", "replace")
                elif tag == TAG_COMMENT:
                    record["comment"] = payload.decode("utf-8", "replace")
            if record["source"] is not None:
                yield record


def extract(paths):
    entries = {}
    conflicts = {}
    for path in paths:
        data, sections = read_sections(path)
        if 0x69 not in sections:
            continue
        for record in iter_records(data, sections):
            source = (record["source"] or "").strip()
            target = (record["translations"][0] if record["translations"] else "").strip()
            if not source or not target:
                continue
            if source in entries and entries[source] != target:
                conflicts.setdefault(source, {entries[source]}).add(target)
                continue
            entries[source] = target
    return entries, conflicts


def main(argv):
    if len(argv) < 2:
        print("usage: qm_extract.py <out.json> <file.qm>...")
        return 2
    output = argv[1]
    entries, conflicts = extract(argv[2:])
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump({"$schema": "xk-translation-v1", "id": "official-qm",
                   "language": "zh-CN",
                   "description": "Substance 3D Painter 官方 .qm 提取",
                   "translations": entries}, handle, ensure_ascii=False, indent=1)
    print(f"entries={len(entries)} conflicts={len(conflicts)} -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
