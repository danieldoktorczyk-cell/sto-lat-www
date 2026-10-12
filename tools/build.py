"""Buduje sekcję „Nowości” w index.html oraz stronę nowosci.html z content/nowosci.json.
Użycie (z katalogu strony):  python tools/build.py
Edytujesz tylko content/nowosci.json. Znaczniki <!-- NOWOSCI:START --> / <!-- NOWOSCI:END --> w index.html zostają."""
import json, re, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
MIES = ["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca","sierpnia","września","października","listopada","grudnia"]
e = lambda s: html.escape(s, quote=True)
def data_pl(iso):
    if not iso: return ""
    r, m, d = iso.split("-"); return f"{int(d)} {MIES[int(m)-1]} {r}"
d = json.load(open(ROOT/"content"/"nowosci.json", encoding="utf-8"))
wyd, akt = d["wydania"], sorted(d["aktualnosci"], key=lambda x: x["data"], reverse=True)

def naglowek_wydania(w):
    meta = w["status"] if not w.get("data") else f'{w["status"]} · {data_pl(w["data"])}'
    return f'<div class="rel-head"><span class="ver">Wersja {e(w["wersja"])}</span><span class="rtag">{e(w["tytul"])}</span><span class="rmeta">{e(meta)}</span></div>'
def zmiany(w, open_=False):
    li = "".join(f"<li>{e(z)}</li>" for z in w["zmiany"])
    return f'<details class="chg"{" open" if open_ else ""}><summary>Pełna lista zmian ({len(w["zmiany"])})</summary><ul>{li}</ul></details>'
def wyrozniki(w):
    return '<div class="news">' + "".join(f'<div><span class="badge">Nowość</span><div><h3>{e(x["tytul"])}</h3><p>{e(x["opis"])}</p></div></div>' for x in w["wyrozniki"]) + "</div>"
def feed(items):
    return '<div class="feed">' + "".join(f'<article class="item"><time datetime="{e(x["data"])}">{e(data_pl(x["data"]))}</time><div><span class="ftag">{e(x["tag"])}</span><h3>{e(x["tytul"])}</h3><p>{e(x["tekst"])}</p></div></article>' for x in items) + "</div>"

# --- sekcja na stronie głównej ---
w0 = wyd[0]
blok = f'''<!-- NOWOSCI:START (generowane przez tools/build.py, nie edytuj ręcznie) -->
<section id="nowosci">
<p class="eyebrow" style="color:var(--pink)">Nowości</p>
<h2>Co nowego w „Sto lat!”</h2>
<div class="rel">
{naglowek_wydania(w0)}
{wyrozniki(w0)}
{zmiany(w0)}
</div>
<h3 class="sub">Aktualności</h3>
{feed(akt[:3])}
<p class="more"><a href="nowosci.html">Wszystkie nowości i aktualności →</a></p>
</section>
<!-- NOWOSCI:END -->'''
idx = (ROOT/"index.html").read_text(encoding="utf-8")
if "<!-- NOWOSCI:START" in idx:
    idx = re.sub(r"<!-- NOWOSCI:START.*?<!-- NOWOSCI:END -->", lambda m: blok, idx, flags=re.S)
else:
    idx = re.sub(r'<section id="nowosci">.*?</section>', lambda m: blok, idx, count=1, flags=re.S)
CSS = """/* Nowości i aktualności */
.rel{margin-top:32px;padding:28px;border-radius:28px;background:var(--bg3);border:1px solid var(--line)}
.rel-head{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center}
.ver{font-size:24px;font-weight:800;color:var(--white)}
.rtag{padding:4px 14px;border-radius:999px;background:rgba(105,215,190,.14);color:var(--mint);font-size:13px;font-weight:700;letter-spacing:.04em}
.rmeta{color:var(--muted);font-size:14px}
.rel .news{margin-top:20px}
details.chg{margin-top:18px;border-top:1px solid var(--line);padding-top:14px}
details.chg summary{cursor:pointer;font-weight:600;color:var(--white)}
details.chg ul{margin:12px 0 0;padding-left:22px;color:var(--muted);font-size:15px}
details.chg li{margin:6px 0}
h3.sub{margin-top:48px;font-size:22px;font-weight:800}
.feed{margin-top:18px;display:grid;gap:12px}
.feed .item{display:grid;grid-template-columns:150px 1fr;gap:6px 20px;padding:18px 22px;border-radius:20px;background:var(--bg2);border:1px solid var(--line)}
@media (max-width:600px){.feed .item{grid-template-columns:1fr}}
.feed time{color:var(--muted);font-size:14px;padding-top:3px}
.feed h3{font-size:17px;margin:4px 0 2px}
.feed p{margin:0;color:var(--muted);font-size:15px}
.ftag{display:inline-block;padding:2px 10px;border-radius:999px;background:rgba(238,133,173,.16);color:var(--pink);font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase}
.more{margin:22px 0 0}
.rel .news>div{flex-wrap:wrap;gap:10px 14px}
.rel .news>div>div{display:block;padding:0;border:0;background:none;border-radius:0;flex:1 1 220px;min-width:0}
@media (max-width:600px){.rel{padding:20px}}
/* /Nowości */
"""
if "/* Nowości i aktualności */" in idx:
    idx = re.sub(r"/\* Nowości i aktualności \*/.*?/\* /Nowości \*/\n?", lambda m: CSS, idx, flags=re.S)
else:
    idx = idx.replace("</style>", CSS + "</style>", 1)
if 'href="nowosci.html">Nowości</a>' not in idx:
    idx = idx.replace('<a href="polityka-prywatnosci.html">Polityka prywatności</a><a href="mailto', '<a href="nowosci.html">Nowości</a><a href="polityka-prywatnosci.html">Polityka prywatności</a><a href="mailto', 1)
(ROOT/"index.html").write_text(idx, encoding="utf-8")

# --- strona nowosci.html ---
style = re.search(r"<style>.*?</style>", idx, re.S).group(0)
wydania_html = "".join(f'<div class="rel">{naglowek_wydania(w)}{wyrozniki(w)}{zmiany(w, True)}</div>' for w in wyd)
page = f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nowości i aktualności – Sto lat!</title>
<meta name="description" content="Lista zmian w aplikacji Sto lat! i najnowsze wiadomości o aplikacji.">
<meta property="og:title" content="Nowości i aktualności – Sto lat!">
<meta property="og:image" content="https://danieldoktorczyk-cell.github.io/sto-lat-www/og.png">
<link rel="icon" href="icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
{style}
<style>body{{background:linear-gradient(180deg,#130f1d,#1c162a) fixed}}.pg{{padding:40px 24px 80px}}.pg h1{{font-size:clamp(34px,6vw,56px);font-weight:800;letter-spacing:-.02em;margin:24px 0 0}}.top2{{display:flex;justify-content:space-between;align-items:center;padding-top:28px}}</style>
</head>
<body>
<div class="wrap pg">
<div class="top2"><a class="brand" href="./"><img src="icon.png" alt="">Sto lat!</a><a href="./">← Strona główna</a></div>
<h1>Nowości i aktualności</h1>
<h2 style="font-size:24px;margin-top:40px">Wydania</h2>
{wydania_html}
<h2 style="font-size:24px;margin-top:48px">Aktualności</h2>
{feed(akt)}
<footer>
<div class="row"><a class="brand" href="./"><img src="icon.png" alt="" style="width:32px;height:32px;border-radius:9px">Sto lat!</a>
<div class="links"><a href="polityka-prywatnosci.html">Polityka prywatności</a><a href="mailto:stolat.app@gmail.com">Kontakt: stolat.app@gmail.com</a></div></div>
</footer>
</div>
</body>
</html>
'''
(ROOT/"nowosci.html").write_text(page, encoding="utf-8")
print("OK:", len(akt), "aktualności,", len(wyd), "wydań")
