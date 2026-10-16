# -*- coding: utf-8 -*-
"""正确的 CSS 解析器 —— 供分层分析/生成共用。

为什么单独写一个
----------------
之前的分析用了 `re.finditer(r'([^{}]+)\{([^{}]*)\\}')`。
这个正则在**跨规则**时会失控：它不认注释、不认字符串、也不配平花括号，
于是把 A 规则的尾巴和 B 规则的头部拼成一条"规则"。

后果很严重：它报出「:root{--sfc:…} 在全部 28 份文件里逐字相同」，
而实际上 **m01_c_arrays.css 里根本没有 --sfc 的定义**（只在注释里提过一次）。
基于错误数据我差点删掉一份文件里的真实规则 —— 幸好先拿单页试跑，
只删掉 1 个块就发现对不上，已从备份还原。

本解析器按字符扫描，正确处理：
  · 注释          /* … */
  · 字符串        "…"  '…'
  · 括号配平      {} 与 ()（url() 里可能有花括号字符）
  · @media 嵌套   递归处理内部规则

对外接口：
    parse(css) -> [Node]
    Node = {'kind':'rule'|'at'|'comment', 'prelude':…, 'body':…, 'children':[…],
            'start':int, 'end':int, 'text':str}
"""
import re


class Node:
    __slots__ = ("kind", "prelude", "body", "children", "start", "end", "text")

    def __init__(self, kind, prelude, body, children, start, end, text):
        self.kind = kind          # 'rule' | 'at' | 'comment'
        self.prelude = prelude    # 选择器 或 @media 的条件文本
        self.body = body          # 花括号内的原文（comment 为 None）
        self.children = children  # 仅 @media 之类有
        self.start = start
        self.end = end
        self.text = text

    def norm(self):
        """归一化文本：压空白、去注释 —— 用于跨文件比对。"""
        return norm(self.text)

    def __repr__(self):
        return "<%s %s>" % (self.kind, self.prelude[:40])


def strip_comments(s):
    """去掉注释，但保留位置（用等长空白替换）—— 便于后续按偏移取原文。"""
    out = []
    i, n = 0, len(s)
    while i < n:
        if s[i:i + 2] == '/*':
            j = s.find('*/', i + 2)
            if j < 0:
                out.append(' ' * (n - i))
                break
            out.append(' ' * (j + 2 - i))
            i = j + 2
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def norm(s):
    """归一化：去注释 + 压空白。"""
    return re.sub(r'\s+', ' ', strip_comments(s)).strip()


def _skip_ws(s, i, n):
    while i < n and s[i] in " \t\r\n":
        i += 1
    return i


def _read_block(s, i, n):
    """从 '{' 开始读一个配平的块。返回 (body_start, body_end, next_i)。
    正确跳过字符串与注释。"""
    assert s[i] == '{'
    depth = 0
    j = i
    in_str = None
    while j < n:
        ch = s[j]
        if in_str:
            if ch == '\\':
                j += 2
                continue
            if ch == in_str:
                in_str = None
            j += 1
            continue
        if ch == '"' or ch == "'":
            in_str = ch
            j += 1
            continue
        if s[j:j + 2] == '/*':
            k = s.find('*/', j + 2)
            j = n if k < 0 else k + 2
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i + 1, j, j + 1
        j += 1
    return i + 1, n, n


def parse(css, start=0, end=None):
    """把 CSS 解析成顶层节点列表。"""
    if end is None:
        end = len(css)
    nodes = []
    i = start
    while i < end:
        # 注释
        if css[i:i + 2] == '/*':
            j = css.find('*/', i + 2)
            j = end if j < 0 else min(j + 2, end)
            nodes.append(Node('comment', '', None, [], i, j, css[i:j]))
            i = j
            continue
        if css[i] in " \t\r\n;":
            i += 1
            continue
        # 读 prelude（到 '{' 或 ';' 为止）
        j = i
        in_str = None
        while j < end:
            ch = css[j]
            if in_str:
                if ch == '\\':
                    j += 2
                    continue
                if ch == in_str:
                    in_str = None
                j += 1
                continue
            if ch == '"' or ch == "'":
                in_str = ch
                j += 1
                continue
            if css[j:j + 2] == '/*':
                k = css.find('*/', j + 2)
                j = end if k < 0 else k + 2
                continue
            if ch == '{' or ch == ';':
                break
            j += 1
        if j >= end:
            break
        if css[j] == ';':
            nodes.append(Node('at', css[i:j].strip(), None, [], i, j + 1, css[i:j + 1]))
            i = j + 1
            continue
        prelude = css[i:j].strip()
        bs, be, ni = _read_block(css, j, end)
        body = css[bs:be]
        kind = 'at' if prelude.startswith('@') else 'rule'
        children = []
        if kind == 'at' and re.match(r'@(media|supports|layer|container)\b', prelude):
            children = parse(css, bs, be)
        nodes.append(Node(kind, prelude, body, children, i, ni, css[i:ni]))
        i = ni
    return nodes


def at_condition(prelude):
    """从 '@media (prefers-color-scheme: dark)' 里取出条件文本。"""
    m = re.match(r'@\w+\s*(.*)$', prelude.strip(), re.S)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''


def all_rules(css):
    """递归取出全部 rule 节点，附带其所在的 at 条件链。"""
    out = []

    def walk(nodes, conds):
        for nd in nodes:
            if nd.kind == 'comment':
                continue
            if nd.kind == 'rule':
                out.append((tuple(conds), nd))
            elif nd.children:
                walk(nd.children, conds + [at_condition(nd.prelude)])
    walk(parse(css), [])
    return out
