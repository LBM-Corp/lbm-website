#!/usr/bin/env python3
"""
LBM Corporation — static site generator.

    python3 build.py

Reads data/site.json, writes index.html, esg.html and brand/*.html.
assets/ is checked in as-is.
"""
import json, os, html, urllib.parse, hashlib


def _v(rel):
    """Content hash so browsers and CDNs pick up CSS/JS changes immediately."""
    try:
        return "?v=" + hashlib.md5(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:8]
    except OSError:
        return ""


ROOT = os.path.dirname(os.path.abspath(__file__))
D    = json.load(open(os.path.join(ROOT, "data/site.json"), encoding="utf-8"))
CO, BRANDS, ESG = D["company"], D["brands"], D["esg"]
KEY = {"london-bagel-museum": "lbm", "artist-bakery": "ab",
       "cafe-layered": "cl", "cafe-highwaist": "hw"}

# Written by _claude/ig_sync.py from the official Instagram API. Absent until
# LBM runs the sync; the feed falls back to brand photography until then.
try:
    IG = json.load(open(os.path.join(ROOT, "data/instagram.json"), encoding="utf-8"))
except (OSError, ValueError):
    IG = {}

e = lambda s: html.escape(str(s or ""), quote=True)
TODO = lambda v: (not v) or str(v).strip().upper().startswith("TODO")
naver = lambda q: "https://map.naver.com/p/search/" + urllib.parse.quote(q)


# ---------------------------------------------------------------- chrome
def head(title, desc, brand=None, depth=0, flat=False, path="", noindex=False):
    up = "../" * depth
    cls = ' class="flat"' if flat else ""
    return f"""<!doctype html>
<html lang="ko"{f' data-brand="{brand}"' if brand else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#1A120C">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
{'<meta name="robots" content="noindex">' if noindex else ''}
{f'<link rel="canonical" href="https://lbmcorporation.com/{path}">' if path else ''}
{f'<meta property="og:url" content="https://lbmcorporation.com/{path}">' if path else ''}
<meta property="og:site_name" content="{e(CO['nameEn'])}">
<meta property="og:image" content="https://lbmcorporation.com/assets/img/og-cover.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="{up}assets/img/favicon-32.png{_v("assets/img/favicon-32.png")}">
<link rel="icon" type="image/png" sizes="512x512" href="{up}assets/img/favicon-512.png{_v("assets/img/favicon-512.png")}">
<link rel="apple-touch-icon" href="{up}assets/img/apple-touch-icon.png{_v("assets/img/apple-touch-icon.png")}">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{up}assets/css/main.css{_v("assets/css/main.css")}">
<script>document.documentElement.className+=" js";</script>
</head>
<body{cls}>"""


def header(active, depth=0):
    """브랜드 and 매장 are one thing: pick a brand, then its stores.
    The nav item opens a panel of the four official marks, set to equal optical size."""
    up = "../" * depth

    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{up}{href}"{cur}>{label}</a>'

    mega = "".join(
        f'<a class="mega__i" data-card="{KEY[b["slug"]]}" href="{up}brand/{b["slug"]}.html">'
        f'<span class="mega__shot"><img src="{up}assets/img/nav-{KEY[b["slug"]]}-1080.jpg'
        f'{_v("assets/img/nav-" + KEY[b["slug"]] + "-1080.jpg")}" alt="" loading="lazy"></span>'
        f'<span class="mega__mark"><img src="{up}assets/img/logo-{KEY[b["slug"]]}.png{_v("assets/img/logo-" + KEY[b["slug"]] + ".png")}" alt="{e(b["nameEn"])}"></span>'
        f'<span class="mega__cat">{e(b["category"])}</span>'
        f'<b class="mega__name">{e(b["nameEn"])}</b>'
        f'<span class="mega__go">매장 {len(b["locations"])}곳 <i></i></span></a>'
        for b in BRANDS)

    cur_b = ' aria-current="page"' if active in ("brands", "stores") else ""
    return f"""
<header class="hdr">
  <a class="hdr__mark" href="{up}index.html" aria-label="LBM Corporation">
    <b>LBM Corporation</b></a>
  <nav class="nav">
    <div class="nav__has">
      <a class="nav__brands" href="{up}index.html#brands" aria-expanded="false" aria-controls="mega"{cur_b}>Brands</a>
    </div>
    {a('esg.html', 'Newsroom', 'esg')}
  </nav>
  <button class="burger" aria-label="메뉴"><i></i><i></i></button>
</header>
<div class="mega" id="mega" hidden>
  <div class="wrap"><div class="mega__in">{mega}</div></div>
</div>"""


def footer(depth=0):
    up = "../" * depth
    links  = "".join(f'<li><a href="{e(l["href"])}">{e(l["label"])}</a></li>' for l in D["footer"]["links"])
    brands = "".join(f'<li><a href="{up}brand/{b["slug"]}.html">{e(b["nameEn"])}</a></li>' for b in BRANDS)
    socials = "".join(
        f'<a href="{e(b["instagram"])}" target="_blank" rel="noopener" '
        f'title="{e(b["nameEn"])} Instagram">{KEY[b["slug"]].upper()}</a>' for b in BRANDS)
    addr = f"{CO['address']}\n대표: {CO['ceo']}\n문의: {CO['email']}"
    return f"""
<footer class="ft">
  <div class="wrap">
    <div class="ft__top">
      <div class="ft__mark">
        <b>LBM Corporation</b><span>주식회사 엘비엠</span>
        <div class="ft__addr">{e(addr)}</div>
      </div>
      <div><h4>Brands</h4><ul>{brands}</ul></div>
      <div><h4>Company</h4><ul>
        <li><a href="{up}index.html#company">회사 소개</a></li>
        <li><a href="{up}esg.html">ESG</a></li>
        <li><a href="mailto:{e(CO['email'])}">제휴 · 문의</a></li>
      </ul></div>
    </div>
  </div>
  <div class="wrap">
    <div class="ft__bar">
      <div class="ft__policy">{links}<span>{e(CO['footerLegal'])}</span></div>
      <div class="ft__social">{socials}</div>
    </div>
  </div>
</footer>
<button class="totop" aria-label="맨 위로">&uarr;</button>
<script src="{up}assets/js/main.js{_v("assets/js/main.js")}"></script>
</body></html>"""


# ---------------------------------------------------------------- blocks
def sec(num, label, inner, sid="", cls="", head_html=""):
    return f"""
<section class="sec {cls}"{f' id="{sid}"' if sid else ''}>
  <div class="wrap"><div class="sec__grid">
    <div class="sec__body">{head_html}{inner}</div>
  </div></div>
</section>"""


def quote(q, lead=False, tag=""):
    """Museum wall-text. Their own words, set large."""
    return f"""
<figure class="quote{' quote--lead' if lead else ''}{' quote--stmt' if q.get('statement') else ''}" data-rise>
  <blockquote>{e(q['text'])}</blockquote>
  <figcaption><i></i><b>{e(q['by'])}</b>{f'<span>{e(q["role"])}</span>' if q.get('role') else ''}{tag}</figcaption>
</figure>"""


def quote_band(q, cls="sec--paper"):
    return f"""
<section class="sec sec--tight {cls}">
  <div class="wrap"><div class="sec__grid">
    <div class="sec__body">{quote(q, lead=True)}</div>
  </div></div>
</section>"""



def band(img, eyebrow, head, body="", depth=0):
    up = "../" * depth
    return f"""
<section class="band">
  <img src="{up}assets/img/{img}-2600.jpg"
       srcset="{up}assets/img/{img}-1600.jpg 1600w, {up}assets/img/{img}-2600.jpg 2600w"
       sizes="100vw" alt="" loading="lazy" decoding="async">
  <div class="band__in"><div data-rise>
    <p class="eyebrow">{eyebrow}</p>
    <h2 class="h-lg">{head}</h2>
    {f'<p>{body}</p>' if body else ''}
  </div></div>
</section>"""


def band_quote(img, q, depth=0):
    up = "../" * depth
    return f"""
<section class="band band--quote{' band--stmt' if q.get('statement') else ''}">
  <img src="{up}assets/img/{img}-2600.jpg"
       srcset="{up}assets/img/{img}-1600.jpg 1600w, {up}assets/img/{img}-2600.jpg 2600w"
       sizes="100vw" alt="" loading="lazy" decoding="async">
  <div class="band__in"><figure style="margin:0" data-rise>
    <blockquote>{e(q['text'])}</blockquote>
    <figcaption><b>{e(q['by'])}</b>{f" &middot; {e(q['role'])}" if q.get('role') else ''}</figcaption>
  </figure></div>
</section>"""


def gallery(prefix, alt, depth=0, n=3):
    up = "../" * depth
    return ('<div class="gal" data-rise>' + "".join(
        f'<figure style="margin:0"><img src="{up}assets/img/{prefix}-{i}-1800.jpg" '
        f'srcset="{up}assets/img/{prefix}-{i}-1200.jpg 1200w, {up}assets/img/{prefix}-{i}-1800.jpg 1200w" '
        f'sizes="33vw" alt="{e(alt)}" loading="lazy" decoding="async"></figure>'
        for i in range(1, n + 1)) + '</div>')


def subnav(brand, depth=1):
    up = "../" * depth
    items = [("#story", "Story"), ("#space", "Space"),
             ("#stores", f"매장 {len(brand['locations'])}곳"), ("#feed", "Instagram")]
    links = "".join(
        f'<a href="{h}"{" class=" + chr(34) + "is-store" + chr(34) if h == "#stores" else ""}>{lab}</a>'
        for h, lab in items)
    return f"""
<div class="subnav"><div class="wrap"><div class="subnav__in">
  <span class="subnav__brand"><img src="{up}assets/img/logo-{KEY[brand["slug"]]}-w.png" alt="{e(brand["nameEn"])}"></span>{links}
</div></div></div>"""


def locations_block(brand, depth=1):
    """Editorial index rows. A card grid read like a store directory; rows give the
    photography room and let each store carry its own line of type."""
    up = "../" * depth
    out = []
    for n, L in enumerate(brand["locations"], 1):
        hours = "" if TODO(L.get("hours")) else \
            f'<div class="strow__r"><b>Hours</b><span>{e(L["hours"])}</span></div>'
        thumbs = "".join(
            f'<button type="button" data-full="{up}assets/img/{L["id"]}-{r}-1080.jpg" '
            f'aria-label="{e(L["name"])} {lab}">'
            f'<img src="{up}assets/img/{L["id"]}-{r}-540.jpg" '
            f'alt="{e(brand["nameEn"])} {e(L["name"])} {lab}" loading="lazy" decoding="async"></button>'
            for r, lab in (("b", "공간"), ("c", "메뉴"), ("d", "디테일")))
        out.append(f"""
      <article class="strow{' strow--flip' if n % 2 == 0 else ''}" data-rise>
        <div class="strow__n">{n:02d}</div>
        <div class="strow__body">
          <h3><span class="strow__name">{e(L['name'])}</span><span class="strow__en">{e(L['nameEn'])}</span></h3>
          <p class="strow__note">{e(L['note'])}</p>
          <div class="strow__rows">
            <div class="strow__r"><b>Address</b><span>{e(L['address'])}</span></div>
            <div class="strow__r"><b>Opened</b><span>{e(L['opened'])}</span></div>
            {hours}
          </div>
          <div class="strow__map-wrap">
          <a class="strow__map" href="{naver(brand['nameKo'] + ' ' + L['name'])}" target="_blank" rel="noopener">네이버 지도 <i></i></a>
          <a class="mapcard" href="{naver(brand['nameKo'] + ' ' + L['name'])}" target="_blank" rel="noopener" tabindex="-1">
            <span class="mapcard__map">
              <img src="{up}assets/img/map/{L['id']}.jpg" alt="" decoding="async">
              <span class="mapcard__pin"></span>
            </span>
            <div class="mapcard__body">
            <b class="mapcard__name">{e(brand['nameEn'])} {e(L['name'])}</b>
            <span class="mapcard__addr">{e(L['address'])}</span>
            {f'<span class="mapcard__row"><i>영업</i>{e(L["hours"])}</span>' if not TODO(L.get("hours")) else ''}
            <span class="mapcard__row"><i>오픈</i>{e(L['opened'])}</span>
            <span class="mapcard__go">네이버 지도에서 열기 &rarr;</span>
            </div>
          </a>
        </div>
        <div class="strow__links">
          {f'<a class="strow__map" href="{e(L["catchtable"])}" target="_blank" rel="noopener">캐치테이블 <i></i></a>' if L.get("catchtable") else ''}
        </div>
        </div>
        <div class="strow__media">
          <div class="strow__hero">
            <img class="loc__main" src="{up}assets/img/{L['id']}-row-1800.jpg"
                 srcset="{up}assets/img/{L['id']}-row-1800.jpg 1800w"
                 sizes="46vw" alt="{e(brand['nameEn'])} {e(L['name'])}" loading="lazy" decoding="async">
          </div>
          <div class="strow__thumbs">{thumbs}</div>
        </div>
      </article>""")
    return f'<div class="stores">{"".join(out)}</div>'


def ig_block(brand, depth=1):
    """A profile card, not a bare link. Handle, name and bio are real; the
    tiles are the brand's own photography standing in until LBM supplies
    live posts (see README-INSTAGRAM.md)."""
    up = "../" * depth
    k = KEY[brand["slug"]]
    ct = ""
    if brand.get("catchtable") and not TODO(brand["catchtable"]):
        ct = f'<a class="btn" href="{e(brand["catchtable"])}" target="_blank" rel="noopener">캐치테이블 예약</a>'
    elif brand.get("catchtable"):
        ct = ('<a class="btn" href="https://app.catchtable.co.kr/ct/search?keyword='
              + urllib.parse.quote(brand["nameKo"]) + '" target="_blank" rel="noopener">캐치테이블에서 찾기</a>')
    ig = brand.get("ig", {})
    live = IG.get(brand["slug"]) or {}
    posts = live.get("posts") or []

    handle = live.get("handle") or ig.get("handle") or brand["instagram"].rstrip("/").split("/")[-1]
    followers = ig.get("followers")
    if live.get("followers"):
        n = live["followers"]
        followers = f"{n/10000:.1f}만" if n >= 10000 else f"{n:,}"
    bio = live.get("bio") or ig.get("bio") or brand["tagline"]

    if posts:
        # Real posts: each tile opens the post. Pins sit first (ig_sync.py
        # sorts newest-first, then floats the pinned ones).
        tiles = "".join(
            f'<a class="igp__tile{" is-pin" if p.get("pinned") else ""}'
            f'{" is-vid" if p.get("media_type") == "VIDEO" else ""}"'
            f' href="{e(p["permalink"])}" target="_blank" rel="noopener"'
            f' title="{e(p["caption"][:90])}">'
            f'<img src="{up}{e(p["img"])}" alt="{e(p["caption"][:70])}"'
            f' loading="lazy" decoding="async"></a>'
            for p in posts[:6])
    else:
        tiles = "".join(
            f'<span class="igp__tile"><img src="{up}assets/img/{t}" alt="" loading="lazy" decoding="async"></span>'
            for t in (f'sp-{k}-1-1200.jpg', f'sp-{k}-2-1200.jpg', f'sp-{k}-3-1200.jpg',
                      f'{k}-a-1200.jpg', f'{k}-b-1200.jpg', f'tex-{k}-1100.jpg'))
    return f"""
    <div class="igp">
      <div class="igp__head">
        <span class="igp__av"><img src="{up}assets/img/logo-{k}-w.png" alt=""></span>
        <div class="igp__id">
          <span class="igp__at">@{e(handle)}</span>
          {f'<span class="igp__stat"><b>{e(followers)}</b> 팔로워</span>' if followers else ''}
          <b class="igp__name">{e(brand["nameEn"])}</b>
          <p class="igp__bio">{e(bio)}</p>
          {f'<a class="igp__link" href="https://{e(ig["link"])}" target="_blank" rel="noopener">{e(ig["link"])}</a>' if ig.get("link") else ''}
          <a class="igp__cta" href="{e(brand['instagram'])}" target="_blank" rel="noopener">팔로우</a>
        </div>
      </div>
      <div class="igp__grid">{tiles}</div>
      <a class="igp__all" href="{e(brand['instagram'])}" target="_blank" rel="noopener">Instagram에서 더 보기 <i></i></a>
    </div>
    <div class="btns" style="margin-top:22px">{ct}</div>"""


def subnav(brand, depth=1):
    up = "../" * depth
    items = [("#story", "Story"), ("#space", "Space"),
             ("#stores", f"매장 {len(brand['locations'])}곳"), ("#feed", "Instagram")]
    links = "".join(
        f'<a href="{h}"{" class=" + chr(34) + "is-store" + chr(34) if h == "#stores" else ""}>{lab}</a>'
        for h, lab in items)
    return f"""
<div class="subnav"><div class="wrap"><div class="subnav__in">
  <span class="subnav__brand"><img src="{up}assets/img/logo-{KEY[brand["slug"]]}-w.png" alt="{e(brand["nameEn"])}"></span>{links}
</div></div></div>"""


def subnav(brand, depth=1):
    up = "../" * depth
    items = [("#story", "Story"), ("#space", "Space"),
             ("#stores", f"매장 {len(brand['locations'])}곳"), ("#feed", "Instagram")]
    links = "".join(
        f'<a href="{h}"{" class=" + chr(34) + "is-store" + chr(34) if h == "#stores" else ""}>{lab}</a>'
        for h, lab in items)
    return f"""
<div class="subnav"><div class="wrap"><div class="subnav__in">
  <span class="subnav__brand"><img src="{up}assets/img/logo-{KEY[brand["slug"]]}-w.png" alt="{e(brand["nameEn"])}"></span>{links}
</div></div></div>"""


HERO = [
    ("hx-lbm", "London Bagel Museum"),
    ("hx-cl",  "café Layered"),
    ("hx-hw",  "café highwaist"),
    ("hx-ab",  "Artist Bakery"),
]


def build_index():
    panels = ""
    for pi, (pref, label) in enumerate(HERO):
        imgs = "".join(
            f'<img{" class=" + chr(34) + "is-on" + chr(34) if i == 1 else ""} '
            f'src="assets/img/{pref}-{i}-1600.jpg" '
            f'srcset="assets/img/{pref}-{i}-1100.jpg 1100w, assets/img/{pref}-{i}-1600.jpg 1400w" sizes="25vw" '
            f'alt="{e(label)}"'
            f'{" fetchpriority=" + chr(34) + "high" + chr(34) if i == 1 and pi == 0 else ""}'
            f'{"" if i == 1 else " loading=" + chr(34) + "lazy" + chr(34)}>'
            for i in (1, 2, 3, 4))
        panels += (f'<div class="hero__panel">{imgs}'
                   f'<span class="hero__cap">{e(label)}</span></div>')

    cards = "".join(f"""
      <a class="bcard" href="brand/{b['slug']}.html" data-card="{KEY[b['slug']]}" data-rise="{i*80}">
        <div class="bcard__img">
          <img src="assets/img/card-{KEY[b['slug']]}-1400.jpg"
               srcset="assets/img/card-{KEY[b['slug']]}-1100.jpg 1100w, assets/img/card-{KEY[b['slug']]}-1400.jpg 1400w"
               sizes="25vw"
               alt="{e(b['nameEn'])}" loading="lazy" decoding="async">
          <span class="bcard__tint" style="background:{b['palette']['deep']}"></span>
        </div>
        <div class="bcard__body">
          <span class="bcard__cat">{e(b['category'])}</span>
          <span class="bcard__mark"><img class="bcard__logo" src="assets/img/logo-{KEY[b['slug']]}-w.png{_v("assets/img/logo-" + KEY[b["slug"]] + "-w.png")}" alt="{e(b['nameEn'])}" loading="lazy"></span>
          
          <p class="bcard__desc">{e(b['tagline'])}</p>
          <span class="bcard__go">매장 보기 <i></i></span>
        </div>
      </a>""" for i, b in enumerate(BRANDS))

    chars = "".join(f'<div class="char" data-rise="{i*55}">'
                    f'<div class="char__i"><img src="assets/img/{c["img"]}.jpg" alt="{e(c["name"])}" loading="lazy"></div>'
                    f'<b>{e(c["name"])}</b><span>{e(c.get("brandEn") or c["brand"])}</span></div>'
                    for i, c in enumerate(D["characters"]["items"]))

    live = [a for a in ESG["articles"] if a.get("status") != "hidden"]
    def _esg_thumb(a):
        """Notices and press releases usually carry no photograph; the
        landing-page teaser must not assume one."""
        if not a.get("images"):
            return ""
        q = a["images"][0].replace(".jpg", "")
        return (f'<div class="esg__thumb"><img src="assets/img/{q}-1100.jpg" '
                f'alt="{e(a["title"])}" loading="lazy" decoding="async"></div>')

    esg_rows = "".join(f"""
      <a class="esg__i" href="news/{e(a['id'])}.html" data-rise>
        {_esg_thumb(a)}
        <div><span class="esg__tag">{e(a['category'])}</span>
          <h3>{e(a['title'])}{'<span class="esg__draft">검수 대기</span>' if a.get('status')=='draft' else ''}</h3>
          <p>{'' if TODO(a['summary']) else e(a['summary'])}</p></div>
        <span class="esg__date">{e(a['date'])}</span>
      </a>""" for a in live[:3])


    body = f"""


<section class="hero">
  <div class="hero__grid">{panels}</div>
  <div class="hero__body"><div class="hero__inner">
    <div class="hero__eyebrow">LBM Corporation &middot; Seoul</div>
    <h1 class="hero__title">빵을 사랑하는 사람들이<br><span class="nb">모여 만드는 네 개의 공간.</span></h1>
    <p class="hero__sub">{e(CO['lede'])}</p>
    <div class="hero__meta">
      {"".join(f'<a class="hero__brand" data-card="{KEY[b["slug"]]}" href="brand/{b["slug"]}.html" '
               f'aria-label="{e(b["nameEn"])}"><img src="assets/img/logo-{KEY[b["slug"]]}-w.png'
               f'{_v("assets/img/logo-" + KEY[b["slug"]] + "-w.png")}" alt="{e(b["nameEn"])}"></a>' for b in BRANDS)}
    </div>
  </div></div>
</section>

{sec('01', 'Company', f'''
  <div class="split">
    <div>
      <p class="eyebrow">Company Overview</p>
      <h2 class="h-lg" data-rise>{e(CO['nameEn'])}</h2>
      <p class="lede" data-rise="70" style="margin-top:20px">{e(CO['visionBody'])}</p>
      <p class="lede" data-rise="110" style="margin-top:22px">{e(CO['profileProse'])}</p>
    </div>
    <div>
      <figure class="figframe" data-rise="90" style="margin:0">
        <img src="assets/img/band-spaces-1600.jpg" alt="{e(CO['nameKo'])}" loading="lazy" decoding="async">
      </figure>
    </div>
  </div>
''', sid='company')}

{sec('02', 'Portfolio', f'<div class="brands">{cards}</div>', sid='brands', cls='sec--caramel',
     head_html='''<p class="eyebrow">Brand Portfolio</p>
  <h2 class="h-lg" data-rise>네 개의 브랜드, <span class="em">하나</span>의 운영 체계.</h2>
  <p class="lede" data-rise="70" style="margin:20px 0 clamp(30px,3.6vw,48px)">
    베이글과 크림치즈, 홈메이드 스콘과 케이크, 소금빵과 바게트까지.
    네 브랜드 모두 직영으로 운영합니다.</p>''')}

{sec('03', 'Faces', f'<div class="chars">{chars}</div>', sid='faces', cls='sec--wine',
     head_html=f'''<p class="eyebrow">Characters</p>
  <h2 class="h-md" data-rise>매장에서 만나는 얼굴들.</h2>
  <p class="lede" data-rise="70" style="margin:18px 0 clamp(26px,3.2vw,40px)">{e(D['characters']['lede'])}</p>''')}

<section class="sec esgroom" id="esg">
  <div class="wrap">
    <div class="esgroom__mast">
      <span class="esgroom__name">LBM <em>Newsroom</em></span>
      <span class="esgroom__meta">Environmental &middot; Social &middot; Governance</span>
    </div>
    <h2 class="h-lg esgroom__head" data-rise>브랜드가 아니라,<br>LBM 전체로서.</h2>
    <p class="lede" data-rise="70" style="margin:22px 0 clamp(30px,3.6vw,48px)">{e(ESG['lede'])}</p>
    <div class="esg">{esg_rows}</div>
    <div style="margin-top:28px" data-rise><a class="arrow" href="esg.html">ESG 전체 보기 <i></i></a></div>
  </div></section>
"""
    return (head(f"{CO['nameEn']}. {CO['taglineKo']}", CO["lede"], "london-bagel-museum", path="index.html")
            + header("company") + body + footer())


# ---------------------------------------------------------------- brand
def build_brand(b):
    k = KEY[b["slug"]]
    heroes = "".join(
        f'<img{" class=" + chr(34) + "is-on" + chr(34) if i == 0 else ""} '
        f'src="../assets/img/{h}-2000.jpg" alt="{e(b["nameEn"])}"'
        f'{" fetchpriority=" + chr(34) + "high" + chr(34) if i == 0 else " loading=" + chr(34) + "lazy" + chr(34)}>'
        for i, h in enumerate(b["hero"]))

    mood = ""
    if b.get("moodWords"):
        mood = ('<p class="small" style="margin-top:20px;letter-spacing:.2em;text-transform:uppercase">'
                + " / ".join(e(w) for w in b["moodWords"]) + "</p>")

    craft_imgs = "".join(
        f'<figure><img src="../assets/img/cr-{k}-{i}-900.jpg" '
        f'srcset="../assets/img/cr-{k}-{i}-450.jpg 450w, ../assets/img/cr-{k}-{i}-900.jpg 900w" '
        f'sizes="33vw" alt="{e(b["craft"]["head"])}" loading="lazy" decoding="async"></figure>'
        for i in (1, 2, 3))

    art = ""
    if b.get("quote2"):
        plate = "".join(f'<img src="../assets/img/ab-art-{i}-900.jpg" alt="{e(b["nameEn"])}" loading="lazy">'
                        for i in (1, 2, 3, 4))
        art = sec("06", "Artwork", f'<div class="plate" data-rise>{plate}</div>', cls="sec--raised",
                  head_html=f'<div style="margin-bottom:clamp(24px,3vw,44px)">{quote(b["quote2"])}</div>')

    story_head = (
        '<p class="eyebrow">Brand Story</p>'
        f'<h2 class="h-md" data-rise>{e(b["nameEn"])}</h2>'
        f'<p class="lede" data-rise="70" style="margin-top:22px">{e(b["story"])}</p>{mood}')
    story = (
        '<div class="split"><div>' + story_head + '</div>'
        f'<figure class="figframe" data-rise="110" style="margin:0">'
        f'<img src="../assets/img/{b["texture"]}-1600.jpg" alt="{e(b["nameEn"])}" loading="lazy" decoding="async">'
        f'<figcaption>{e(b["categoryKo"])} &mdash; {e(b["nameEn"])}</figcaption></figure></div>')

    craft_head = (
        '<p class="eyebrow">What We Bake</p>'
        f'<h2 class="h-lg" data-rise>{e(b["craft"]["head"])}</h2>'
        f'<p class="lede" data-rise="70" style="margin:22px 0 clamp(28px,3.4vw,44px)">{e(b["craft"]["body"])}</p>')
    craft = (f'<div class="craft" data-rise>{craft_imgs}</div>'
             f'<p class="kinds" data-rise="80">{e(b["craft"]["kinds"])}</p>')

    space_head = (
        '<p class="eyebrow">The Space</p>'
        f'<h2 class="h-lg" data-rise>{e(b["space"]["head"])}</h2>'
        f'<p class="lede" data-rise="70" style="margin:22px 0 clamp(28px,3.4vw,44px)">{e(b["space"]["body"])}</p>')

    # "전국" only when the brand actually reaches beyond the capital region
    nationwide = "전국 " if any(
        not l.get("address", "").startswith(("서울", "경기"))
        for l in b["locations"]) else ""
    stores_head = (
        '<p class="eyebrow">Store Index</p>'
        f'<h2 class="h-lg" data-rise>{nationwide}<span class="em">{len(b["locations"])}개</span> 지점.</h2>'
        '<p class="lede" data-rise="70" style="margin:22px 0 clamp(28px,3.4vw,44px)">'
        '모든 매장을 직영으로 운영합니다. 작은 사진 위에 마우스를 올리면 큰 사진이 바뀝니다.</p>')

    feed_head = ('<p class="eyebrow">Instagram</p>'
                 f'<h2 class="h-md" data-rise>{e(b["nameEn"])}</h2>'
                 '<div style="margin-bottom:clamp(22px,2.8vw,34px)"></div>')

    body = "".join([
        '<section class="bhero"><div class="bhero__panel">', heroes, '</div>',
        '<div class="bhero__body"><div class="hero__inner">',
        f'<div class="hero__eyebrow">{e(b["category"])}</div>',
        f'<h1 class="bhero__h"><img class="bhero__logo" src="../assets/img/logo-{k}-w.png" alt="{e(b["nameEn"])}"></h1>',
        f'<p class="bhero__tag">{e(b["tagline"])}</p>',
        '</div></div></section>',
        subnav(b),
        sec("01", "Story", story, sid="story"),
        band_quote(f"band-{k}", b["quote"], depth=1),
        sec("02", "Space", gallery(f"sp-{k}", b["nameEn"] + " space", depth=1), sid="space",
            cls=("sec--umber" if b["slug"] == "london-bagel-museum" else ""), head_html=space_head),
        sec("03", "Stores", locations_block(b), sid="stores",
            cls=("sec--russet" if b["slug"] == "london-bagel-museum" else ""), head_html=stores_head),
        art,
        (band_quote("band-quote", D["quotes"]["closing"], depth=1)
         if b["slug"] == "london-bagel-museum" else ""),
        sec("06", "Feed", ig_block(b), sid="feed", cls="sec--raised", head_html=feed_head),
    ])
    return (head(f"{b['nameEn']}. {CO['nameEn']}", b["tagline"], b["slug"], depth=1, path=f"brand/{b['slug']}.html")
            + header("stores", 1) + body + footer(1))


# ---------------------------------------------------------------- esg
def build_esg():
    """The newsroom: a featured lead, then the full index with a category
    filter, then the photographs. The label on each row does the sorting."""
    SEC = ESG.get("sections", [])
    LABEL = {x["id"]: x["label"] for x in SEC}
    live = [a for a in ESG["articles"] if a.get("status") != "hidden"]

    lead = next((a for a in live if a.get("images")), live[0] if live else None)
    hero = ""
    if lead:
        cat = lead.get("cat", "esg")
        img = ""
        if lead.get("images"):
            q = lead["images"][0].replace(".jpg", "")
            img = (f'<div class="lead__shot"><img src="assets/img/{q}-1400.jpg" '
                   f'alt="{e(lead["title"])}" decoding="async"></div>')
        hero = f"""
  <section class="latest">
    <div class="sechd"><h2 class="sechd__t">최신 소식</h2><span class="sechd__n">Latest</span></div>
    <a class="lead" href="news/{e(lead['id'])}.html" data-rise>
      {img}
      <div class="lead__body">
        <span class="lead__cat">[{e(LABEL.get(cat, cat))}]</span>
        <h2 class="lead__head">{e(lead['title'])}</h2>
        <span class="lead__date">{e(lead['date'])}</span>
      </div>
    </a>
  </section>"""

    opts = "".join(f'<option value="{e(x["id"])}">{e(x["label"])}</option>' for x in SEC)
    rows = "".join(f"""
        <tr data-cat="{e(a.get('cat','esg'))}">
          <td class="ix__no">{len(live) - i}</td>
          <td class="ix__cat"><span class="plabel plabel--{e(a.get('cat','esg'))}">{e(LABEL.get(a.get('cat','esg'), ''))}</span></td>
          <td class="ix__t"><a href="news/{e(a['id'])}.html">{e(a['title'])}</a>{'<i class="ix__wait">검수 대기</i>' if a.get('status') == 'draft' else ''}</td>
          <td class="ix__d">{e(a['date'])}</td>
        </tr>""" for i, a in enumerate(live))
    if not rows:
        rows = '<tr><td colspan="4" class="ix__none">등록된 게시물이 없습니다.</td></tr>'

    # the newest article already headlines the page as 최신 소식 — repeating
    # its photo in the gallery reads as a duplicate, so it is excluded here
    tiles = "".join(f"""
      <a class="gal2__i" href="news/{e(a['id'])}.html" data-rise>
        <span class="gal2__shot">{(
          '<img src="assets/img/' + a['images'][0].replace('.jpg','') + '-1100.jpg" alt="" loading="lazy" decoding="async">'
          if a.get('images') else '<span class="gal2__set">' + e(LABEL.get(a.get('cat','esg'), '')) + '</span>')}</span>
        <span class="gal2__cat">{e(LABEL.get(a.get('cat','esg'), ''))}</span>
        <b class="gal2__t">{e(a['title'])}</b>
        <span class="gal2__d">{e(a['date'])}</span>
      </a>""" for a in live if not (lead and a["id"] == lead["id"]))

    body = f"""
<div class="wrap">
  <div class="mast">
    <div class="mast__rule"></div><div class="mast__rule--thin"></div>
    <div class="mast__row">
      <div class="mast__name">LBM <em>Newsroom</em></div>
      <div class="mast__meta">
        {e(CO['nameEn'])}<br>{e(CO['domain'])}
      </div>
    </div>
    <div class="mast__rule--thin"></div><div class="mast__rule" style="margin-top:3px"></div>
    <div class="mast__lede">
      <h1 data-rise>지역사회와 함께한 기록.</h1>
      <p data-rise="70">{e(ESG['lede'])}</p>
    </div>
  </div>
  {hero}

  <div class="ix">
    <div class="sechd"><h2 class="sechd__t">전체 목록</h2><span class="sechd__n">Index</span></div>
    <div class="ix__bar">
      <span class="ix__count"><b>{len(live)}</b>건</span>
      <label class="ix__filter">분류
        <select id="catfilter"><option value="all">전체</option>{opts}</select>
      </label>
    </div>
    <table class="ix__t8">
      <thead><tr><th>No</th><th>분류</th><th>제목</th><th>날짜</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  {('<section class="gal2"><div class="sechd"><h2 class="sechd__t">사진으로 보기</h2><span class="sechd__n">Photos</span></div><div class="gal2__grid">' + tiles + '</div></section>') if tiles else ''}
</div>
<div style="height:clamp(50px,6vw,96px)"></div>
"""
    return (head(f"뉴스룸. {CO['nameEn']}", ESG["lede"], "esg", flat=True, path="esg.html")
            + header("esg") + body + footer())


def build_article(a, prev, nxt):
    """One post as a press article, modelled on Korean newspaper article
    pages (ksilbo reference): headline, 승인 meta line, hero image with a
    제공 caption, body, byline, copyright, related posts."""
    SEC = ESG.get("sections", [])
    LABEL = {x["id"]: x["label"] for x in SEC}
    cat = a.get("cat", "esg")
    shot = ""
    if a.get("images"):
        q = a["images"][0].replace(".jpg", "")
        shot = (f'<figure class="art__shot"><img src="../assets/img/{q}-1400.jpg" '
                f'alt="{e(a["title"])}" decoding="async">'
                f'<figcaption>{e(a["title"])}. 사진=LBM 제공</figcaption></figure>')
    if TODO(a["summary"]):
        body = ('<div class="art__wait"><b>검수 대기</b> 본문과 정확한 날짜, 출처는 '
                'LBM 확인 후 게시됩니다. 사진은 LBM이 제공한 자료입니다.</div>')
    else:
        paras = "".join(f"<p>{e(p)}</p>" for p in a["summary"].split("\n") if p.strip())
        body = f'<div class="art__body">{paras}</div>'
    src = (f'<span class="art__meta-i"><i>출처</i>{e(a["source"])}</span>') if a.get("source") else ""

    def near(x, label):
        if not x:
            return ""
        return (f'<a class="art__near" href="{e(x["id"])}.html">'
                f'<span>{label}</span><b>{e(x["title"])} ({e(x["date"])})</b></a>')

    html_body = f"""
<div class="wrap wrap--art">
  <a class="art__back" href="../esg.html">뉴스룸으로</a>
  <article class="art">
    <span class="plabel plabel--{e(cat)}">{e(LABEL.get(cat, cat))}</span>
    <h1 class="art__head">{e(a['title'])}</h1>
    <div class="art__metaline">
      <span class="art__meta-i"><i>기자명</i>LBM 뉴스룸</span>
      <span class="art__meta-i"><i>승인</i>{e(a['date'])}</span>
      {src}
    </div>
    {shot}{body}
    <div class="art__byline">
      <b>LBM 뉴스룸</b>
      <a href="mailto:{e(CO['email'])}">{e(CO['email'])}</a>
    </div>
    <p class="art__copy">저작권자 &copy; {e(CO['nameEn'])} 무단전재 및 재배포 금지</p>
  </article>
  {('<div class="art__relhead">관련 기사</div><nav class="art__nav">'
     + near(nxt, '이전 기사') + near(prev, '다음 기사') + '</nav>') if (prev or nxt) else ''}
</div>
<div style="height:clamp(50px,6vw,96px)"></div>
"""
    desc = "" if TODO(a["summary"]) else a["summary"][:150]
    return (head(f"{a['title']} ({a['date']}). {CO['nameEn']}", desc or ESG["lede"], "esg", path=f"news/{a['id']}.html", noindex=a.get('status')=='draft',
                 depth=1, flat=True)
            + header("esg", depth=1) + html_body + footer(depth=1))


# ---------------------------------------------------------------- write
_IMG_RE = __import__("re").compile(r'((?:\.\./)?assets/img/[A-Za-z0-9._/-]+\.(?:jpg|png))(?!\?)')


def stamp(html_text):
    """Version every image URL by content hash. Without this, browsers keep
    serving the previous photograph after a re-crop and edits look ignored."""
    cache = {}

    def sub(m):
        rel = m.group(1)
        key = rel.lstrip("./").replace("../", "")
        if key not in cache:
            cache[key] = _v(key)
        return rel + cache[key]

    return _IMG_RE.sub(sub, html_text)




def true_srcset(txt):
    """Stamp every srcset width descriptor with the file's real pixel width.
    Templates guess; source-capped files made those guesses lie, and a wrong
    descriptor silently skews which variant browsers download."""
    import re, struct

    def jpg_width(p):
        try:
            with open(p, "rb") as f:
                data = f.read(64 * 1024)
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF: i += 1; continue
                m = data[i + 1]
                if m in (0xC0, 0xC1, 0xC2, 0xC3):
                    return struct.unpack(">H", data[i + 7:i + 9])[0]
                if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7: i += 2; continue
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        except Exception:
            pass
        return None

    def fix(mm):
        cands = []
        for part in mm.group(1).split(","):
            bits = part.strip().rsplit(" ", 1)
            if len(bits) == 2 and bits[1].endswith("w"):
                rel = bits[0].split("?")[0]
                w = jpg_width(os.path.join(ROOT, rel.lstrip("./").replace("../", "")))
                if w: bits[1] = f"{w}w"
            cands.append(" ".join(bits))
        seen, uniq = set(), []
        for c in cands:
            w = c.rsplit(" ", 1)[-1]
            if w in seen: continue
            seen.add(w); uniq.append(c)
        return 'srcset="' + ", ".join(uniq) + '"'

    return re.sub(r'srcset="([^"]+)"', fix, txt)

def main():
    os.makedirs(os.path.join(ROOT, "brand"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "news"), exist_ok=True)
    out = {"index.html": build_index(), "esg.html": build_esg()}
    for b in BRANDS:
        out[f"brand/{b['slug']}.html"] = build_brand(b)
    live = [a for a in ESG["articles"] if a.get("status") != "hidden"]
    for i, a in enumerate(live):
        out[f"news/{a['id']}.html"] = build_article(
            a, live[i - 1] if i else None, live[i + 1] if i + 1 < len(live) else None)
    # A deleted post must take its page with it, or the old URL keeps serving.
    keep = {f"{a['id']}.html" for a in live}
    for p in os.listdir(os.path.join(ROOT, "news")):
        if p.endswith(".html") and p not in keep:
            os.remove(os.path.join(ROOT, "news", p))
    for path, txt in out.items():
        open(os.path.join(ROOT, path), "w", encoding="utf-8").write(true_srcset(stamp(txt)))
        print("wrote", path, f"({len(txt)//1024} KB)")

    todos = []
    for b in BRANDS:
        todos += [f"hours — {b['nameKo']} {L['name']}" for L in b["locations"] if TODO(L.get("hours"))]
        if b.get("catchtable") and TODO(b["catchtable"]):
            todos.append(f"catchtable URL — {b['nameKo']}")
    todos += [f"ESG body — {a['title']} ({a['date']})" for a in ESG["articles"] if TODO(a.get("summary"))]
    if todos:
        print(f"\n{len(todos)} field(s) awaiting client input:")
        for t in todos:
            print("  ·", t)


if __name__ == "__main__":
    main()
