from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"

    html = read_text(app_dir / "index.html")
    css = read_text(app_dir / "styles.css")
    data = read_text(app_dir / "data.js")
    js = read_text(app_dir / "app.js")

    html = html.replace('<link rel="stylesheet" href="./styles.css" />', f"<style>\n{css}\n</style>")
    html = html.replace('<script src="./data.js"></script>', f"<script>\n{data}\n</script>")
    html = html.replace('<script src="./app.js"></script>', f"<script>\n{js}\n</script>")

    out = root / "word-builder-1200-single-file.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
