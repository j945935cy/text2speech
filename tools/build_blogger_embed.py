from pathlib import Path
import re


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def scope_css(css: str, scope: str) -> str:
    scoped_lines = []
    blocks = re.findall(r"([^{]+)\{([^}]*)\}", css, flags=re.S)
    for raw_selectors, body in blocks:
        selectors = raw_selectors.strip()
        body = body.strip()
        if not selectors or not body:
            continue
        if selectors.startswith("@"):
            scoped_lines.append(f"{selectors}{{{body}}}")
            continue
        scoped = []
        for selector in selectors.split(","):
            selector = selector.strip()
            if selector == ":root":
                scoped.append(scope)
            elif selector.startswith("@"):
                scoped.append(selector)
            else:
                scoped.append(f"{scope} {selector}")
        scoped_lines.append(", ".join(scoped) + " {" + body + "}")
    return "\n\n".join(scoped_lines)


def convert_html_fragment(html: str) -> str:
    body_match = re.search(r"<body>(.*)</body>", html, flags=re.S)
    fragment = body_match.group(1).strip() if body_match else html
    fragment = fragment.replace('<script src="./data.js"></script>', "")
    fragment = fragment.replace('<script src="./app.js"></script>', "")
    fragment = fragment.replace('<link rel="stylesheet" href="./styles.css" />', "")
    return fragment


def scope_js(js: str) -> str:
    return js.replace("document.querySelector(", "root.querySelector(")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"

    html = read_text(app_dir / "index.html")
    css = read_text(app_dir / "styles.css")
    data = read_text(app_dir / "data.js")
    js = read_text(app_dir / "app.js")

    fragment = convert_html_fragment(html)
    scoped_css = scope_css(css, "#wb1200-blogger-root")
    scoped_js = scope_js(js)

    out = f"""<div id="wb1200-blogger-root">
{fragment}
</div>
<style>
{scoped_css}
</style>
<script>
{data}
(function() {{
  const root = document.getElementById("wb1200-blogger-root");
  if (!root) return;
{scoped_js}
}})();
</script>
"""

    out_path = root / "blogger-word-builder-1200.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
