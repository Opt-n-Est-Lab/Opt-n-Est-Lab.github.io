# ONE Lab website

The source of [one.unm.edu](https://one.unm.edu). Every page is built from
Markdown files in `_build/docs/`: edit those, never the `.html` files.

## 1. Get the code (once)

```sh
git clone https://github.com/Opt-n-Est-Lab/Opt-n-Est-Lab.github.io.git
cd Opt-n-Est-Lab.github.io
python3 -m pip install markdown pyyaml
```

## 2. Update

Start from the latest version, so you don't overwrite someone else's change:

```sh
git pull
```

Then edit the file for what you want to change, in `_build/docs/`:

| To change | Edit |
|---|---|
| News | `news.md` (newest first; the home page shows the first three) |
| Publications | `publications.md` |
| People | `people.md` |
| A research project | `projects/<name>.md` |
| Header, nav, footer, contact details | `site.md` |
| Gallery photos | `gallery.md` |
| Home, FAQ and other page text | `pages/*.md` |

Copy an entry next to the one you are adding. New pictures go in `pic/`; news
pictures should be square.

## 3. Build

```sh
python3 _build/build.py
```

To preview, run `python3 -m http.server 8000` and open http://localhost:8000.
(Double-clicking an `.html` file won't work: its links point at folders.)

If the build stops and names a page, that page's `.html` was edited directly;
see [`_build/README.md`](_build/README.md).

## 4. Push

```sh
git status
git add .
git commit -m "xxxxx"
git push origin main
```

`git add .` includes both your Markdown edit and the rebuilt `.html` pages.
[opt-n-est-lab.github.io](https://opt-n-est-lab.github.io) updates a minute or
two after the push. one.unm.edu is a copy on UNM's server and updates when that
server pulls from GitHub (`git_sync.sh`).

---

How each file is written, the design system and other notes:
[`_build/README.md`](_build/README.md).
