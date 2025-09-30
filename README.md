# envsubst-windows-linux
<p align="center">
  <img src="https://img.shields.io/badge/zero%20deps-✔-00E5FF?style=for-the-badge">
  <img src="https://img.shields.io/badge/cross%20platform-win%20%7C%20mac%20%7C%20linux-777?style=for-the-badge">
  <img src="https://img.shields.io/github/actions/workflow/status/xryv/envsubst-windows-linux/ci.yml?style=for-the-badge">


</p>

# envsubst-windows-linux

**One-file, zero-dependency `envsubst` for Windows, macOS, and Linux.**  
Substitute `${VAR}` or `{{VAR}}` from `.env` and environment into any text files.

> Perfect for Docker/K8s YAML, GitHub Actions, Markdown, NGINX configs—without installing GNU `envsubst`.

![demo](assets/demo.gif) <!-- placeholder -->

## Why?
- Windows users struggle with GNU `envsubst`.  
- Most tools need Node/Python packages or shells not present in CI.  
- This is **a single Python script**—drop it in any repo and run.

## Features
- `${VAR}` and `{{VAR}}` patterns
- `.env` + current environment
- Globs & directories (recursive)
- `--check` for missing vars (CI-friendly)
- `--safe` leaves unknown placeholders intact
- `--dry-run` prints a tiny diff-like preview
- In-place or `--out` directory rendering

## Install
- **Option A (quick):** copy `cli.py` + `core.py` into your repo.
- **Option B:** `git clone` the repo and run in place.

Requires **Python 3.8+** (preinstalled on most systems).

## Quick Start
```bash
echo "SERVICE_NAME=api" > .env
echo "PORT=8080" >> .env
echo "IMAGE_TAG=api:latest" >> .env
echo "API_URL=https://example.com" >> .env

python3 cli.py examples/example.yml --env .env --out dist
cat dist/examples/example.yml


