"""Publish the supplied game byte for byte; keep download tools on a separate page."""
import argparse
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--game", default="24_深海覺醒_技能按鈕主題美化.html")
args = parser.parse_args()
game = (ROOT / args.game).read_bytes()
docs = ROOT / "docs"
(docs / "index.html").write_bytes(game)
worker = docs / "sw.js"
source, changed = re.subn(r"const EXPECTED_GAME_BYTES = \d+;",
    f"const EXPECTED_GAME_BYTES = {len(game)};", worker.read_text(encoding="utf-8"))
assert changed == 1
worker.write_text(source, encoding="utf-8", newline="\n")
assert (docs / "index.html").read_bytes() == game
print(f"Unmodified homepage: {len(game)} bytes; SHA-256 {hashlib.sha256(game).hexdigest()}")
