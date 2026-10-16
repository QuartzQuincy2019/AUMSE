# _q01_orig_snapshot.html

Q01《std 与命名空间初步》**改写前**的原始页面快照（11 节，49,465 字符）。

## 为什么留这个文件

`tools/build_q01_body.py` 要重写 Q01 时，是从**这份原版的片段**里切的
（第 1、2、9 三节的代码块保留了原有的 `hl-*` 高亮标记，手抄必出错）。

**不能从当前页面切** —— 当前 Q01 已经只剩 4 节，脚本第二次运行会
`KeyError: 's9'`，而且第 2 节会重复第 1 节的内容。

生成方式（如需重建）：

```
git show <改造前的提交>:SharingGroup/tutorials/q01-std-and-namespace.html
```

注意：用 PowerShell 的 `>` 重定向会写成 UTF-16，脚本读不了。
要么用 `[System.IO.File]::WriteAllLines` 指定 UTF-8，
要么用 `git show … | Out-File -Encoding utf8`。