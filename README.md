# FortiGate automatic repack script

version: v0.2

## 使用说明

在执行脚本前，需要在 ori 目录下放置几个文件


1. busybox
2. rev_shell，后门程序，如果不提前放置，在执行脚本时会提示是否自动生成
3. rootfs.gz，从虚拟磁盘提取到的原始 rootfs.gz 文件

此外还需要将 busybox 程序复制到 /bin 目录下， 确保文件 /bin/busybox 存在。

之后执行命令，按照提示操作。

```python
python3 automatic_repack.py
```

## 注意

patch init 需要手动完成，可以直接对 do_halt 函数打补丁，欢迎您帮助完善代码。

仅在 7.2.x vm 版本测试过。

将最终生成的 rootfs.gz 覆盖到原始位置，启动时需要调试内核修改启动参数，请参考文章。

## 相关文章

https://wzt.ac.cn/2023/03/02/fortios_padding/