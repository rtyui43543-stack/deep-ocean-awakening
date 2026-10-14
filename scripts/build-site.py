"""Publish the original full-screen cover, with one secondary download link."""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--game", default="21_深海覺醒_海洋圖鑑清晰版.html")
args = parser.parse_args()
game = (ROOT / args.game).read_bytes()
head = '''
    <!-- Website-only installation metadata and secondary download entry. -->
    <link rel="manifest" href="./manifest.webmanifest">
    <link rel="apple-touch-icon" href="./icons/icon-192.png">
    <link rel="icon" type="image/svg+xml" href="./icons/app-icon.svg">
    <meta name="theme-color" content="#050a1f">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style id="website-download-entry">
        #start-screen #cover-downloads {
            position: absolute; top: 16px; right: 182px;
            display: inline-flex; align-items: center; justify-content: center;
            min-height: 30px; padding: 5px 10px;
            border: 1px solid rgba(204,230,242,.28); border-radius: 7px;
            background: rgba(5,29,48,.74); color: #d0e6ec;
            font-size: clamp(10px,.86vw,12px); font-weight: 500;
            line-height: normal; white-space: nowrap; text-decoration: none;
        }
        #start-screen #cover-downloads:hover { color: #fff; background: rgba(8,57,77,.9); }
        #start-screen #cover-downloads:focus-visible { outline: 3px solid #ffdd9f; outline-offset: 3px; }
        @media (max-height:430px) {
            #start-screen #cover-downloads { top: 10px; right: 158px; min-height: 26px; padding: 4px 7px; }
        }
    </style>
'''.encode("utf-8")
anchor = b'            <button type="button" id="btn-cover-music-source">'
link = '            <a id="cover-downloads" href="./downloads.html">下載／離線</a>\n'.encode("utf-8")
assert game.count(b"</head>") == 1 and game.count(anchor) == 1
homepage = game.replace(b"</head>", head + b"</head>", 1).replace(anchor, link + anchor, 1)
docs = ROOT / "docs"
(docs / "index.html").write_bytes(homepage)
(docs / "game.html").write_text('''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=./">
<title>深海覺醒</title>
<style>html{background:#050a1f;color:#d0e6ec;font-family:sans-serif}a{color:inherit}</style>
<script>location.replace(new URL('./', location.href).href);</script>
</head><body><a href="./">開啟深海覺醒</a></body></html>
''', encoding="utf-8", newline="\n")
worker = docs / "sw.js"
source = worker.read_text(encoding="utf-8")
source, changed = re.subn(r"const EXPECTED_GAME_BYTES = \d+;", f"const EXPECTED_GAME_BYTES = {len(homepage)};", source)
assert changed == 1
worker.write_text(source, encoding="utf-8", newline="\n")
# Only metadata, scoped link CSS, and the download link may differ from the original.
assert homepage.replace(head, b"", 1).replace(link, b"", 1) == game
print(f"Full-screen homepage: {len(homepage)} bytes; original game content preserved")
