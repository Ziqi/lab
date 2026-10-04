#!/usr/bin/env python3
# EP02 quick-test checker (stdlib only; written by CTO, never shown to Grok). Runs outside the sandbox.
# usage: python3 check_markitdown.py --level L1|L2|L3 --run-dir <RUN> --out <check.json>
# Output contract: ab-harness tools/score_run.py (gates{id:{pass}}, top-level f1). Gates (pass/fail, sum 40) and correctness = 20 x cell-level F1 against truth/ (plan section 5).
import argparse, csv, json, re, sys
from pathlib import Path
H = Path(__file__).resolve().parent; TR = H / "truth"
ap = argparse.ArgumentParser(); ap.add_argument("--level", required=True); ap.add_argument("--run-dir", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args(); run = Path(a.run_dir)
if a.level == "ST":  # selftest only: one gate, file exists and has the table row
    ok = (run / "out/smoke.md").exists() and "robot dog" in (run / "out/smoke.md").read_text(errors="ignore")
    json.dump({"schema": "check/1", "level": "ST", "gates": {"G1_smoke_md": {"pass": ok, "points": 40}}, "gate_points": 40 if ok else 0,
               "all_gates_pass": ok, "metrics": {"f1": 1.0 if ok else 0.0}, "correctness_points": 20.0 if ok else 0.0, "f1": 1.0 if ok else 0.0}, open(a.out, "w"), indent=1)
    print(json.dumps({"level": "ST", "pass": ok})); sys.exit(0)
SPEC = {"L1": ("out/parts.csv", "L1_parts.csv", ["part_no"], {"unit_price_cny": 0.01, "stock": 0}),
        "L2": ("out/q3_sales.csv", "L2_q3_sales.csv", ["region", "month", "sku"], {"units": 0, "revenue_cny": 1}),
        "L3": ("out/contracts.csv", "L3_contracts.csv", ["contract_id"], {"amount_cny": 0.01})}
outrel, trf, keycols, num = SPEC[a.level]
truth = list(csv.DictReader(open(TR / trf, newline="")))
head = list(truth[0].keys())
def norm(c, v):
    v = (v or "").strip()
    if c in num:
        try: return float(v.replace(",", "").replace("CNY", "").strip())
        except ValueError: return None
    return v.lower() if c in ("region",) else v
def eq(c, x, y):
    if c in num: return x is not None and y is not None and abs(x - y) <= num[c] + 1e-9
    return x == y
gates = {}; rows = None; got_head = None; err = None
p = run / outrel
try:
    with open(p, newline="", encoding="utf-8-sig") as f:
        rd = csv.reader(f); allr = [r for r in rd if any(x.strip() for x in r)]
    got_head = [x.strip() for x in allr[0]]; rows = [dict(zip(got_head, r)) for r in allr[1:]]
except Exception as e: err = f"{type(e).__name__}: {e}"
ok = rows is not None
gates["G1_file_parses"] = {"pass": ok, "points": 10, "detail": err or str(p.relative_to(run))}
gates["G2_header_exact"] = {"pass": ok and got_head == head, "points": 10, "detail": got_head}
n_exp = len(truth)
if a.level == "L1":
    gates["G3_row_count"] = {"pass": ok and len(rows) == n_exp, "points": 10, "detail": f"{len(rows) if ok else 0}/{n_exp}"}
    bad = [r for r in (rows or []) if re.search(r"Okafor|Vey|Arden|Purchasing|Quality|Logistics", " ".join(r.values()))]
    gates["G4_no_table1_rows"] = {"pass": ok and not bad, "points": 10, "detail": len(bad)}
elif a.level == "L2":
    per = {}
    for r in rows or []: per[(r.get("region") or "").strip().lower()] = per.get((r.get("region") or "").strip().lower(), 0) + 1
    gates["G3_rows_27_and_9_per_region"] = {"pass": ok and len(rows) == 27 and per == {"north": 9, "south": 9, "east": 9}, "points": 10, "detail": per}
    sj = json.load(open(TR / "L2_summary.json")); g4 = False; det = None
    try:
        s = json.load(open(run / "out/summary.json")); det = s
        g4 = int(s.get("rows")) == 27 and abs(float(s.get("total_revenue_cny")) - sj["total_revenue_cny"]) <= 1
    except Exception as e: det = f"{type(e).__name__}: {e}"
    gates["G4_summary_json_correct"] = {"pass": g4, "points": 10, "detail": det}
else:
    ids = [(r.get("contract_id") or "").strip() for r in rows or []]
    gates["G3_ids_clean_unique_count"] = {"pass": ok and len(ids) == n_exp and len(set(ids)) == len(ids) and all(re.fullmatch(r"C-\d{4}", i) for i in ids), "points": 10, "detail": f"{len(ids)}/{n_exp}, bad={[i for i in ids if not re.fullmatch(r'C-[0-9]{4}', i)][:5]}"}
    gates["G4_cancelled_C1017_excluded"] = {"pass": ok and "C-1017" not in ids, "points": 10, "detail": "C-1017" in ids}
# correctness: cell-level F1 over non-key cells, rows matched by key
tk = {tuple(norm(k, r[k]) for k in keycols): r for r in truth}
gk = {}
for r in rows or []:
    try: gk.setdefault(tuple(norm(k, r.get(k)) for k in keycols), r)
    except Exception: pass
valcols = [c for c in head if c not in keycols]
tp = 0; mism = []
for k, t in tk.items():
    g = gk.get(k)
    if not g: continue
    for c in valcols:
        if eq(c, norm(c, g.get(c)), norm(c, t[c])): tp += 1
        elif len(mism) < 15: mism.append({"key": list(k), "col": c, "got": g.get(c), "want": t[c]})
n_t = len(tk) * len(valcols); n_g = len(gk) * len(valcols)
prec = tp / n_g if n_g else 0.0; rec = tp / n_t if n_t else 0.0
f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
out = {"schema": "check/1", "level": a.level, "run_dir": str(run.name), "gates": gates,
       "gate_points": sum(g["points"] for g in gates.values() if g["pass"]), "all_gates_pass": all(g["pass"] for g in gates.values()),
       "metrics": {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4), "tp_cells": tp, "truth_cells": n_t, "got_cells": n_g, "mismatches_first15": mism},
       "correctness_points": round(20 * f1, 2), "f1": round(f1, 4)}
json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)
print(json.dumps({"level": a.level, "gate_points": out["gate_points"], "f1": out["metrics"]["f1"], "all_gates_pass": out["all_gates_pass"]}))
