# -*- coding: utf-8 -*-
"""按用户要求调整遮罩渐变：**两端实、中间透**，用来盖住图与卡片的接缝。

几何前提（已实测，别再猜）
    卡片      约 348~452 x 181~202（随视口变，宽高比约 1.7~2.5:1）
    题干图    797 x 666（宽高比 1.20:1）
    图的底    纯白（84% 的像素是 #ffffff）

    「保持比例」＋「铺满卡片的高和宽」在数学上不可同时成立：
    保持比例时，若高度铺满，图宽只有卡片宽的 48%~69%，两侧必然留边。
    所以做法是：图按高度居中铺（比例不变），两侧那两条边
    用**底色渐变的两端盖住** —— 两端不透明就等于用卡片底色把那两条边
    连图带缝一起盖掉；中间半透明，图才透出来。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\home-cards.js"
t = io.open(P, encoding="utf-8").read()

# 亮色
old_l = """        : 'linear-gradient(100deg, rgba(255,253,245,1) 0%,'
          + ' rgba(255,253,245,.97) 30%, rgba(253,243,220,.82) 52%,'
          + ' rgba(253,243,220,.58) 100%)';"""
new_l = """        : 'linear-gradient(100deg,'
          + ' rgba(255,253,245,1) 0%, rgba(255,253,245,1) 16%,'
          + ' rgba(255,253,245,.58) 46%, rgba(253,243,220,.58) 54%,'
          + ' rgba(253,243,220,1) 84%, rgba(253,243,220,1) 100%)';"""
if old_l in t:
    t = t.replace(old_l, new_l, 1)
    print("  亮色渐变：两端不透明、中间 .58")
else:
    print("  !! 亮色渐变锚点未匹配")

# 暗色
old_d = """        ? 'linear-gradient(100deg, rgba(36,29,12,1) 0%,'
          + ' rgba(36,29,12,.97) 30%, rgba(43,34,16,.82) 52%,'
          + ' rgba(43,34,16,.58) 100%)';"""
new_d = """        ? 'linear-gradient(100deg,'
          + ' rgba(36,29,12,1) 0%, rgba(36,29,12,1) 16%,'
          + ' rgba(36,29,12,.62) 46%, rgba(43,34,16,.62) 54%,'
          + ' rgba(43,34,16,1) 84%, rgba(43,34,16,1) 100%)';"""
if old_d in t:
    t = t.replace(old_d, new_d, 1)
    print("  暗色渐变：两端不透明、中间 .62")
else:
    print("  !! 暗色渐变锚点未匹配")

# hover 也同步成同样的「两端实、中间透」
hl_old = """a.card.has-bg:hover{--card-veil:linear-gradient(100deg,
  rgba(255,253,245,1) 0%, rgba(255,253,245,.96) 32%,
  rgba(253,243,220,.76) 54%, rgba(251,233,196,.48) 100%)}"""
hl_new = """a.card.has-bg:hover{--card-veil:linear-gradient(100deg,
  rgba(255,253,245,1) 0%, rgba(255,253,245,.99) 16%,
  rgba(255,253,245,.50) 46%, rgba(251,233,196,.50) 54%,
  rgba(251,233,196,.96) 84%, rgba(251,233,196,1) 100%)}"""

io.open(P, "w", encoding="utf-8", newline="").write(t)

# ---- make_pages.py 里的两条 .has-bg 规则同步 ----
M = r"E:\QKMansion\CSX10\w\UME\tools\make_pages.py"
m = io.open(M, encoding="utf-8").read()

# 亮色：基础值也要两端实
ml_old = """a.card.has-bg{--card-veil:linear-gradient(100deg,
  rgba(255,253,245,1) 0%, rgba(255,253,245,.97) 30%,
  rgba(253,243,220,.82) 52%, rgba(253,243,220,.58) 100%)}"""
ml_new = """a.card.has-bg{--card-veil:linear-gradient(100deg,
  rgba(255,253,245,1) 0%, rgba(255,253,245,1) 16%,
  rgba(255,253,245,.58) 46%, rgba(253,243,220,.58) 54%,
  rgba(253,243,220,1) 84%, rgba(253,243,220,1) 100%)}"""
if ml_old in m:
    m = m.replace(ml_old, ml_new, 1)
    print("  make_pages 亮色基础值已同步")
if hl_old in m:
    m = m.replace(hl_old, hl_new, 1)
    print("  make_pages 亮色 hover 已同步")

# 暗色 hover
hd_old = """  a.card.has-bg:hover{--card-veil:linear-gradient(100deg,
    rgba(43,34,16,1) 0%, rgba(43,34,16,.97) 32%,
    rgba(58,45,16,.86) 54%, rgba(58,45,16,.66) 100%)}"""
hd_new = """  a.card.has-bg:hover{--card-veil:linear-gradient(100deg,
    rgba(43,34,16,1) 0%, rgba(43,34,16,.99) 16%,
    rgba(43,34,16,.54) 46%, rgba(58,45,16,.54) 54%,
    rgba(58,45,16,.98) 84%, rgba(58,45,16,1) 100%)}"""
if hd_old in m:
    m = m.replace(hd_old, hd_new, 1)
    print("  make_pages 暗色 hover 已同步")

io.open(M, "w", encoding="utf-8", newline="").write(m)
print("  已写入")
