#!/bin/bash
# repro pack copy: local absolute paths replaced by <EP_DIR> (this episode dir) and <PYTHON3_13> (a Python 3.13 interpreter); otherwise identical to the file used in the runs (original md5 6e81043e).
# EP02 per-run preparation hook for ab-harness (called after prepare_rundirs.sh created runs/<TAG>/ and its read-only .grok/config.toml).
# usage: prep_run.sh <RUN_DIR> <L> <A|B>
# Copies fixtures/<L>/* to <RUN>/input/ (read-only), builds <RUN>/.venv IN PLACE with uv from the local cache (no copying: copied venvs keep
# shebangs that point outside the run dir, which strict cannot execute). A: base libs. B: base libs + markitdown-mcp 0.0.1a7 + markitdown[all] 0.1.8
# + launcher shim .venv/bin/mdmcp_shim.py. Writes <EP_DIR>/evidence/freeze_<TAG>.txt and input_md5_<TAG>.txt (EP_DIR = parent of runs/).
set -eu
R=$1; L=$2; G=$3; H=<EP_DIR>; TAG=$(basename $R); EPD=$(dirname $(dirname $R))
BASE="pdfplumber==0.11.10 openpyxl==3.1.5 python-pptx==1.0.2 python-docx==1.2.0 pandas==3.0.6"
TOOL="markitdown-mcp==0.0.1a7 markitdown[all]==0.1.8"
[ -e $R/input ] && { echo "input exists, not touched: $R"; exit 0; }
mkdir -p $R/input; cp $H/fixtures/$L/* $R/input/; chmod 444 $R/input/*
uv venv -q --python <PYTHON3_13> $R/.venv
if [ "$G" = B ]; then VIRTUAL_ENV=$R/.venv uv pip install -q $BASE $TOOL; cp $H/tools/mcp_launch_shim.py $R/.venv/bin/mdmcp_shim.py
else VIRTUAL_ENV=$R/.venv uv pip install -q $BASE; fi
mkdir -p $EPD/evidence; VIRTUAL_ENV=$R/.venv uv pip freeze > $EPD/evidence/freeze_$TAG.txt 2>/dev/null
(cd $R && md5sum input/*) > $EPD/evidence/input_md5_$TAG.txt
echo "prep $TAG: $(wc -l < $EPD/evidence/freeze_$TAG.txt) pkgs, inputs $(ls $R/input | tr '\n' ' ')"
