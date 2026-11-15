#!/bin/sh
# Download the two inputs this film is recorded from. Neither is redistributed in this repo.
#   microgpt.py: Andrej Karpathy's gist, pinned to revision 14fb038 (2026-02-16)
#   names.txt:   karpathy/makemore at commit 988aa59 (MIT licence), saved as input.txt,
#                which is the file name microgpt.py reads from its working directory
# Both are checked against SHA-256 and the script fails on any mismatch.
set -eu
DIR=$(cd "$(dirname "$0")/.." && pwd)/third_party
mkdir -p "$DIR"
GIST=https://gist.githubusercontent.com/karpathy/8627fe009c40f57531cb18360106ce95/raw/14fb038816c7aae0bb9342c2dbf1a51dd134a5ff/microgpt.py
NAMES=https://raw.githubusercontent.com/karpathy/makemore/988aa59/names.txt
get() {  # url file sha256
  [ -f "$DIR/$2" ] || curl -fsSL -o "$DIR/$2" "$1"
  got=$(python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$DIR/$2")
  [ "$got" = "$3" ] || { echo "SHA-256 mismatch for $2: $got" >&2; rm -f "$DIR/$2"; exit 1; }
  echo "ok $2 $3"
}
get "$GIST"  microgpt.py d47d88c2fd432c8ebdc1048beab7f7eb64ea7e0e664e11b812d72a6d95ebccee
get "$NAMES" input.txt   0a30b5557f192f32ab962680889aac5f6fda0f4cecf40a6d0b5694f58ea8cc4d
