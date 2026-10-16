"""Package the original game without changing HTML, media, controls, or rules."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--game", default="24_深海覺醒_技能按鈕主題美化.html")
parser.add_argument("--source-package", type=Path, help="Original complete ZIP to publish unchanged")
parser.add_argument("--site", action="store_true", help="Copy the exact game to the Pages homepage")
args = parser.parse_args()

version = "24.0.0"
game_path = ROOT / args.game
game = game_path.read_bytes()
release = ROOT / ".publish" / "release-v24"
release.mkdir(parents=True, exist_ok=True)
asset_base = "deep-ocean-awakening-v24-offline"
html_path = release / (asset_base + ".html")
html_path.write_bytes(game)

instructions = """深海覺醒・第24版 離線遊玩包

1. 完整下載 ZIP，先解壓縮，不要直接在壓縮檔預覽內開啟遊戲。
2. 雙擊「開始遊戲.html」，使用 Chrome、Edge 或 Firefox 開啟。
3. 圖片、配樂及海洋圖卡已內嵌，之後不需要網路即可遊玩。

本包的開始遊戲.html與提供的第24版HTML完全相同，沒有修改任何遊戲畫面、操作或內容。
原檔的頁籤標題仍顯示第23版，為保留原檔未更名；以第24版檔名及SHA-256辨識版本。

操作：方向鍵移動；Z水砲；X無敵衝刺；P或Esc暫停。
手機／平板請橫向使用，觸控裝置使用左下搖桿及右下技能鍵。
暫停選單可放棄本次闖關返回首頁。
水砲3能量、冷卻1秒；無敵衝刺5能量、持續2秒、冷卻6秒。

手機和平板的本機HTML開啟方式依瀏覽器而異。
若無法開啟下載檔，可連網到下方「下載與離線準備」頁，按「準備手機／平板離線遊玩」，
等待成功後點「返回遊戲」。之後使用同一個瀏覽器及遊戲網址。
保留瀏覽器網站資料；清除資料或裝置自動清出儲存空間後，需要重新準備。
來源與授權的外部網頁仍需網路，圖鑑閱讀和遊戲本身不需要。

線上遊戲：https://rtyui43543-stack.github.io/deep-ocean-awakening/
下載與離線準備：https://rtyui43543-stack.github.io/deep-ocean-awakening/downloads.html
完整資料包：https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/tag/v24.0.0

第一、二關配樂為Call to Adventure；第三關為Chest of Adventure。
請保留本包內配樂署名、授權及修改說明，遊戲內「配樂來源」亦可閱讀。
"""
contents = {
    "深海覺醒_離線版/開始遊戲.html": game,
    "深海覺醒_離線版/離線遊玩說明.txt": instructions.encode("utf-8-sig"),
    "深海覺醒_離線版/配樂署名與修改說明.txt": (ROOT / "credits" / "配樂署名與修改說明.txt").read_bytes(),
    "深海覺醒_離線版/海洋圖卡來源.txt": (ROOT / "credits" / "海洋圖卡來源.txt").read_bytes(),
}
zip_path = release / (asset_base + ".zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for name, data in contents.items():
        info = zipfile.ZipInfo(name, date_time=(2026, 10, 16, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
with zipfile.ZipFile(zip_path) as archive:
    assert archive.testzip() is None
    assert archive.read("深海覺醒_離線版/開始遊戲.html") == game

digest = lambda data: hashlib.sha256(data).hexdigest()
manifest = {
    "version": version, "source_game": game_path.name,
    "game_bytes": len(game), "game_sha256": digest(game),
    "zip_bytes": zip_path.stat().st_size, "zip_sha256": digest(zip_path.read_bytes()),
    "zip_contents": list(contents), "html_asset": html_path.name, "zip_asset": zip_path.name,
    "handoff_files": {p.name: digest(p.read_bytes()) for p in sorted((ROOT / "handoff-v24").iterdir()) if p.is_file()},
}
if args.source_package:
    original = args.source_package.read_bytes()
    complete = release / "deep-ocean-awakening-v24-complete.zip"
    complete.write_bytes(original)
    with zipfile.ZipFile(complete) as archive:
        assert archive.testzip() is None
        games = [n for n in archive.namelist() if n.endswith(".html")]
        assert len(games) == 1 and archive.read(games[0]) == game
        for name, sha in manifest["handoff_files"].items():
            matches = [n for n in archive.namelist() if n.endswith("/" + name)]
            assert len(matches) == 1 and digest(archive.read(matches[0])) == sha
    manifest["complete_package"] = {"original_name": args.source_package.name, "asset": complete.name,
                                    "bytes": len(original), "sha256": digest(original)}
if args.site:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build-site.py"), "--game", args.game], check=True)
    assert (ROOT / "docs" / "index.html").read_bytes() == game
(release / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=True))
