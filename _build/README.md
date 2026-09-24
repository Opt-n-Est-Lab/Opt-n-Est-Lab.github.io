# `_build/` — the site generator

**Edit the Markdown in `docs/` (in this folder), then run:**

```
python3 _build/build.py            rebuild every page
python3 _build/build.py --check    show what would change, write nothing
```

The `.html` files are build output. An edit made to one directly is lost on the
next build. If a page was edited by hand, the build stops, names the page and
copies it to `_build/_backup/`; `--force` builds over it anyway.

Needs `markdown` and `pyyaml`: `python3 -m pip install markdown pyyaml`.

## What lives where

| file | what it drives |
|---|---|
| `docs/site.md` | header, nav, footer, social links, emails — every page |
| `docs/news.md` | all news, newest first; the home page shows the first three |
| `docs/publications.md` | every paper **once**, each with an `id` |
| `docs/projects/*.md` | one per research project: its page, `order`, card `summary`, and `publications:` as a list of ids |
| `docs/people.md` | the People page — groups, cards, alumni rows |
| `docs/gallery.md` | the Gallery photos |
| `docs/pages/home.md` | the home page intro and section headings |
| `docs/pages/projects.md` | the header block on every Projects tab |
| `docs/pages/software.md`, `lab_spaces.md` | those two tabs |
| `docs/pages/faq.md` | the FAQ: `##` a section, `###` a question, `{open}` starts it expanded |
| `build.py` | page **layouts** only — no page text |

## How a file is written

Each file starts with YAML settings between two `---` lines; anything below
the second `---` is Markdown prose:

```markdown
---
title: Reservoir Computing
order: 1
publications:
  - lora-rc-2026        # an id from publications.md
---

This project leverages the reservoir computing (RC) architecture…
```

In the text, `*italic*` and `**bold**` work, and HTML is fine where Markdown has
no equivalent. Links in the settings — a paper's or news item's `links:`, a
card's `link:` — are written from the site root (`file/IFAC_IAV_2025_Phoenix.pdf`)
and the build adds the right `../` for each page. A link typed into the prose
itself is used exactly as written.

## Common edits

Every one of these is an edit to a file in `_build/docs/`, followed by
`python3 _build/build.py`. Copy the entry next to the one you are adding.

**Add a news item.** Add a block at the top of `items:` in `news.md`. The home
page shows the newest three automatically; the news page shows them all.

> **Always use a square picture for news.** The picture is a fixed square, so a
> square source is shown whole; anything else is centre-cropped. Set
> `framed: true` on logos and diagrams to letterbox them inside the square.

**Add a publication.** Add an entry to `publications.md` with a new `id`. To
show it on a project page, add that `id` to the project's `publications:`
list in `projects/<name>.md` — the paper itself is never typed twice.

**Add a person.** Add an entry to the right group in `people.md`. `honors` is a
list; `interests` is the badge at the foot of the card; `row: true` turns an
alum into a one-line row.

**Change the header, nav, footer, contact details or a social link.** Edit
`site.md`. It feeds every page.

**Reorder the research projects.** Change `order:` in each `projects/*.md`. The
home page and the Projects page both follow it.

**Retire a project.** Delete its file from `projects/`. The next build removes
its page, as it does any page it no longer makes, unless that page was edited
by hand, in which case the build leaves it and names it.

**Edit a page's text.** `pages/home.md`, `pages/projects.md` (the header on all
Projects tabs), `pages/software.md`, `pages/lab_spaces.md`, `pages/faq.md`.

## Site layout

From the site root:

```
index.html              Home — welcome line, hero, about, research, latest news
styles.css              The entire design system (see below)
people/index.html       Member cards in a grid, category shown as a pill
projects/
  index.html            Research projects
  software/index.html
  lab_spaces/index.html
  gallery/index.html    Photo grid with lightbox
  research/
    <project>/index.html  One page per research project (the six on index.html)
  <project>/index.html  Software project pages, beside software/
publications/index.html Publications and theses
news/
  index.html            All news cards (items have no pages of their own)
faq/index.html          Collapsible Q&A
rcukf/                  Standalone RCUKF paper page (untouched, see Notes)
pic/                    Every image the site uses
  profile/              People photos (also used by news cards that show a person)
    alumni/             Alumni photos, kept together
  project/              Project illustrations
  news/                 Pictures used only by news cards
  gallery/              Gallery page photos
  site/                 Logo, banners, favicon
fonts/                  The five Linux Libertine faces the stylesheet loads
_bin/                   Unused files set aside for review (not published; see Notes)

_build/                 The generator — source of every .html above
  build.py              Page layouts: shared <head>, header, footer, cards
  docs/                 Everything the pages SAY, as Markdown (see What lives where)
```

The generated pages are fully self-contained — the header and footer markup is
baked into each file rather than fetched at runtime — so every page works with
JavaScript disabled, needs no server-side includes, and GitHub Pages serves it
untouched. The generator gives you single-source editing without paying for that
at runtime.

All internal links are **relative and point at the folder** (`../people/`, not
`../people/index.html`), so addresses read `…/people/`. In `site.md` and the
other docs, write them from the site root (`people/`, `faq/#some-question`;
`./` is the home page). A folder only opens its `index.html` when the site is
served, so preview with `python3 -m http.server`: double-clicking an `.html`
file opens it, but its links then show folder listings.

## Shared page furniture

Every page opens with the **banner** directly under the header, then its own
content. There are two files: `pic/site/onelab_banner.jpg` for light mode and
`pic/site/onelab_banner_dark.jpg` for dark, both emitted in `page()` in
`build.py` with CSS showing whichever matches the theme. The dark file was
generated from the light one (grey ground flipped dark, blue wordmark kept), so
**if the banner artwork is replaced, the dark version needs regenerating** —
it will not update on its own. The spacing rules `.banner + .hero` /
`.banner + .section` / `.banner + .welcome` in `styles.css` set what follows
it. The header and footer are likewise written once in `header()` and
`footer()`.

## The design system

The visual design is ported from the Insect-scale Autonomy workshop site and
retinted to the ONE Lab brand blue.

Everything lives in `styles.css`, driven by CSS custom properties on `:root`.
Nothing is hard-coded per page.

### Themes

Light and dark are both first-class. The theme is stored on
`document.documentElement.dataset.theme`; a small inline script in each `<head>`
applies it *before* first paint so there is no flash. **Every visit starts
light**, whatever the visitor's system setting. Switching to dark with the
toggle is kept in `sessionStorage`, so it holds while they browse and resets on
their next visit.

Every color is defined in the light `:root` block and then redefined in
`:root[data-theme="dark"]`. If you add a color, add it to both.

### Changing the accent color

Swap the four values in each `:root` block:

| Token | Light | Dark |
|---|---|---|
| `--link` | `#4a5bb0` | `#93a4e6` |
| `--link-hover` | `#37468f` | `#b4c0ef` |

The amber/honey values from the original workshop site are noted in comments
next to each one if you ever want that look back.

The accent also tints the panels and the glass surfaces, via `--panel`,
`--panel2` and `--line`, so those are worth shifting to match if you change it
to something far from blue.

### Page background

Flat: white in light mode, near-black in dark. There is no gradient wash.

Worth knowing if you are editing the glass: `backdrop-filter` blurs whatever is
behind an element, and behind these is now a flat colour, so the blur itself
contributes nothing on the page background. The glass still reads because of
its gradient fill, its specular top edge and its shadow — but the material will
look flatter over plain background than it does over the cards and images it
overlaps when the page is scrolled.

### Typography

**Linux Libertine**, served from `fonts/` — the same typeface the lab has always
used. Five faces are registered with `@font-face`:

| File | Used for |
|---|---|
| `LinLibertine_R.woff` | body text, regular |
| `LinLibertine_RI.woff` | italic |
| `LinLibertine_RB.woff` | bold |
| `LinLibertine_RBI.woff` | bold italic |
| `LinLibertine_aBS.woff` | headings — the bold **small-caps** display cut |

Two tokens control it: `--font-body` for everything, and `--font-display` for
`h1` and `h2`. That small-caps display cut is what gives the page and section
headings their character; it is the same face the previous site used. `h3` —
card titles, people's names, project names — stays in the text face, bold, so
small caps are reserved for the larger structural headings.

Libertine has a noticeably lower x-height than a system sans, so text set at a
given pixel size reads about one step smaller. Every size in the stylesheet is
tuned for that — base body text is `17px`, and the small UI sizes were raised to
match. **If you ever switch back to a sans-serif, lower them again** or the
page will look oversized. The `SANS OPTION` comment in `:root` says how.

Font files load with `font-display: swap`, so text paints immediately in Georgia
and reflows to Libertine once the face arrives.

### Artwork classes — important

Three kinds of image live on this site and each needs different handling in dark
mode. When you add an image, give it the right class or it will look wrong:

- **`.art-mark`** — flat single-color ONE Lab logos. Lifted with a brightness
  filter so the brand blue stays legible on near-black.
- **`.art-illus`** — full-color illustrations that carry their own white ground
  (everything in `pic/project/`). Filtering blows out the whites, so these sit
  on a light plate instead.
- **`.art-photo`** — photographs. Left completely alone.

### Page width

The content column is **700px**, matching the previous ONE Lab site
(`.container { width: 700px }`). It is set once, as `--max: 736px` in `:root`
— 700px of content plus the container's 2×18px side padding.

Grid breakpoints are tuned for this narrow column rather than for the viewport:
news is three columns down to 700px, two to 520px, then one.

The nav has five items — Home, People, Projects, Publications, FAQ — which is
what fits on one row beside the brand at this width. **News is deliberately not
in the nav:** it is reached from the home page's "All news" button. The brand block (logo + tagline) is a static
lockup, not a link.

### Reusable pieces

`.hero` / `.hero-grid` / `.badge`, `.card`, `.prose`, `.section`, `.btn`,
`.btn-ghost`, `.ref-link`, `.seg-nav`, `.project-card`, `.news-card`,
`.person-card`, `.pub-item`, `.faq-item`, `.gallery-grid`, `.icon-link`.

Copy an existing block rather than writing new CSS — that is what keeps the
pages consistent.

## Accessibility and behavior notes

- The collapsible sections on **FAQ** are native `<details>`/`<summary>` —
  they work without JavaScript and are keyboard and screen-reader accessible.
  The only JavaScript on the site is the theme toggle and the gallery lightbox.
- Below ~740px the header becomes two rows — brand and theme toggle, then the
  nav pills centred beneath — so the nav is in the header at every width. There
  is no separate mobile nav.
- `prefers-reduced-motion` is respected: all transitions and the fade-up
  animation are disabled.
- Every decorative image has `alt=""`; every icon link has an `aria-label`.

## Notes

- **`_bin/`** holds files nothing on the site uses: old logos and icons, spare
  photos, unused font cuts and a flyer PDF. Each file keeps its original folder
  path inside `_bin/` (e.g. `_bin/pic_profile/lab.jpg`) so you can tell where it
  came from. Like `_build/`, it starts with an underscore, so GitHub Pages does
  not publish it. Delete what you do not need; move anything back into `pic/`
  and reference it to use it again.
- **Image folders cannot start with `_`.** GitHub Pages hides those, so an
  image there would break on the live site. That is why the image folder is
  `pic/`, not `_pic/`.
- **`rcukf/`** is a separate Bulma-based paper page authored by Kumar Anurag with
  its own styling and canonical URL. It was copied across untouched and does not
  follow this design system. It contains a placeholder link to `pdfs/Sample.pdf`
  that does not exist — that was already broken in the previous site.
- Google Analytics (`G-SW68LZVXCV`) is carried over unchanged in every page head.
