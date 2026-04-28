# text2speech

## Word Builder 1200 字根組字彙教學站

一個用字首、字根、字尾拆解英文單字的靜態教學站。內建 1200 個常用單字、字根家族課程、組字工坊、快問快答，以及瀏覽器發音功能。

## Features

- 1200 個常用英文單字
- 字首 + 字根 + 字尾組字分析
- 字根家族課程卡
- 字根快問快答練習
- 單字搜尋與瀏覽器發音
- PWA 離線快取與安裝支援

## Project Paths

- `app/` - GitHub Pages app source
- `pwa-app/` - installable PWA package with local dev server
- `android-app/` - Android WebView wrapper
- `word-builder-1200-single-file.html` - bundled single-file version
- `blogger-word-builder-1200.html` - Blogger embed version

## Run Locally

```powershell
cd C:\text2speech\pwa-app
npm.cmd run dev
```

Then open:

```text
http://localhost:4173
```

## Regenerate Assets

Generate the dataset:

```powershell
python tools/generate_dataset.py
```

Bundle the single-file app:

```powershell
python tools/bundle_single_file.py
```

Build the Blogger embed:

```powershell
python tools/build_blogger_embed.py
```

## Published App

- GitHub Pages: [Word Builder 1200](https://j945935cy.github.io/text2speech/word-builder-1200-single-file.html)
