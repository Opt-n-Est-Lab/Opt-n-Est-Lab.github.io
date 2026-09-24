#!/usr/bin/env python3
"""
Generate the ONE Lab website.

    python3 _build/build.py            rebuild every page
    python3 _build/build.py --check    report what would change, write nothing
    python3 _build/build.py --force    rebuild even over hand-edited pages

EDIT THE MARKDOWN, NOT THE HTML. Everything a page says lives in _build/docs/:

    site.md            header, nav, footer, social links, emails - every page
    news.md            all news, newest first (the home page shows the first few)
    publications.md    every paper once, each with an id
    people.md          the People page
    gallery.md         the Gallery photos
    projects/*.md      one per research project; `publications:` lists paper ids
    pages/*.md         home, projects header, software, lab spaces, FAQ

This file only holds the page layouts. The generated .html files are build
output: an edit made to one directly is lost on the next build.

A build REFUSES to overwrite a page that was edited by hand, and saves a copy
of it under _build/_backup/ first. It tells the two cases apart with
manifest.json, which records the digest of what it last wrote. Use --check if
you are unsure whether anything has drifted.

A page the build made before but no longer makes - one that moved, or a
project whose .md was deleted - is removed, unless it was edited by hand.
"""

import hashlib
import html
import io
import json
import os
import re
import shutil
import sys
import time

try:
    import markdown as _markdown
    import yaml as _yaml
except ImportError as exc:  # pragma: no cover - environment problem, not logic
    sys.exit("Missing build dependency: %s\n"
             "Install both with:  python3 -m pip install markdown pyyaml" % exc.name)


# The site root is this script's parent directory.
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Long-form page text lives in _build/docs as Markdown: YAML front matter for
# the structured parts (title, artwork, publication list) and Markdown below it
# for the prose. Writing a paragraph there needs no Python quoting, and the
# structured parts are rendered by the same helpers the rest of the site uses,
# so a project page and the publications page cannot drift apart.
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


# Front matter runs from the first line to the next line that is exactly
# "---". Splitting on any "---" would also cut at a "# -----" comment rule.
_FRONT = re.compile(r"\A---[ \t]*\n(.*?)^---[ \t]*$\n?(.*)\Z", re.S | re.M)


def read_md(path):
    """(front matter dict, Markdown body) for one file in _build/docs."""
    raw = io.open(path, encoding="utf-8").read()
    m = _FRONT.match(raw)
    if not m:
        sys.exit("%s: expected YAML front matter between two --- lines"
                 % os.path.relpath(path, DOCS))
    return (_yaml.safe_load(m.group(1)) or {}), m.group(2).strip()


def load_docs(subdir):
    """Every .md in _build/docs/<subdir>, as (slug, front matter, prose html),
    ordered by filename so a build is reproducible."""
    folder = os.path.join(DOCS, subdir)
    out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md"):
            data, body = read_md(os.path.join(folder, name))
            out.append((name[:-3], data, _markdown.markdown(body)))
    return out


# Site-wide settings - header, nav, footer - written once in docs/site.md.
# SITE and NAV keep the shapes the page builders below already expect.
_site, _ = read_md(os.path.join(DOCS, "site.md"))
SITE = {k: v for k, v in _site.items() if k not in ("nav", "social")}
SITE["social"] = [(s["icon"], s["url"], s["label"]) for s in _site["social"]]
NAV = [(n["key"], n["href"], n["label"], n.get("short", n["label"])) for n in _site["nav"]]


def md_inline(text):
    """Markdown for a single run of text - no wrapping <p> - so it can sit
    inside markup the template already provides."""
    html_ = _markdown.markdown(text)
    m = re.fullmatch(r"<p>(.*)</p>", html_, re.S)
    return m.group(1) if m else html_


# News - one list, newest first, written once in docs/news.md. The home page
# takes the first three, the news page all of them.
_news, _ = read_md(os.path.join(DOCS, "news.md"))
NEWS_INTRO = _news["intro"]
NEWS = [(it["date"], it["image"], bool(it.get("framed")), "", md_inline(it["text"]),
         [(l["label"], l["url"]) for l in it.get("links", [])])
        for it in _news["items"]]

# Publications - every paper written once, in docs/publications.md, each with
# an id. Project pages list ids, so an edit there shows up everywhere.
_pubs, _ = read_md(os.path.join(DOCS, "publications.md"))
PUB_BY_ID = {p["id"]: p for p in _pubs["publications"] + _pubs.get("theses", [])}

# People - the People page's header block and every group, in docs/people.md.
_people, _ = read_md(os.path.join(DOCS, "people.md"))
PEOPLE = [(g["title"], True, g.get("members") or []) for g in _people["groups"]]
JOIN_CARD = _people.get("join_card")

# Gallery - the photos on the Gallery tab, in docs/gallery.md.
_gallery, _ = read_md(os.path.join(DOCS, "gallery.md"))
GALLERY = [(ph["file"], ph["alt"]) for ph in _gallery["photos"]]

# Research projects - one file each in docs/projects/, listed by `order` on
# both the home page and the Projects page.
PROJECTS = sorted(load_docs("projects"), key=lambda d: d[1]["order"])


def site_url(url, depth):
    """Links in a doc are written from the site root. Pages sit at different
    depths, so the ../ is added here rather than typed into the Markdown.
    Folders are linked as `people/`, not `people/index.html`, so the address
    bar stays clean; `./` is the home page."""
    if url.startswith(("http://", "https://", "mailto:", "#")):
        return url
    if url.startswith("./"):
        url = url[2:]
    return "../" * depth + url or "./"


def doc_refs(refs, depth):
    """A row of reference pills from front matter."""
    if not refs:
        return ""
    # depth=1 keeps fix_ref a no-op: site_url has already resolved the href.
    items = "".join(ref_anchor(r["label"], site_url(r["url"], depth), 1) for r in refs)
    return f'\n<div class="ref-links">{items}</div>'


def pub_html(pid, depth):
    """One publication, looked up by its id in docs/publications.md."""
    if pid not in PUB_BY_ID:
        sys.exit("Unknown publication id %r - check the ids in docs/publications.md" % pid)
    p = PUB_BY_ID[pid]
    links = [(l["label"], site_url(l["url"], depth)) for l in p.get("links", [])]
    # depth=1 keeps fix_ref a no-op: site_url has already resolved each href.
    return pub_item(p["title"], None, p["authors"], p["venue"], links, 1)


def doc_publications(ids, depth):
    """The Publications block on a project page, from a list of ids."""
    if not ids:
        return ""
    items = "\n".join(pub_html(pid, depth) for pid in ids)
    return f'\n<h3>Publications</h3>\n<ul class="pub-list">\n{items}\n</ul>'

GA_ID = SITE["ga_id"]


ICON = {
    "github": ('is-solid', '<path d="M12 2.8a9.2 9.2 0 0 0-2.9 17.9c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.2-3.4-1.2-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 0 1.6 1 1.6 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.7-1.4-2.3-.3-4.7-1.1-4.7-5.1 0-1.1.4-2.1 1-2.8-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.9 1.1a9.8 9.8 0 0 1 5.2 0C17.2 4.7 18 5 18 5c.5 1.4.2 2.4.1 2.7.7.7 1 1.7 1 2.8 0 4-2.4 4.8-4.7 5.1.4.3.7 1 .7 1.9v2.7c0 .3.2.6.7.5A9.2 9.2 0 0 0 12 2.8Z"></path>'),
    "linkedin": ('is-solid', '<path d="M6.5 8.5H3.5V20H6.5V8.5Z"></path><path d="M5 3.7a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6Z"></path><path d="M10 8.5h3v1.6c.9-1.2 2.2-2 4-2 3.1 0 4.5 2 4.5 5.5V20h-3v-5.8c0-2-.7-3.2-2.4-3.2-1.9 0-3.1 1.3-3.1 3.7V20h-3V8.5Z"></path>'),
    "youtube": ('is-solid', '<path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8ZM10 15V9l5.2 3L10 15Z"></path>'),
    "website": ('', '<circle cx="12" cy="12" r="9"></circle><path d="M3 12h18"></path><path d="M12 3a15 15 0 0 1 0 18"></path><path d="M12 3a15 15 0 0 0 0 18"></path>'),
    "email": ('', '<rect x="3" y="5" width="18" height="14" rx="2.5"></rect><path d="m3.5 7 8.5 6 8.5-6"></path>'),

    # Brand glyphs from simple-icons (CC0). Authored on the same 24x24 grid as
    # the hand-drawn marks above, so they need no rescaling; all are filled.
    "scholar": ('is-solid', '<path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917z"></path><path d="M4.176 9.032a.5.5 0 0 0-.656.327l-.5 1.7a.5.5 0 0 0 .294.605l4.5 1.8a.5.5 0 0 0 .372 0l4.5-1.8a.5.5 0 0 0 .294-.605l-.5-1.7a.5.5 0 0 0-.656-.327L8 10.466z"></path>', '0 0 16 16'),
    "researchgate": ('is-solid', '<path d="M19.586 0c-.818 0-1.508.19-2.073.565-.563.377-.97.936-1.213 1.68a3.193 3.193 0 0 0-.112.437 8.365 8.365 0 0 0-.078.53 9 9 0 0 0-.05.727c-.01.282-.013.621-.013 1.016a31.121 31.123 0 0 0 .014 1.017 9 9 0 0 0 .05.727 7.946 7.946 0 0 0 .077.53h-.005a3.334 3.334 0 0 0 .113.438c.245.743.65 1.303 1.214 1.68.565.376 1.256.564 2.075.564.8 0 1.536-.213 2.105-.603.57-.39.94-.916 1.175-1.65.076-.235.135-.558.177-.93a10.9 10.9 0 0 0 .043-1.207v-.82c0-.095-.047-.142-.14-.142h-3.064c-.094 0-.14.047-.14.141v.956c0 .094.046.14.14.14h1.666c.056 0 .084.03.084.086 0 .36 0 .62-.036.865-.038.244-.1.447-.147.606-.108.385-.348.664-.638.876-.29.212-.738.35-1.227.35-.545 0-.901-.15-1.21-.353-.306-.203-.517-.454-.67-.915a3.136 3.136 0 0 1-.147-.762 17.366 17.367 0 0 1-.034-.656c-.01-.26-.014-.572-.014-.939a26.401 26.403 0 0 1 .014-.938 15.821 15.822 0 0 1 .035-.656 3.19 3.19 0 0 1 .148-.76 1.89 1.89 0 0 1 .742-1.01c.344-.244.593-.352 1.137-.352.508 0 .815.096 1.144.303.33.207.528.492.764.925.047.094.111.118.198.07l1.044-.43c.075-.048.09-.115.042-.199a3.549 3.549 0 0 0-.466-.742 3 3 0 0 0-.679-.607 3.313 3.313 0 0 0-.903-.41A4.068 4.068 0 0 0 19.586 0zM8.217 5.836c-1.69 0-3.036.086-4.297.086-1.146 0-2.291 0-3.007-.029v.831l1.088.2c.744.144 1.174.488 1.174 2.264v11.288c0 1.777-.43 2.12-1.174 2.263l-1.088.2v.832c.773-.029 2.12-.086 3.465-.086 1.29 0 2.951.057 3.667.086v-.831l-1.49-.2c-.773-.115-1.174-.487-1.174-2.264v-4.784c.688.057 1.29.057 2.206.057 1.748 3.123 3.41 5.472 4.355 6.56.86 1.032 2.177 1.691 3.839 1.691.487 0 1.003-.086 1.318-.23v-.744c-1.031 0-2.063-.716-2.808-1.518-1.26-1.376-2.95-3.582-4.355-6.074 2.32-.545 4.04-2.722 4.04-4.9 0-3.208-2.492-4.698-5.758-4.698zm-.515 1.29c2.406 0 3.839 1.26 3.839 3.552 0 2.263-1.547 3.782-4.097 3.782-.974 0-1.404-.03-2.063-.086v-7.19c.66-.059 1.547-.059 2.32-.059z"></path>'),
    "x": ('is-solid', '<path d="M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"></path>'),
    "arxiv": ('is-solid', '<path d="M3.8423 0a1.0037 1.0037 0 0 0-.922.6078c-.1536.3687-.0438.6275.2938 1.1113l6.9185 8.3597-1.0223 1.1058a1.0393 1.0393 0 0 0 .003 1.4229l1.2292 1.3135-5.4391 6.4444c-.2803.299-.4538.823-.2971 1.1986a1.0253 1.0253 0 0 0 .9585.635.9133.9133 0 0 0 .6891-.3405l5.783-6.126 7.4902 8.0051a.8527.8527 0 0 0 .6835.2597.9575.9575 0 0 0 .8777-.6138c.1577-.377-.017-.7502-.306-1.1407l-7.0518-8.3418 1.0632-1.13a.9626.9626 0 0 0 .0089-1.3165L4.6336.4639s-.3733-.4535-.768-.463zm0 .272h.0166c.2179.0052.4874.2715.5644.3639l.005.006.0052.0055 10.169 10.9905a.6915.6915 0 0 1-.0072.945l-1.0666 1.133-1.4982-1.7724-8.5994-10.39c-.3286-.472-.352-.6183-.2592-.841a.7307.7307 0 0 1 .6704-.4401Zm14.341 1.5701a.877.877 0 0 0-.6554.2418l-5.6962 6.1584 1.6944 1.8319 5.3089-6.5138c.3251-.4335.479-.6603.3247-1.0292a1.1205 1.1205 0 0 0-.9763-.689zm-7.6557 12.2823 1.3186 1.4135-5.7864 6.1295a.6494.6494 0 0 1-.4959.26.7516.7516 0 0 1-.706-.4669c-.1119-.2682.0359-.6864.2442-.9083l.0051-.0055.0047-.0055z"></path>'),
    "orcid": ('is-solid', '<path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"></path>'),
}


def icon_link(kind, href, label, external=True):
    # An ICON entry is (solid_class, path_markup) on the shared 24x24 grid, or
    # (solid_class, path_markup, viewBox) for a borrowed mark drawn on its own.
    entry = ICON[kind]
    solid, path = entry[0], entry[1]
    view = entry[2] if len(entry) > 2 else "0 0 24 24"
    cls = f"icon-link {solid}".strip()
    rel = ' target="_blank" rel="noopener noreferrer"' if external else ""
    return (
        f'<a class="{cls}" href="{href}"{rel} aria-label="{html.escape(label)}" '
        f'title="{html.escape(label)}"><svg viewBox="{view}" aria-hidden="true">{path}</svg></a>'
    )


def header(depth, active):
    p = "../" * depth
    items = []
    for key, href, label, short in NAV:
        cur = ' aria-current="page" class="active"' if key == active else ""
        lbl = (
            f'<span class="navLabelDesktop">{label}</span>'
            f'<span class="navLabelMobile">{short}</span>'
            if label != short else label
        )
        items.append(
            f'        <a href="{site_url(href, depth)}"{cur} data-label="{label}" data-short="{short}">\n'
            f'          <span class="navLabel">{lbl}</span>\n'
            f'        </a>'
        )
    nav = "\n".join(items)
    return f"""  <header class="header">
    <div class="container navbar">
      <a class="brand" href="{site_url('./', depth)}">
        <img class="brandLogo" src="{p}pic/site/onelab_t.svg" alt="{SITE['name']}" width="132" height="22" />
        <small>{SITE['tagline']}</small>
      </a>

      <nav class="nav" aria-label="Primary navigation">
{nav}
      </nav>

      <button id="themeToggle" class="themeBtn" type="button" aria-label="Switch color theme" aria-pressed="false" title="Switch color theme">
        <span class="themeTrack" aria-hidden="true">
          <svg class="themeIcon themeIconSun" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="3.5"></circle>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42"></path>
          </svg>
          <svg class="themeIcon themeIconMoon" viewBox="0 0 24 24">
            <path d="M20 15.2A8.5 8.5 0 0 1 8.8 4a8.5 8.5 0 1 0 11.2 11.2Z"></path>
          </svg>
          <span class="themeThumb"></span>
        </span>
      </button>
    </div>
  </header>"""


def footer(depth):
    """The one and only footer. Its text comes from site.md."""
    p = "../" * depth

    social = "\n        ".join(
        icon_link(kind, url, label) for kind, url, label in SITE["social"]
    )

    return f"""  <footer class="footer">
    <div class="container footer-inner">
      <div>
        <div class="footer-logo">
          <a href="{site_url('./', depth)}"><img src="{p}pic/site/onelab_t.svg" alt="{SITE['name']}" width="108" height="19" /></a>
        </div>
        <p class="footer-meta">
          Optimization and Estimation (ONE) Lab<br />
          MSC01 1150<br />
          1 University of New Mexico<br />
          Albuquerque, NM 87131<br />
        </p>
      </div>

      <div class="footer-social">
        {social}
      </div>
    </div>

    <div class="container">
      <p class="footer-meta">&copy; {SITE['name']}. All rights reserved.</p>
    </div>
  </footer>"""


THEME_SCRIPT = """  <script>
    (function () {
      var root = document.documentElement;
      var btn = document.getElementById("themeToggle");

      function store(theme) {
        try { sessionStorage.setItem("theme", theme); } catch (e) {}
      }

      function apply(theme) {
        root.dataset.theme = theme;
        store(theme);
        var isDark = theme === "dark";
        if (btn) {
          btn.setAttribute("aria-pressed", String(isDark));
          btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
        }
      }

      apply(root.dataset.theme === "dark" ? "dark" : "light");

      if (btn) {
        btn.addEventListener("click", function () {
          apply(root.dataset.theme === "light" ? "dark" : "light");
        });
      }
    })();
  </script>"""

# Runs before paint so the theme is on <html> before anything is drawn. Every
# visit starts light, whatever the visitor's system setting; a switch to dark
# is kept (in sessionStorage) only for the rest of that visit.
THEME_INIT = """    <script>
      (function () {
        var saved = null;
        try { saved = sessionStorage.getItem("theme"); } catch (e) {}
        document.documentElement.dataset.theme = saved === "dark" ? "dark" : "light";
      })();
    </script>"""


def page(depth, active, title, description, body, extra_js=""):
    p = "../" * depth
    return f"""<!doctype html>
<!--
  GENERATED FILE - do not edit directly.

  Built by _build/build.py; page text lives in _build/docs/.
  Any edit made here is overwritten the next time the site is built.
-->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />

    <title>{html.escape(title)} &middot; ONE Lab</title>
    <meta name="description" content="{html.escape(description)}" />

    <meta property="og:title" content="{html.escape(title)} · ONE Lab" />
    <meta property="og:description" content="{html.escape(description)}" />
    <meta property="og:type" content="website" />

    <link rel="icon" href="{p}pic/site/icon.png" />
    <link rel="stylesheet" href="{p}styles.css" />

{THEME_INIT}

    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
  </head>

  <body>
{header(depth, active)}

    <main class="container">
      <div class="banner-wrap">
      <img
        class="banner banner--light"
        src="{p}pic/site/onelab_banner.jpg"
        alt="{SITE['full_name']}"
        width="1640"
        height="167"
      />
      <img
        class="banner banner--dark"
        src="{p}pic/site/onelab_banner_dark.jpg"
        alt="{SITE['full_name']}"
        width="1640"
        height="167"
      />
      </div>

{body}
    </main>

{footer(depth)}

{THEME_SCRIPT}
{extra_js}
  </body>
</html>
"""


CHECK = "--check" in sys.argv
FORCE = "--force" in sys.argv

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(BUILD_DIR, "manifest.json")

PAGES = {}


def write(relpath, text):
    """Collect a generated page. Nothing reaches disk until flush()."""
    PAGES[relpath] = text


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _backup(relpaths):
    """Copy pages aside before they are overwritten. Returns the folder."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    folder = os.path.join(BUILD_DIR, "_backup", stamp)
    for relpath in relpaths:
        dest = os.path.join(folder, relpath)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(OUT, relpath), dest)
    return folder


def flush():
    """Compare against disk, protect hand edits, then write.

    A page can differ from the generator for two very different reasons:

      * someone edited the .html by hand  -> their work; must not be lost
      * a docs/ file or build.py changed  -> expected; just needs writing

    manifest.json records the digest of what this script last wrote, which is
    what tells those apart.
    """
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            recorded = json.load(f)
    except (OSError, ValueError):
        recorded = {}

    hand_edited, stale = [], []
    for relpath, text in sorted(PAGES.items()):
        try:
            current = open(os.path.join(OUT, relpath), encoding="utf-8").read()
        except FileNotFoundError:
            stale.append(relpath)
            continue
        if recorded.get(relpath) and _digest(current) != recorded[relpath]:
            hand_edited.append(relpath)
        elif current != text:
            stale.append(relpath)

    # Pages the build wrote last time but no longer makes: a moved page, or a
    # project whose .md was deleted. Unchanged ones are removed; one edited by
    # hand is left in place and named, and stays in the manifest so it keeps
    # being named until someone deletes it.
    retired, retired_kept = [], []
    for relpath in sorted(set(recorded) - set(PAGES)):
        try:
            current = open(os.path.join(OUT, relpath), encoding="utf-8").read()
        except FileNotFoundError:
            continue
        if _digest(current) == recorded[relpath]:
            retired.append(relpath)
        else:
            retired_kept.append(relpath)

    if CHECK:
        if hand_edited:
            print("Edited by hand since the last build "
                  "(a plain build will refuse to overwrite these):\n")
            for relpath in hand_edited:
                print("  " + relpath)
        if stale:
            print(("\n" if hand_edited else "") +
                  "Out of date; a build will rewrite them:\n")
            for relpath in stale:
                print("  " + relpath)
        if retired:
            print("\nNo longer built; a build will remove them:\n")
            for relpath in retired:
                print("  " + relpath)
        if retired_kept:
            print("\nNo longer built, but edited by hand; left in place:\n")
            for relpath in retired_kept:
                print("  " + relpath)
        if not (hand_edited or stale or retired or retired_kept):
            print("Everything is up to date.")
        return 1 if hand_edited else 0

    saved = _backup(hand_edited) if hand_edited else None

    if hand_edited and not FORCE:
        print(f"Build stopped. {len(hand_edited)} page(s) were edited by hand:\n")
        for relpath in hand_edited:
            print("  " + relpath)
        print("\nThose edits exist only in the .html, so building would discard")
        print("them. They have been copied to:\n")
        print("  " + os.path.relpath(saved, OUT) + "\n")
        print("Move the change into _build/docs/ (words, nav, footer) or")
        print("_build/build.py (layout), then build again. To build anyway and")
        print("keep only the backup copy, re-run with --force.")
        return 1

    for relpath, text in sorted(PAGES.items()):
        path = os.path.join(OUT, relpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    for relpath in retired:
        path = os.path.join(OUT, relpath)
        os.remove(path)
        # Drop folders the removal left empty, but never the site root.
        folder = os.path.dirname(path)
        while folder != OUT and not os.listdir(folder):
            os.rmdir(folder)
            folder = os.path.dirname(folder)

    manifest = {r: _digest(t) for r, t in PAGES.items()}
    manifest.update({r: recorded[r] for r in retired_kept})
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")

    if retired:
        print("Removed " + str(len(retired)) + " page(s) no longer built:")
        for relpath in retired:
            print("  " + relpath)
    if retired_kept:
        print("Not removed - no longer built, but edited by hand:")
        for relpath in retired_kept:
            print("  " + relpath)

    if saved:
        print("Overwrote " + str(len(hand_edited)) + " hand-edited page(s); "
              "copies kept in " + os.path.relpath(saved, OUT))
    print(f"Done - {len(PAGES)} pages written.")
    return 0


# ===========================================================================
# Fragments
# ===========================================================================

CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"></path></svg>'


def person_card(p, depth, interests=False):
    """Speaker-style card: portrait, name, department, then any honour /
    next-step line, with icon links at the foot. The person's category is the
    heading of the section the card sits in.

    interests=True adds the member's research interests as a meta line under
    the department. It is opt-in per section rather than automatic, because
    every member carries an "interests" value in people.md and only some
    sections show it."""
    up = "../" * depth

    lines = ""
    for h in p.get("honors", []):
        lines += f'\n          <div class="person-honor">{h}</div>'
    if p.get("nxt"):
        # A leading arrow in the data means this line continues from the role
        # above it ("B.S. '25" then where they went), so it is drawn as a
        # downward step instead of an inline arrow. Lines that stand on their
        # own keep their own wording untouched.
        nxt, step = p["nxt"], ""
        if nxt.startswith("&rarr;"):
            nxt, step = nxt[len("&rarr;"):].strip(), " is-step"
        lines += f'\n          <div class="person-next{step}">{nxt}</div>'

    # Last in the block: the interest badge sinks to the foot of the card, just
    # above the icon row, so it reads as a footer rather than a subtitle.
    if interests and p.get("interests"):
        lines += f'\n          <div class="person-interest">{p["interests"]}</div>'

    links = []
    if p.get("website"):
        links.append(icon_link("website", p["website"], f'{p["name"]} website'))
    if p.get("scholar"):
        links.append(icon_link("scholar", p["scholar"], f'{p["name"]} on Google Scholar'))
    if p.get("researchgate"):
        links.append(icon_link("researchgate", p["researchgate"], f'{p["name"]} on ResearchGate'))
    if p.get("arxiv"):
        links.append(icon_link("arxiv", p["arxiv"], f'{p["name"]} on arXiv'))
    if p.get("github"):
        links.append(icon_link("github", p["github"], f'{p["name"]} on GitHub'))
    if p.get("x"):
        links.append(icon_link("x", p["x"], f'{p["name"]} on X'))
    if p.get("linkedin"):
        links.append(icon_link("linkedin", p["linkedin"], f'{p["name"]} on LinkedIn'))
    if p.get("email"):
        links.append(icon_link("email", f'mailto:{p["email"]}', f'Email {p["name"]}', external=False))
    actions = (
        '\n          <div class="person-actions">\n            <div class="social-links" '
        f'aria-label="{html.escape(p["name"])} links">\n              '
        + "\n              ".join(links) + "\n            </div>\n          </div>"
    ) if links else ""

    return f"""        <article class="person-card">
          <img class="person-avatar" src="{up}{p['photo']}" alt="{html.escape(p['name'])}" loading="lazy" width="120" height="120" />
          <div class="person-name">{p['name']}</div>
          <div class="person-role">{p['dept']}</div>{lines}{actions}
        </article>"""


def join_card(depth):
    """An empty slot in the shape of a member card: vacant portrait, an
    invitation where the name goes, and the FAQ button where a member's icon
    links would be. Driven by join_card in people.md."""
    up = "../" * depth
    j = JOIN_CARD
    return f"""        <article class="person-card join-card">
          <div class="person-avatar is-empty" aria-hidden="true"></div>
          <div class="person-name">{j['name']}</div>
          <div class="person-role">{j['dept']}</div>
          <div class="person-actions">
            <a class="btn" href="{up}{j['href']}">{j['label']} <span aria-hidden="true">&rarr;</span></a>
          </div>
        </article>"""


def alum_row(p, depth):
    """Full-width alumni row: name, department and degree on the left, then an
    arrow across to where they went. Used instead of a grid card for members
    flagged row: true in people.md."""
    # Degree and department read as one fact ("UNM, B.S. '26, Mechanical
    # Engineering"), so they share a cell rather than two columns.
    bits = [b for b in (p.get("degree"), p.get("dept")) if b]
    meta = (f'\n          <span class="alum-meta">{", ".join(bits)}</span>'
            if bits else "")
    # The arrow is drawn by .alum-next::before rather than carried in the
    # markup: it is punctuation between two fields, not content of its own, and
    # a stacked narrow layout drops it without touching the HTML.
    dest = (f'\n          <span class="alum-next">{p["nxt"]}</span>'
            if p.get("nxt") else "")
    return f"""        <article class="alum-row">
          <span class="alum-name">{html.escape(p['name'])}</span>{meta}{dest}
        </article>"""


def art_class(path, is_art):
    """Pick the dark-mode treatment for an image: flat brand mark, full-colour
    illustration on a light plate, or an untouched photograph."""
    if "onelab" in path:
        return "art-mark"
    return "art-illus" if is_art else "art-photo"


def project_card(img, title, href, desc, depth, row=False):
    """A project tile. Pass desc=None for the compact form used on the home
    page: image and a plain <h4> title only — no link, description or details
    button.

    row=True lays the same card out as the old site's projects page does:
    artwork on the left, and on the right the title, description and the
    details button. The title is plain text - the button carries the link."""
    up = "../" * depth
    thumb = (f'<img class="project-thumb {art_class(img, True)}" src="{up}{img}" '
             f'alt="" loading="lazy" draggable="false" />')

    if row:
        return f"""      <article class="project-card project-card--row">
        {thumb}
        <div class="project-body">
          <h3>{title}</h3>
          <p>{desc}</p>
          <a class="btn-ghost" href="{href}">Project details <span aria-hidden="true">&rarr;</span></a>
        </div>
      </article>"""

    extra = (f"\n        <p>{desc}</p>"
             f"\n        <a class=\"btn-ghost\" href=\"{href}\">Project details "
             f"<span aria-hidden=\"true\">&rarr;</span></a>") if desc else ""
    heading = (f'<h3><a href="{href}">{title}</a></h3>' if desc
               else f"<h4>{title}</h4>")
    return f"""      <article class="project-card">
        {thumb}
        {heading}{extra}
      </article>"""


TARGET_BLANK = ' target="_blank" rel="noopener noreferrer"'


def fix_ref(url, depth):
    """Reference URLs are authored relative to a subfolder (news/, publications/).
    On a root-level page, drop the leading '../'."""
    if url.startswith("http") or url.startswith("mailto:"):
        return url
    if depth == 0 and url.startswith("../"):
        return url[3:]
    return url


def ref_anchor(label, url, depth=1):
    """A reference pill. Links that leave the site open in a new tab. The
    outward-arrow icon is drawn by .ref-link::after rather than emitted here,
    so every pill carries one and the SVG is not repeated on every page."""
    href = fix_ref(url, depth)
    if href.startswith("http"):
        return f'<a class="ref-link" href="{href}"{TARGET_BLANK}>{label}</a>'
    return f'<a class="ref-link" href="{href}">{label}</a>'


def news_card(date, thumb, contain, summary, refs, depth):
    up = "../" * depth
    # Thumbnails living under news/ are already relative to the news folder.
    src = f"{up}{thumb}"
    cls = (f"news-thumb news-thumb--contain {art_class(thumb, True)}"
           if contain else "news-thumb")
    ref_html = ""
    if refs:
        items = "".join(ref_anchor(l, u, depth) for l, u in refs)
        ref_html = f'\n          <div class="ref-links">{items}</div>'
    # News items have no pages of their own: the card is the whole item, so
    # the picture is not a link. The date is a plain label.
    return f"""      <article class="news-card">
        <div class="news-pic">
          <img class="{cls}" src="{src}" alt="" loading="lazy" />
        </div>
        <div class="news-body">
          <span class="news-date">{date}</span>
          <p>{summary}</p>{ref_html}
        </div>
      </article>"""


def pub_label(url):
    """Name a publication's own link. Most are plain doi.org links; the AIAA
    one carries its DOI inside the path, and the IDEALS thesis has an HDL
    handle rather than a DOI, so it cannot be labelled one."""
    for marker in ("doi.org/", "/doi/abs/", "/doi/"):
        if marker in url and url.split(marker, 1)[1].startswith("10."):
            return "DOI"
    if "hdl.handle.net/" in url:
        return "Handle"
    return "Link"


def pub_item(title, url, authors, venue, refs, depth):
    # The title is plain text: the paper's own link sits below the venue as a
    # reference pill named after its DOI, alongside any other references.
    links = ([(pub_label(url), url)] if url else []) + list(refs)
    ref_html = ""
    if links:
        items = "".join(ref_anchor(l, u, depth) for l, u in links)
        ref_html = f'\n        <div class="ref-links">{items}</div>'
    return f"""      <li class="pub-item">
        <p class="pub-title">{title}</p>
        <p class="pub-authors">{authors}</p>
        <p class="pub-venue">{venue}</p>{ref_html}
      </li>"""


def seg_nav(active, depth):
    # Written from the site root, so the tabs work from any Projects page.
    tabs = [
        ("research", "projects/", "Research Projects"),
        ("open-source", "projects/software/", "Software"),
        ("lab", "projects/lab_spaces/", "Lab Spaces"),
        ("gallery", "projects/gallery/", "Gallery"),
    ]
    rows = []
    for key, href, label in tabs:
        cur = ' aria-current="page"' if key == active else ""
        rows.append(f'        <a href="{site_url(href, depth)}"{cur}>{label}</a>')
    items = "\n".join(rows)
    return f"""      <nav class="seg-nav" aria-label="Projects sections">
{items}
      </nav>"""


LIGHTBOX = """      <div class="lightbox" id="lightbox" data-open="false">
        <button class="lightbox-close" type="button" aria-label="Close image">&times;</button>
        <img id="lightbox-img" src="" alt="" />
      </div>"""

LIGHTBOX_JS = """  <script>
    (function () {
      var box = document.getElementById("lightbox");
      if (!box) return;
      var img = document.getElementById("lightbox-img");

      document.querySelectorAll(".gallery-grid img").forEach(function (thumb) {
        thumb.setAttribute("tabindex", "0");
        thumb.setAttribute("role", "button");
        function open() {
          img.src = thumb.src;
          img.alt = thumb.alt;
          box.dataset.open = "true";
        }
        thumb.addEventListener("click", open);
        thumb.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
        });
      });

      function close() { box.dataset.open = "false"; img.src = ""; }
      box.addEventListener("click", close);
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") close();
      });
    })();
  </script>"""


# ===========================================================================
# Pages
# ===========================================================================

def build_home():
    home, intro = read_md(os.path.join(DOCS, "pages", "home.md"))
    R, N = home["research"], home["news"]
    latest = NEWS[:N.get("count", 3)]
    cards = "\n".join(
        news_card(d, t, c, sm, r, 0) for d, t, c, _, sm, r in latest
    )
    # Compact tiles on the home page: no description, just image + title.
    projects = "\n".join(
        project_card(d["image"], d["title"], f"projects/research/{slug}/", None, 0)
        for slug, d, _ in PROJECTS)

    # The director's card in the intro block draws on the same PEOPLE entry as
    # the People page, so the photo and links cannot go out of sync.
    pi = next(p for _, _, members in PEOPLE for p in members if p.get("lead"))
    # The intro block keeps the three a visitor landing here would want. The
    # full set of academic profiles lives on his People card.
    pi_links = "\n              ".join(
        [icon_link("website", pi["website"], f"{pi['name']} website"),
         icon_link("linkedin", pi["linkedin"], f"{pi['name']} on LinkedIn"),
         icon_link("email", f"mailto:{pi['email']}", f"Email {pi['name']}", external=False)])

    body = f"""      <section class="section">
        <div class="prose intro">
          <div class="intro-text">
            {_markdown.markdown(intro)}
            <p class="intro-sign">
              <a href="{pi['website']}" target="_blank" rel="noopener noreferrer"><strong>{pi['name']}</strong></a><br />
              Director, {SITE['name']}
            </p>
          </div>

          <div class="intro-pi">
            <img src="{pi['photo']}" alt="{pi['name']}" width="160" height="160" loading="lazy" />
            <div class="intro-links" aria-label="{pi['name']} links">
              {pi_links}
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <p class="section-label">{R["label"]}</p>
        <div class="section-head">
          <h2>{R["heading"]}</h2>
          <a class="btn-ghost" href="projects/">{R["button"]} <span aria-hidden="true">&rarr;</span></a>
        </div>
        <p class="section-intro">{R["intro"]}</p>

        <div class="project-grid project-grid--home">
{projects}
        </div>
      </section>

      <section class="section">
        <p class="section-label">{N["label"]}</p>
        <div class="section-head">
          <h2>{N["heading"]}</h2>
          <a class="btn-ghost" href="news/">{N["button"]} <span aria-hidden="true">&rarr;</span></a>
        </div>
        <p class="section-intro">{N["intro"]}</p>

        <div class="news-grid">
{cards}
        </div>
      </section>"""

    write("index.html", page(
        0, "home", "Home",
        "The Optimization and Estimation (ONE) Lab at the University of New Mexico studies "
        "resilient estimation and safe control for cyber-physical systems.",
        body))


def pi_card(p, depth):
    """The original PI card: a large square portrait beside the name, with
    email, title and department on their own lines; the bio beneath; icon
    links along the foot."""
    up = "../" * depth
    # Four links only. The academic profiles (Scholar, ResearchGate, arXiv, X)
    # stay in people.md but are not shown here - the website they all hang off
    # is the first icon. Each is optional so the card works for a PI who has
    # not got all of them.
    order = [("website", "website", "{n} website"),
             ("github", "github", "{n} on GitHub"),
             ("linkedin", "linkedin", "{n} on LinkedIn")]
    items = [icon_link(kind, p[key], label.format(n=p["name"]))
             for key, kind, label in order if p.get(key)]
    if p.get("email"):
        items.append(icon_link("email", f'mailto:{p["email"]}',
                               f'Email {p["name"]}', external=False))
    links = "\n                ".join(items)
    return f"""        <article class="pi-card">
          <div class="pi-profile">
            <img class="pi-photo" src="{up}{p['photo']}" alt="{html.escape(p['name'])}" loading="lazy" width="168" height="168" />
            <div class="pi-identity">
              <h3>{p['name']}</h3>
              <p class="pi-affiliation">
                <a href="mailto:{p['email']}"><code>{p['email']}</code></a><br />
                {"<br />".join(p['dept'].split(', '))}
              </p>

              <div class="pi-actions" aria-label="{html.escape(p['name'])} links">
                {links}
              </div>
            </div>
          </div>

          <p class="pi-bio">{md_inline(p['bio'])}</p>
        </article>"""


def build_people():
    # One section per group, in the order they appear in people.md: the
    # Professors group renders as the Faculty card, every other group as a
    # heading over a grid of cards.
    sections = []
    for title, _, members in PEOPLE:
        if title == "Professors":
            sections.append(f"""      <section class="people-section">
        <h2>Faculty</h2>
{pi_card(members[0], 1)}
      </section>""")
        else:
            rows = "\n".join(alum_row(p, 1) for p in members if p.get("row"))
            cards = "\n".join(person_card(p, 1, interests=True)
                              for p in members if not p.get("row"))
            if JOIN_CARD and JOIN_CARD["section"] == title:
                cards = f"{cards}\n{join_card(1)}" if cards else join_card(1)
            body = f"{rows}\n" if rows else ""
            if cards:
                body += f'        <div class="people-grid">\n{cards}\n        </div>'
            sections.append(f"""      <section class="people-section">
        <h2>{title}</h2>
{body}
      </section>""")
    sections_html = "\n\n".join(sections)

    body = f"""      <section class="hero">
        <div class="hero-grid">
          <div>
            <h1>{_people["title"]}</h1>
            {_markdown.markdown(_people["intro"])}
          </div>

          <div class="card">
            <h3>{_people["card"]["title"]}</h3>
            <p>{_people["card"]["text"]}</p>
            <a class="btn" href="{site_url(_people["card"]["link"], 1)}">{_people["card"]["button"]} <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </section>

{sections_html}"""

    write("people/index.html", page(
        1, "people", "People",
        "Members of the Optimization and Estimation (ONE) Lab at the University of New Mexico.",
        body))


# One header for the whole Projects section. Every tab carries it, so the four
# pages read as parts of one thing rather than four separate pages; the seg-nav
# beneath it is what says which tab you are on.
# The header block on every Projects tab, written once in docs/pages/projects.md.
_ph, _ph_body = read_md(os.path.join(DOCS, "pages", "projects.md"))


def projects_hero(depth):
    return f"""      <section class="hero">
        <div class="hero-grid">
          <div>
            <h1>{_ph["title"]}</h1>
            {_markdown.markdown(_ph_body)}
          </div>

          <div class="card">
            <h3>{_ph["card"]["title"]}</h3>
            <p>{_ph["card"]["text"]}</p>
            <a class="btn" href="{site_url(_ph["card"]["link"], depth)}">{_ph["card"]["button"]} <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </section>"""


def projects_shell(active, title, intro, inner, extra_js="", badges="", depth=1):
    # The card sends visitors to the FAQ, which covers openings and how to apply.
    body = f"""{projects_hero(depth)}

      <section class="section">
{seg_nav(active, depth)}

{inner}
      </section>"""
    return page(depth, "projects", title,
                "Research and open-source projects of the ONE Lab at the University of New Mexico.",
                body, extra_js)


def build_projects():
    cards = "\n".join(
        project_card(d["image"], d["title"], f"research/{slug}/", d["summary"], 1, row=True)
        for slug, d, _ in PROJECTS)
    inner = f"""      <div class="project-grid project-grid--list">
{cards}
      </div>"""
    write("projects/index.html", projects_shell(
        "research", "Research Projects",
        "We integrate optimization, control theory, and machine learning to build theoretical "
        "foundations for networked cyber-physical systems, then turn them into practical, "
        "efficient, verifiable algorithms.",
        inner,
        badges='<div class="badges"><span class="badge">6 active directions</span>'
               '<span class="badge">Estimation</span><span class="badge">Safe control</span></div>'))

    # Software and Lab Spaces are plain prose pages, written in docs/pages/.
    # Every Projects tab is a folder, so its address ends in / (depth 2).
    for slug, key in (("software", "open-source"), ("lab_spaces", "lab")):
        data, body = read_md(os.path.join(DOCS, "pages", slug + ".md"))
        inner = f"""      <div class="prose">
{_markdown.markdown(body)}
      </div>"""
        write(f"projects/{slug}/index.html",
              projects_shell(key, data["title"], "", inner, depth=2))

    imgs = "\n".join(
        f'        <img src="{site_url("pic/gallery/" + f, 2)}" alt="{html.escape(alt)}" loading="lazy" />'
        for f, alt in GALLERY)
    inner = f"""      <div class="gallery-grid">
{imgs}
      </div>

{LIGHTBOX}"""
    write("projects/gallery/index.html", projects_shell(
        "gallery", "Gallery",
        "Conferences, demos, outreach, and the occasional round of Topgolf.",
        inner, extra_js=LIGHTBOX_JS, depth=2))

    # Project detail pages, one folder each so the address ends in /:
    # research projects in projects/research/<slug>/, software projects in
    # projects/<slug>/. `back:` in the project's .md says which it is.
    for slug, data, prose in load_docs("projects"):
        title, img, back = data["title"], data["image"], data["back"]
        software = back.startswith("software")
        eyebrow = "Software" if software else "Research Project"
        back_label = "All software" if software else "All research projects"
        depth = 2 if software else 3
        up = "../" * depth
        body_html = prose + doc_publications(data.get("publications"), depth) \
                          + doc_refs(data.get("refs"), depth)
        back = site_url("projects/software/" if software else "projects/", depth)
        back_link = (f'<p><a class="btn-ghost back-link" href="{back}">'
                     f'<span aria-hidden="true">&larr;</span> {back_label}</a></p>')
        # Research pages open with the back link, above the title; software
        # pages keep it at the foot of the panel.
        top = f"\n          {back_link}" if not software else ""
        foot = f"\n\n          {back_link}" if software else ""
        body = f"""      <section class="section">
        <div class="prose">{top}
          <div class="detail-head">
            <p class="detail-eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <img class="{art_class(img, True)}" src="{up}{img}" alt="" />
          </div>

{body_html}{foot}
        </div>
      </section>"""
        folder = f"projects/{slug}/" if software else f"projects/research/{slug}/"
        write(folder + "index.html", page(
            depth, "projects", title,
            f"{title} — a project of the ONE Lab at the University of New Mexico.", body))


def build_publications():
    pubs = "\n".join(pub_html(p["id"], 1) for p in _pubs["publications"])
    theses = "\n".join(pub_html(p["id"], 1) for p in _pubs.get("theses", []))
    # The card carries the lab's own accounts - the same icons as the footer.
    social = "\n              ".join(
        icon_link(kind, url, label) for kind, url, label in SITE["social"])

    body = f"""      <section class="hero">
        <div class="hero-grid">
          <div>
            <h1>Publications</h1>
            <p>{_pubs["intro"]}</p>
          </div>

          <div class="card">
            <h3>Elsewhere</h3>
            <div class="social-links" aria-label="Publication profiles">
              {social}
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>{_pubs["heading"]}</h2>

        <ul class="pub-list">
{pubs}
        </ul>
      </section>

      <section class="section">
        <h2>Theses</h2>

        <ul class="pub-list">
{theses}
        </ul>
      </section>"""

    write("publications/index.html", page(
        1, "publications", "Publications",
        "Publications and theses from the Optimization and Estimation (ONE) Lab.", body))


def build_news():
    cards = "\n".join(
        news_card(d, t, c, sm, r, 1) for d, t, c, _, sm, r in NEWS)
    social = "\n              ".join(
        icon_link(kind, url, label) for kind, url, label in SITE["social"])

    body = f"""      <section class="hero">
        <div class="hero-grid">
          <div>
            <h1>News</h1>
            <p>{NEWS_INTRO}</p>
          </div>

          <div class="card">
            <h3>Follow along</h3>
            <div class="footer-social" style="margin-top:12px">
              {social}
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="news-grid">
{cards}
        </div>
      </section>"""

    write("news/index.html", page(
        1, "news", "News", "News and updates from the ONE Lab at the University of New Mexico.",
        body))


def faq_slug(text):
    """A url fragment from a question or heading: lowercase words joined by
    hyphens, with the markup and punctuation dropped."""
    plain = re.sub(r"<[^>]+>", "", html.unescape(text))
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")[:60]


# A <details> stays shut when you jump to it, so a deep link would land on a
# closed question. This opens the targeted one - on click, and on load for a
# link followed from another page.
FAQ_JS = """  <script>
    (function () {
      function open(id) {
        var el = id && document.getElementById(decodeURIComponent(id));
        if (!el) return null;
        var d = el.closest("details");
        if (d) d.open = true;
        return el;
      }

      document.addEventListener("click", function (e) {
        var a = e.target.closest('a[href^="#"]');
        if (a) open(a.getAttribute("href").slice(1));
      });

      window.addEventListener("hashchange", function () {
        open(location.hash.slice(1));
      });

      var el = open(location.hash.slice(1));
      if (el) el.scrollIntoView();
    })();
  </script>"""


def parse_faq(body):
    """docs/pages/faq.md below the front matter -> [(heading, intro, [(q, open, answer)])].
    "## " starts a section, "### " a question; a trailing {open} starts it expanded.
    Questions before the first "## " form a section with no heading."""
    sections = [[None, [], []]]
    target = sections[0][1]
    for line in body.split("\n"):
        if line.startswith("## "):
            sections.append([line[3:].strip(), [], []])
            target = sections[-1][1]
        elif line.startswith("### "):
            q = line[4:].strip()
            is_open = q.endswith("{open}")
            q = q[:-len("{open}")].strip() if is_open else q
            sections[-1][2].append([q, is_open, []])
            target = sections[-1][2][-1][2]
        else:
            target.append(line)
    return [(h, "\n".join(i).strip(), [(q, o, "\n".join(a).strip()) for q, o, a in qs])
            for h, i, qs in sections if h or qs]


def build_faq():
    meta, body = read_md(os.path.join(DOCS, "pages", "faq.md"))
    opp = meta.get("opportunities")
    parts = []
    for heading, intro, items in parse_faq(body):
        qs = "\n".join(f"""        <details class="faq-item" id="{faq_slug(q)}"{" open" if is_open else ""}>
          <summary>{CHEV}<span>{q}</span></summary>
          <div class="faq-answer">{_markdown.markdown(a)}</div>
        </details>""" for q, is_open, a in items)
        head = f'\n        <h2 id="{faq_slug(heading)}">{heading}</h2>' if heading else ""
        pre = f"\n        {_markdown.markdown(intro)}" if intro else ""
        parts.append(f"""      <section class="section">{head}{pre}

        <div class="faq-list">
{qs}
        </div>
      </section>""")
        if opp and heading == opp.get("after"):
            parts.append(f"""      <section class="hero">
        <div class="hero-grid">
          <div>
            <p class="section-label">{opp["label"]}</p>
            <p>{opp["text"]}</p>
          </div>

          <div class="card">
            <h3>{opp["card"]}</h3>
            <a class="btn" href="{opp["link"]}"{TARGET_BLANK}>{opp["button"]} <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </section>""")
    body = "\n\n".join(parts)

    write("faq/index.html", page(
        1, "faq", "FAQ",
        "Frequently asked questions about joining and working in the ONE Lab.", body, extra_js=FAQ_JS))



def main():
    build_home()
    build_people()
    build_projects()
    build_publications()
    build_news()
    build_faq()
    return flush()


if __name__ == "__main__":
    raise SystemExit(main())
