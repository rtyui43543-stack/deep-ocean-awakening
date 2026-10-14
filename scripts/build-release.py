"""Build the exact offline game and its student ZIP; copy the verified Pages shell."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--game", default="20_深海覺醒_挑戰與技能特效強化版.html")
parser.add_argument("--site", action="store_true", help="Copy the complete .publish/site shell to docs")
args = parser.parse_args()
game_path = ROOT / args.game
game = game_path.read_bytes()
stage = ROOT / ".publish"
release = stage / "release"
release.mkdir(parents=True, exist_ok=True)
version = "20.0.0"
asset_base = "deep-ocean-awakening-v20-offline"
html_path = release / (asset_base + ".html")
html_path.write_bytes(game)

instructions = """深海覺醒・海豚騎士的大冒險 第20版

電腦離線遊玩
1. 完整下載 ZIP，先解壓縮，不要直接在壓縮檔預覽內開啟遊戲。
2. 雙擊「開始遊戲.html」，使用 Chrome、Edge 或 Firefox 開啟。
3. 圖片、配樂和海洋圖卡已內嵌，之後不需要網路即可遊玩。

手機與平板
在下載檔案可由瀏覽器開啟並執行HTML的裝置上，可以開啟上述遊戲檔。
iPhone/iPad請先連網使用Safari開啟網站，選分享→加入主畫面，再從該圖示開啟，按「準備手機／平板離線遊玩」並等待成功。
Android或其他裝置可先在瀏覽器準備完成，再用安裝/加入主畫面選單；之後從同一個瀏覽器或圖示進入。
請保留瀏覽器的網站資料；若清除網站資料，需重新連網準備離線內容。
手機、平板遊戲畫面請橫向使用。圖卡、配樂作者與資料來源的外部連結仍需網路。

操作：方向鍵移動；Z水砲；X無敵衝刺；P或Esc暫停。
觸控：左下方向鍵、右下技能鍵；右上暫停可放棄本次闖關返回首頁。
水砲3能量、冷卻1秒；無敵衝刺5能量、持續2秒、冷卻6秒。
第一、二關配樂為Call to Adventure；第三關為Chest of Adventure。

網站：https://rtyui43543-stack.github.io/deep-ocean-awakening/
專案：https://github.com/rtyui43543-stack/deep-ocean-awakening
下載：https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/tag/v20.0.0

請保留本包內配樂署名、授權與修改說明；遊戲內「配樂來源」亦可閱讀。
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
        info = zipfile.ZipInfo(name, date_time=(2026, 10, 14, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
with zipfile.ZipFile(zip_path) as archive:
    assert archive.testzip() is None
    assert archive.read("深海覺醒_離線版/開始遊戲.html") == game
manifest = {"version": version, "game_bytes": len(game), "game_sha256": hashlib.sha256(game).hexdigest(),
            "zip_bytes": zip_path.stat().st_size, "zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
            "zip_contents": list(contents), "html_asset": html_path.name, "zip_asset": zip_path.name}
(release / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
if args.site:
    if (stage / "site" / "index.html").exists():
        shutil.copytree(stage / "site", ROOT / "docs", dirs_exist_ok=True)
    else:
        assert (ROOT / "docs" / "index.html").exists(), "Pages shell docs/index.html is missing"
    (ROOT / "docs" / "game.html").write_bytes(game)
    (ROOT / "docs" / ".nojekyll").write_text("", encoding="utf-8")
    assert (ROOT / "docs" / "game.html").read_bytes() == game
print(json.dumps(manifest, ensure_ascii=True))
