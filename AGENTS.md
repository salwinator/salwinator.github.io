# Obsidian + Hugo Blog Setup

## Overview

Personal blog built with Hugo (hugo-bearblog theme). The Hugo `content/` directory is opened directly as an Obsidian vault — edits in Obsidian reflect instantly on the local Hugo server. Deployed to GitHub Pages via GitHub Actions.

## Key Paths

| Purpose | Path |
|---|---|
| Hugo project root | `/Users/salwynmathew/Code/my-blog/` |
| Hugo config | `/Users/salwynmathew/Code/my-blog/hugo.toml` |
| Obsidian vault / Hugo content dir | `/Users/salwynmathew/Code/my-blog/content/` |
| Blog posts | `/Users/salwynmathew/Code/my-blog/content/blog/` |
| Static assets (images) | `/Users/salwynmathew/Code/my-blog/static/images/` |
| GitHub Actions workflow | `/Users/salwynmathew/Code/my-blog/.github/workflows/hugo.yml` |

## Hugo Configuration

- **Hugo version:** v0.160.1 (extended+withdeploy), installed via Homebrew
- **Theme:** `hugo-bearblog`
- **`baseURL`:** `https://salwinator.github.io/`
- **`contentDir`:** `content` (relative to project root)
- **`timeZone`:** `Asia/Kolkata` (IST) — prevents today-dated posts from being treated as future
- **`ignoreFiles`:** `.obsidian`, `.trash`, `Templates`
- **`hideMadeWithLine`:** `true`

## Deployment

- **GitHub repo:** `https://github.com/salwinator/salwinator.github.io`
- **Live site:** `https://salwinator.github.io/`
- **Deploy method:** GitHub Actions — auto-deploys on every push to `master`
- **Pages source:** GitHub Actions (not legacy branch mode)
- Blog post URLs: `https://salwinator.github.io/<slug>/`

## Publish Workflow

1. Write post in Obsidian (vault is `content/`) under `content/blog/`
2. Set `draft: false` in frontmatter when ready to publish
3. For images: paste into Obsidian — attachments are saved to `static/images/` (configured in Obsidian settings). Rename to remove spaces, then use standard Markdown: `![alt](/images/filename.png)`
4. Commit and push:
   ```bash
   git add . && git commit -m "Add post: <title>" && git push
   ```
5. GitHub Actions builds and deploys automatically (~1 min)

## Local Preview

```bash
cd /Users/salwynmathew/Code/my-blog && hugo server -D
```

Edits in Obsidian reflect instantly — no sync step needed.

## Post Frontmatter Format

```yaml
---
title: "My Post Title"
date: "2026-04-30"
description: ""
tags: []
draft: false
---
```

- `draft: true` = visible locally with `hugo server -D`, hidden in production
- `draft: false` = published
- Dates in IST — Hugo is configured for `Asia/Kolkata`

## Known Quirks

- **Spaces in filenames break Markdown image rendering** — always rename images to use hyphens before using them
- **Obsidian `![[image]]` syntax is not supported** — use `![alt](/images/filename.png)`
- **IST timezone** — without `timeZone = "Asia/Kolkata"`, posts dated today are treated as future and excluded from builds
