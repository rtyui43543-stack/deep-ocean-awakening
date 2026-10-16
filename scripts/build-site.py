"""Preserve game content; correct the tab version and update existing site workers."""
import argparse
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--game", default="24_深海覺醒_技能按鈕主題美化.html")
args = parser.parse_args()
game = (ROOT / args.game).read_bytes()
old_title = re.search(rb"<title>.*?</title>", game)
assert old_title is not None
title = '<title>深海覺醒：海底冒險 (24版・技能按鈕主題美化)</title>'.encode('utf-8')
updater = b'    <script src="./site-update.js" defer></script>\n'
assert game.count(b'</head>') == 1
homepage = game.replace(old_title.group(), title, 1).replace(b'</head>', updater + b'</head>', 1)
docs = ROOT / "docs"
(docs / "index.html").write_bytes(homepage)
# Old workers only intercept their known asset URLs. This path can reach v24 immediately.
(docs / "play-v24.html").write_bytes(homepage)
worker = docs / "sw.js"
source, changed = re.subn(r"const EXPECTED_GAME_BYTES = \d+;",
    f"const EXPECTED_GAME_BYTES = {len(homepage)};", worker.read_text(encoding="utf-8"))
assert changed == 1
worker.write_text(source, encoding="utf-8", newline="\n")
assert homepage.replace(title, old_title.group(), 1).replace(updater, b'', 1) == game
print(f"Original game preserved except tab title and website updater: {len(homepage)} bytes; SHA-256 {hashlib.sha256(homepage).hexdigest()}")
