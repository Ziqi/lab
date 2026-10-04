# Grok+一个工具 第2期 MarkItDown MCP 工具 快测 N=1 复现包

日期：2026年10月4日（6 次运行在 06:11 至 07:28 北京时间之间依次完成，07:47 汇总）
工具：MarkItDown MCP 工具（microsoft/markitdown 的 markitdown-mcp 0.0.1a7，仅 MCP 服务器，一个工具 convert_to_markdown）
分组：A 组 Grok 单独做，B 组 Grok + MarkItDown MCP 工具（注意：与第 1 期命名相反）
规模：快测 N=1，L1、L2、L3 每级每组 1 次，共 6 次。样本极小，只是观察，不是结论
资料：全部是我们自己生成的虚构文件（公司名、人名、金额都是虚构的）
原始流式日志、会话文件、录屏、Grok 本机配置和登录文件都不公开，也不在本目录

## 结果（数字取自 results/*.score.json）
| 级别 | A 总分 | B 总分 | A 成功 | B 成功 |
|---|---|---|---|---|
| L1 | 100.0 | 100.0 | 1/1 | 1/1 |
| L2 | 100.0 | 100.0 | 1/1 | 1/1 |
| L3 | 93.4 | 93.3 | 1/1 | 1/1 |

每次运行的分项、用时、token、续跑见 results/summary.md。

## 目录
- prompts/L1.txt、L2.txt、L3.txt：三级提示词，A、B 两组完全相同（同一个文件）。continue.txt：看门狗触发后 -c 续跑用的提示词（两组相同）
- gen/gen_fixtures.py：生成全部输入文件（pdf、xlsx、pptx、docx）和标准答案，随机种子固定。gen/requirements.txt：生成脚本用的 Python 包。gen/fixtures_md5_used_in_runs.txt：正式运行用的输入文件 md5
- truth/：标准答案（gen_fixtures.py 生成，运行时放在运行目录外，Grok 看不到）
- check_markitdown.py：检查脚本，只用 Python 标准库，输出 check.json。score_spec.json：门分值和计分参数（跑前冻结）
- config/config_A.toml、config_B.toml：两组唯一不同的配置文件（见下）。config/mcp_launch_shim.py：B 组 MCP 启动垫片。config/prep_run.sh、config/episode.env：每次运行的准备脚本和 harness 参数（本机路径已换成占位符）
- harness/score_run.py、redline_scan.py：100 分制计分和红线扫描（已打补丁的版本，即正式运行实际用的版本）。harness/ab-harness-ep02.patch：本期对 harness 的补丁
- versions/：A、B 两组运行目录 .venv 的 pip freeze（A 19 个包，B 75 个包）
- results/：6 次运行的 score.json、check.json 和汇总表
- SHA256SUMS：本目录全部文件的 sha256

## A、B 两组差在哪里
相同：提示词、模型 grok-4.7、effort xhigh、--sandbox strict、--disable-web-search、--always-approve、--no-auto-update、订阅登录（不用 API key）、GROK_FOLDER_TRUST=0、两组都在运行目录配置里禁用全局启用的 text-to-cad 插件（grok inspect 里它仍显示为用户作用域 enabled，但两组都是 0 个该插件的 skill、没有 cad MCP；正式运行的 grok inspect 存证未放进本包）、开跑前的同配置自测里两组都加载了 Grok 内置的 pdf、docx、pptx skill（xAI，Grok Build 内置 skill；正式运行的存证没有记录 skill 名单）、两组 .venv 里同样的 5 个解析库（pdfplumber、openpyxl、python-pptx、python-docx、pandas，连依赖共 19 个包，同版本）。
不同：
1. B 组运行目录的 .grok/config.toml 多一段 project 作用域的 MCP 配置：
```
[mcp_servers.markitdown]
command = "${PWD}/.venv/bin/python"
args = ["${PWD}/.venv/bin/mdmcp_shim.py"]
startup_timeout_sec = 60
```
2. B 组 .venv 多装 markitdown-mcp 0.0.1a7 和 markitdown[all] 0.1.8（连依赖多 56 个包，完整列表对比 versions/freeze_A.txt 和 freeze_B.txt），所以 B 组也能直接 import markitdown。
3. B 组 .venv/bin/mdmcp_shim.py = config/mcp_launch_shim.py。strict 沙箱挡住了 asyncio 自唤醒用的本地 socket 写入，不加垫片时 MCP 服务器收不到握手、超时。垫片只把每次 select 等待限制在 50 毫秒，不改 markitdown 或 markitdown-mcp 的代码。
4. GROK_FOLDER_TRUST=0 两组都加：headless 下 project 作用域的 MCP 受文件夹信任门控，不加时 B 组工具不可用。只加在这次进程的环境变量里，不写全局信任文件。
开跑前后用 grok inspect 核对：A 组 MCP 服务器为 none，B 组为 markitdown，不符即作废。6 次都符合，没有作废。

## 版本
| 项 | 值 |
|---|---|
| Grok | Grok Build CLI 1.0.46，模型 grok-4.7，effort xhigh |
| MCP 工具 | markitdown-mcp 0.0.1a7（MIT），markitdown[all] 0.1.8，mcp 2.3.0，magika 0.6.3，onnxruntime 1.30.0 |
| Python | 3.13.5（运行目录 .venv 和生成脚本都用它），venv 用 uv 0.12.15 建 |
| A 组解析库 | pdfplumber 0.11.10，openpyxl 3.1.5，python-pptx 1.0.2，python-docx 1.2.0，pandas 3.0.6 |
| 生成脚本 | Python 包见 gen/requirements.txt；pdf 由 LibreOffice 25.2.3.2（soffice --headless）从 HTML 转出 |

## 怎么复现
1. 生成输入和标准答案（不需要 Grok）：
```
python3 -m venv .venv-gen && .venv-gen/bin/pip install -r gen/requirements.txt
.venv-gen/bin/python gen/gen_fixtures.py      # 写到 fixtures/L1..L3/ 和 truth/，打印 L1 12 L2 27 L3 23
```
需要系统里有 soffice。truth/ 逐字节可复现；pdf、xlsx、pptx、docx 都带生成时间，重新生成的这四类文件字节和 gen/fixtures_md5_used_in_runs.txt 不同，内容相同。
2. 运行目录：runs/<级别>-<组>-1/ 下放 input/（该级输入，只读）、.venv（按 config/prep_run.sh 建）、.grok/config.toml（A 用 config_A.toml，B 用 config_B.toml，只读）。在运行目录里运行：
```
env -u XAI_API_KEY GROK_FOLDER_TRUST=0 PATH=<RUN>/.venv/bin:$PATH VIRTUAL_ENV=<RUN>/.venv grok -p "$(cat <PACK>/prompts/L1.txt)" --model grok-4.7 --effort xhigh --always-approve --sandbox strict --disable-web-search --no-auto-update --output-format streaming-json --cwd <RUN>
```
每次总时长上限 600 秒；240 秒没有文件产出时用 -c 和 prompts/continue.txt 在同一会话续跑 1 次（算 1 次人工干预，扣 5 分）。
3. 检查和计分：
```
python3 check_markitdown.py --level L1 --run-dir <RUN> --out check.json
```
计分用 harness/score_run.py（需要运行日志目录结构，见文件开头说明），参数 score_spec.json。100 分 = 完成 40 + 正确 20（单元格级 F1）+ 人工干预 15 + 耗时 10 + 成本 10 + 安全 5，成功线 70。

<PACK> 是本复现包目录，<RUN> 是运行目录；config/prep_run.sh 和 config/episode.env 里的 <EP_DIR>、<GROK_BIN>、<PYTHON3_13>、<TMPDIR> 是占位符，换成自己机器上的路径。prep_run.sh 默认从 <EP_DIR>/fixtures/<级别>/ 取输入、从 <EP_DIR>/tools/mcp_launch_shim.py 取垫片。

## 已知情况
- MarkItDown 来自 Microsoft 开源项目 microsoft/markitdown（MIT 许可）。本包不含它的代码，只钉了版本（见 versions/）。
- ab-harness-ep02.patch 改动的 prepare_rundirs.sh 和 run_one.sh 不在本包里，所以 score_run.py 不能只靠本包重跑。
- harness/score_run.py 和 ab-harness-ep02.patch 的安全分正则里写有本机主目录和工作目录的路径前缀：它们是用来识别 Grok 有没有越界读写的匹配规则，不是本包的文件位置，按原样保留以便和正式运行一致。
- gen_fixtures.py 和 check_markitdown.py 里的人名（L1 联系人表）是虚构测试数据。
