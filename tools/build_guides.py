"""이사 체크리스트(정적 사이트)용 가이드 빌드.

사용법:  python tools/build_guides.py
- guides/*.md → guide/<이름>.html, guide/index.html
- index.html 의 <!--GUIDES-->…<!--/GUIDES--> 사이를 가이드 카드로 바꿈
- sitemap.xml 에 /guide/ 주소 추가
- upload/site.zip 대신 쓸 site.zip 을 이 폴더에 만듦 (guide/ 포함)
"""
import datetime
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import guides as G  # noqa: E402

URL = "https://isa-checklist.pages.dev"
index = (ROOT / "index.html").read_text(encoding="utf-8")
gs = G.build(ROOT, ROOT, {
    "url": URL, "name": "이사 체크리스트", "theme": "#3182f6",
    "colors": {"accent": "#3182f6", "soft": "#e8f3ff", "text": "#1b64da"},
    "index_html": index,
    "footer": "이 글은 일반적인 정보를 정리한 참고 자료입니다. 행정 절차와 기한은 관할 기관의 최신 안내를 확인해 주세요.",
    "goatcounter": "isachecklist",
})

card = "<!--GUIDES-->\n" + G.card(gs) + "<!--/GUIDES-->"
if "<!--GUIDES-->" in index:
    index = re.sub(r"<!--GUIDES-->.*?<!--/GUIDES-->", lambda m: card, index, flags=re.S)
else:
    anchor = '  <section class="card">\n    <h2>함께 보면 좋은 체크리스트</h2>'
    index = index.replace(anchor, card + "\n" + anchor, 1)
(ROOT / "index.html").write_text(index, encoding="utf-8")

today = datetime.date.today().isoformat()
sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
sm = "\n".join(l for l in sm.split("\n") if "/guide/" not in l)
add = "".join(f"  <url><loc>{URL}{p}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n"
              for p, pr in [("/guide/", "0.7")] + [(f"/guide/{g['slug']}", "0.8") for g in gs])
sm = sm.replace("</urlset>", add + "</urlset>")
(ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")

with zipfile.ZipFile(ROOT / "site.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in ["index.html", "offers.html", "404.html", "og.png", "robots.txt", "sitemap.xml"]:
        z.write(ROOT / f, f)
    for f in sorted((ROOT / "guide").glob("*.html")):
        z.write(f, "guide/" + f.name)
print(f"가이드 {len(gs)}편 · site.zip 생성")
