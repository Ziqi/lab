# 脱敏片段（text-to-cad A/B，2026-10-03）
原始 stream 日志不公开。下面每段都做了脱敏：项目路径换成 <proj>，handson 根目录换成 <handson>，用户主目录换成 ~，守护进程 id 换成 <id>。每段从命中位置开始截取。行号是原始日志的行号，只在内部能查。

## strict 下网格服务不可用（表面报错）（L1-A-1 stream L650）
```
artifact request failed: The geometry service could not accept the request."} ⏎ 
```

## 根因：socket bind 被拒（L1-A-2 stream L1443）
```
self._socket.bind(address) ⏎     ~~~~~~~~~~~~~~~~~^^^^^^^^^ ⏎ PermissionError: [Errno 1] Operation not permitted ⏎ 
```

## snapshot 需要 loopback HTTP（L1-A-1 stream L2491）
```
[cadgen step snapshot] FAILED: SnapshotError: CAD snapshot needs a loopback HTTP server on 127.0.0.1 for its mesh bytes and could not start one: [Errno 1] Operation not permitted.
```

## viewer --detach（L1-A-1 stream L2681）
```
[Errno 1] Operation not permitted ⏎ 
```

## TMPDIR 重定向后 AF_UNIX path too long（L2-A-2 stream L2745）
```
[cadgen-daemon] cannot bind <proj>/runs/L2-A-2/tmp/cadgen-daemon/cadgen-daemon-v2-<id>.sock: AF_UNIX path too long ⏎ [cadgen-daemon] cannot bind <proj>/runs/L2-A-2/tmp/cadgen-daem
```

## 改短 socket 路径仍被拦（L2-A-2 stream L2852）
```
[cadgen-daemon] cannot bind /tmp/cg-l2a2.sock: [Errno 1] Operation not permitted ⏎ [cadgen-daemon] cannot bind /tmp/cg-l2a2.sock: [Errno 1] Operation not permitted ⏎ 
```

## 红线误报命中的代码（旧正则 \border\b）（L2-A-2 stream L4070）
```
order = np.argsort(depth)  # far to near if larger depth is nearer? we'll paint far first if we use painter and larger depth is farther ⏎     # Use z-buffer: nearer = sma
```

## 读上级目录被挡（L3-B-2 stream L60）
```
ls: cannot open directory '<proj>/': Permission denied ⏎ 
```

## 写 ~/.cache 被挡（L3-A-2 stream L2203）
```
touch: cannot touch '~/.cache/write_test': Permission denied ⏎ ok ⏎ 
```

## watchdog 停止（runner.log，L3-A-1）
```
2026-10-03 13:34:01 CST flags: NARROW_RED=1 WATCHDOG_CONTINUE=0 RUNTMP=0
2026-10-03 13:44:11 CST WATCHDOG: no file change 10 min -> stop
2026-10-03 13:44:21 CST grok ended exit=130 stop=watchdog wall=620s
```
