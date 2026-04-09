# Word Builder 1200 PWA

Word Builder 1200 is a static `HTML/CSS/JavaScript` Progressive Web App for learning English word formation with prefixes, roots, suffixes, and built-in pronunciation.

## Project Structure

```text
pwa-app/
  index.html
  manifest.webmanifest
  sw.js
  package.json
  assets/
    css/styles.css
    js/app.js
    data/data.js
    icons/
  scripts/
    dev-server.js
```

## Run Locally

Use the built-in Node static server:

```powershell
cd C:\text2speech\pwa-app
npm.cmd run dev
```

Then open:

```text
http://localhost:4173
```

## Notes

- `assets/data/data.js` contains the generated 1200-word dataset.
- `sw.js` enables offline caching for PWA behavior.
- iPhone and Android can both install this app from the browser when hosted over `https`.
- `file://` opening is not recommended because service workers and install behavior need a real web origin.
