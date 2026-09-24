# ONE Lab website

The source of [one.unm.edu](https://one.unm.edu), the website of the
Optimization and Estimation (ONE) Lab at the University of New Mexico.

**Anyone with a GitHub account can suggest a change** — a news item, a new
paper, an updated bio, a fix for a typo. Report a problem as an *issue*, or
propose the change yourself as a *pull request*; the maintainer reviews it and
publishes it. Only the maintainer changes the site directly.

## Report a problem

For a typo, a broken link, a picture that doesn't show, or anything else that
looks wrong, [open an issue](https://github.com/Opt-n-Est-Lab/Opt-n-Est-Lab.github.io/issues/new).
Say which page, what's wrong and, if you know it, what it should say. You don't
need git; the maintainer makes the fix.

## Propose a change

To make a change yourself, such as adding a news item, a paper or a bio, you
need a GitHub account, git and Python 3.

### 1. Set up (once)

On GitHub, click **Fork** on this repository's page, then **Create fork**. That
makes your own copy at `github.com/<your-username>/Opt-n-Est-Lab.github.io`.
Then:

```sh
git clone https://github.com/<your-username>/Opt-n-Est-Lab.github.io.git
cd Opt-n-Est-Lab.github.io
git remote add upstream https://github.com/Opt-n-Est-Lab/Opt-n-Est-Lab.github.io.git
python3 -m pip install markdown pyyaml
```

`origin` is your fork; `upstream` is the lab's repository.

### 2. Start from the latest version

Each time you start a change:

```sh
git checkout main
git pull upstream main
git checkout -b my-change
```

Replace `my-change` with a short name for your change, for example
`news-best-paper-award`, and use the same name in step 5.

### 3. Edit

All the text on the site lives in the Markdown files under
[`_build/docs/`](_build/docs/). Change those, never the `.html` files: the pages
are rebuilt from the Markdown, so an edit to an `.html` file is lost.

| To change | Edit, in `_build/docs/` | Pictures go in |
|---|---|---|
| News | `news.md` (newest first) | `pic/news/` (square pictures) |
| Publications | `publications.md` | |
| People | `people.md` | `pic/profile/` |
| A research project | `projects/<name>.md` | `pic/project/` |
| Gallery photos | `gallery.md` | `pic/gallery/` |
| Home, FAQ and other page text | `pages/*.md` | |
| Header, nav, footer, contact details | `site.md` | |

Each file explains its fields at the top. The easiest way to add something is
to copy the entry next to it and change the words. Type picture names exactly,
capitals included: the live site treats `Photo.JPG` and `photo.jpg` as
different files.

### 4. Build and check

```sh
python3 _build/build.py
python3 -m http.server 8000
```

Open http://localhost:8000 and check your change. Press Ctrl+C to stop the
server.

### 5. Push and open a pull request

```sh
git add _build/docs pic
git commit -m "Add news: best paper award"
git push -u origin my-change
```

This commits only `_build/docs` and `pic`; the maintainer rebuilds the pages
after merging.

Then open your fork on GitHub, click **Compare & pull request**, say what the
change is (with a link to the paper or event, if there is one), and click
**Create pull request**.

Finally, discard the pages your build changed, so your next pull is clean:

```sh
git status     # should list only .html files and _build/manifest.json
git restore .
```

### What happens next

The maintainer reviews your pull request and either merges it or leaves a
comment. To follow up, edit on the same branch, commit and `git push`: the pull
request updates itself. Once it is merged, the change appears on the site with
the maintainer's next build. For your next change, start again at step 2.

Keep each pull request to one change, such as one news item.

---

## Maintainer

Only the maintainer pushes to `main`.

### 1. Get the code (once)

```sh
git clone https://github.com/Opt-n-Est-Lab/Opt-n-Est-Lab.github.io.git
cd Opt-n-Est-Lab.github.io
python3 -m pip install markdown pyyaml
```

### 2. Update

Start from the latest version, so you don't overwrite someone else's change:

```sh
git pull
```

Then edit the files you need; the table in [3. Edit](#3-edit) shows which.

### 3. Build

```sh
python3 _build/build.py
```

To preview, run `python3 -m http.server 8000` and open http://localhost:8000.
(Double-clicking an `.html` file won't work: its links point at folders.)

If the build stops and names a page, that page's `.html` was edited directly;
see [`_build/README.md`](_build/README.md).

### 4. Push

```sh
git status
git add .
git commit -m "xxxxx"
git push origin main
```

`git add .` includes both your Markdown edit and the rebuilt `.html` pages.
[opt-n-est-lab.github.io](https://opt-n-est-lab.github.io) updates a minute or
two after the push. The copy at one.unm.edu, on UNM's server, updates when that
server pulls from GitHub (`git_sync.sh`).

### 5. Merging a pull request

On GitHub, open the pull request, check **Files changed**, and click **Merge
pull request**. Pull requests change only the Markdown and pictures, so build
and push the pages yourself:

```sh
git pull
python3 _build/build.py
git add .
git commit -m "Build"
git push origin main
```

---

How each file is written, the design system and other notes:
[`_build/README.md`](_build/README.md).
