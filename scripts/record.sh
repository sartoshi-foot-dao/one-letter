#!/bin/sh
# Re-record the data the film shows. Needs CPython 3.11 (the recorder restates its random.choices).
#   sh scripts/record.sh
# 1. fetch microgpt.py and names.txt (pinned, hash-checked)
# 2. run unmodified microgpt.py      -> assets/reference-run.log
# 3. run the instrumented copy       -> assets/trace.json (+ assets/trace-run.log)
# 4. accept or reject the trace and apply the featured-step rule -> assets/featured.json
set -eu
cd "$(dirname "$0")/.."
sh scripts/fetch_microgpt.sh
(cd third_party && python3 microgpt.py) > assets/reference-run.log
python3 src/record_trace.py > assets/trace-run.log
python3 src/check_trace.py
