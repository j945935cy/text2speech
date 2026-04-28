# text2speech

## Word Builder 1200 字根組字彙教學站

一個用字首、字根、字尾拆解英文單字的靜態教學站。內建 1200 個常用單字、字根家族課程、組字工坊、拆解示範，以及瀏覽器發音功能。

## Features

- 1200 個常用英文單字
- 字首 + 字根 + 字尾組字分析
- 字根家族課程卡
- 字根拆解示範
- 單字搜尋與瀏覽器發音
- PWA 離線快取與安裝支援
- Google Play Books EPUB 輸出

## Project Paths

- `app/` - GitHub Pages app source
- `pwa-app/` - installable PWA package with local dev server
- `android-app/` - Android WebView wrapper
- `word-builder-1200-single-file.html` - bundled single-file version
- `blogger-word-builder-1200.html` - Blogger embed version
- `dist/google-play-books/word-builder-1200-google-play.epub` - generated EPUB output

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

Build the Google Play Books EPUB:

```powershell
python tools/build_epub.py
```

## EPUB Notes

The EPUB build uses the existing word data from `app/data.js`.

- EPUB format: EPUB 3
- Cover image: `app/icons/icon-512.png`
- Output path: `dist/google-play-books/word-builder-1200-google-play.epub`
- The vocabulary table is split into 100-word chapters for easier reading.
- The morphology split is for learning and review, not a strict etymology dictionary.

## Published App

- GitHub Pages: [Word Builder 1200](https://j945935cy.github.io/text2speech/word-builder-1200-single-file.html)
