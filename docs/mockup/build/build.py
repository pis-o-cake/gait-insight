"""목업 빌드 — gait-insight-demo.html의 <style> 블록만 다시 조립한다.

HTML(마크업·JS)이 원본이며 직접 편집한다. 스타일은 base-style.css(공통 UX) + skins.py(테마 토큰)에서 조립돼
<style>...</style> 사이를 통째로 교체한다. 그 밖의 내용은 건드리지 않는다.

사용법 (프로젝트 루트에서):
    python3 docs/mockup/build/build.py
"""
import re
import sys
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
HTML = HERE.parent / "gait-insight-demo.html"
sys.path.insert(0, str(HERE))
from skins import SKINS, THEME_ORDER, THEME_DEFAULT, scoped  # noqa: E402


def build() -> None:
    html = HTML.read_text(encoding="utf-8")
    base = (HERE / "base-style.css").read_text(encoding="utf-8")
    css = base + "\n/* ── 테마 토큰 (html[data-theme]) ── */\n" + "".join(scoped(k) for k in THEME_ORDER)
    new, n = re.subn(r"<style>.*?</style>", lambda m: "<style>\n" + css + "</style>", html, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("<style> block not found")
    new = re.sub(r'<meta name="theme-color" content="[^"]*">',
                 '<meta name="theme-color" content="' + SKINS[THEME_DEFAULT]["theme"] + '">', new, count=1)
    # JS의 THEMES 객체와 skins.py가 어긋나지 않았는지 검사 (팔레트 키·기본 팔레트)
    m = re.search(r"var THEMES = (\{.*?\});\n  var THEME_ORDER", new, re.S)
    if not m:
        raise RuntimeError("THEMES object not found in JS")
    js_themes = json.loads(m.group(1))
    for k in THEME_ORDER:
        if k not in js_themes:
            raise RuntimeError("theme %s missing in JS THEMES (edit the HTML)" % k)
        if set(js_themes[k]["palettes"]) != set(SKINS[k]["palettes"]) or js_themes[k]["defaultPal"] != SKINS[k]["default_pal"]:
            raise RuntimeError("theme %s palettes differ between skins.py and JS THEMES" % k)
    HTML.write_text(new, encoding="utf-8")
    print("built", HTML, len(new))


if __name__ == "__main__":
    build()
