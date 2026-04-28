import json
import re
import shutil
import time
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile
from xml.etree import ElementTree


BOOK_TITLE = "Word Builder 1200 字根組字彙教學"
BOOK_IDENTIFIER = "urn:uuid:word-builder-1200-root-vocabulary"
BOOK_AUTHOR = "Word Builder 1200"
BOOK_LANG = "zh-Hant"
MODIFIED = "2026-04-28T00:00:00Z"

ROOT_NOTES = {
    "act": ("做、行動", "act 是動作的核心，常延伸成行為、互動、反應。"),
    "form": ("形狀、形成", "form 把抽象想法變成形狀，也常用在制度與格式。"),
    "port": ("帶、搬運", "port 讓你看到 transport、support、report 這類移動或承載的概念。"),
    "view": ("看、觀點", "view 連到看見、檢視、觀點，也能延伸到 review。"),
    "play": ("玩、演出", "play 從遊戲延伸到表演、播放與角色運作。"),
    "use": ("使用", "use 可變成 useful、user、reuse，適合觀察字尾改變詞性。"),
    "move": ("移動", "move 連到 remove、movement，能看出字首如何改變方向。"),
    "press": ("壓、推", "press 常出現在 pressure、express、impress 等壓力與表達概念。"),
    "light": ("光、輕", "light 有光亮與輕的雙核心，要靠語境判斷。"),
}

PREFIX_NOTES = {
    "re": "再、回來",
    "un": "不、相反",
    "pre": "之前",
    "dis": "分開、否定",
    "in": "在內、不",
    "im": "不、進入",
    "over": "過度、在上",
    "under": "不足、在下",
}

SUFFIX_NOTES = {
    "er": "人或比較級",
    "ing": "正在、動名詞",
    "ed": "過去、完成",
    "ly": "副詞",
    "tion": "名詞化",
    "ion": "動作或結果名詞",
    "ment": "結果或狀態",
    "ness": "性質",
    "ful": "充滿",
    "less": "缺少",
}

MEANING_ZH = {
    "act, process": "動作或過程",
    "again": "再次、回到原狀",
    "before": "在前、預先",
    "below": "在下、不足",
    "between": "在兩者之間",
    "capable of": "能夠、可以",
    "care": "照顧、關心",
    "carry": "帶、搬運",
    "characterized by": "具有某種特性",
    "clear": "清楚、明白",
    "construct": "建造、組成",
    "core meaning": "基礎字，保留原字意思",
    "do": "做、行動",
    "down, remove": "向下、移除",
    "friend": "朋友、友善",
    "full of": "充滿、具有",
    "go see": "去看、探訪",
    "grow": "成長、增加",
    "guide": "引導、指引",
    "having the nature of": "具有某種性質",
    "help": "幫助、支持",
    "hope": "希望、期待",
    "in a ... way": "以某種方式",
    "just": "公正、正好",
    "kind": "種類、仁慈",
    "knowledge": "知識、理解",
    "make": "製造、使成為",
    "make, become": "使成為、變成",
    "most": "最多、最",
    "move": "移動、改變位置",
    "nation": "國家、民族",
    "nature": "自然、本質",
    "not": "不、否定",
    "not, into": "不、否定；或表示進入",
    "not, opposite": "不、相反",
    "ongoing action": "正在進行的動作",
    "one who, more": "表示人；或比較級",
    "out": "向外、離開",
    "past": "過去、完成",
    "person or thing that": "表示人或事物",
    "play": "玩、演出、播放",
    "read": "閱讀、理解",
    "related to": "與某事相關",
    "press": "壓、推、施加壓力",
    "process or result": "過程或結果",
    "result, process": "結果或過程",
    "rule": "規則、管理",
    "safe": "安全、保護",
    "see": "看見、理解",
    "shape": "形狀、形成",
    "somewhat": "有點、稍微",
    "speak": "說話、表達",
    "state": "狀態、情況",
    "state of": "某種狀態",
    "state or quality": "狀態或性質",
    "state, skill, relation": "狀態、能力或關係",
    "teach": "教導、指導",
    "together": "共同、一起",
    "under": "在下、低於",
    "use": "使用、用途",
    "work": "工作、運作",
    "write": "書寫、記錄",
    "wrongly": "錯誤地、不當地",
}

BASE_WORD_ZH = {
    "about": "關於、大約",
    "after": "在...之後",
    "all": "全部、所有",
    "also": "也、同樣",
    "and": "和、以及",
    "another": "另一個",
    "around": "周圍、大約",
    "as": "作為、如同",
    "at": "在某處或某時",
    "back": "背後、返回",
    "be": "是、存在",
    "because": "因為",
    "been": "曾經是、已經",
    "but": "但是",
    "by": "藉由、在旁邊",
    "can": "能夠、可以",
    "could": "能夠、可能",
    "current": "目前的、當前的",
    "day": "日子、白天",
    "did": "做了",
    "do": "做、執行",
    "down": "向下、在下方",
    "each": "每一個",
    "example": "例子、範例",
    "experience": "經驗、體驗",
    "first": "第一、首先",
    "for": "為了、對於",
    "from": "從、來自",
    "good": "好的、良好的",
    "great": "偉大的、很棒的",
    "had": "曾有、已經",
    "has": "有、已經",
    "have": "有、擁有",
    "he": "他",
    "heard": "聽到、聽見",
    "her": "她的、她",
    "here": "這裡",
    "him": "他",
    "his": "他的",
    "how": "如何、怎樣",
    "if": "如果",
    "in": "在...裡面",
    "into": "進入",
    "is": "是",
    "it": "它、這件事",
    "just": "只是、剛好",
    "know": "知道、了解",
    "like": "喜歡、像",
    "london": "倫敦",
    "made": "製造、完成",
    "make": "製造、使成為",
    "many": "許多",
    "may": "可能、可以",
    "meet": "遇見、會面",
    "more": "更多",
    "most": "最多、大多數",
    "much": "很多、非常",
    "new": "新的",
    "no": "不、沒有",
    "not": "不、否定",
    "of": "屬於、關於",
    "on": "在...上",
    "one": "一個",
    "only": "只有、唯一",
    "or": "或者",
    "other": "其他的",
    "out": "出去、向外",
    "over": "在上方、超過",
    "people": "人們",
    "program": "節目、程式、計畫",
    "said": "說了",
    "same": "相同的",
    "see": "看見、理解",
    "she": "她",
    "so": "所以、如此",
    "some": "一些",
    "such": "這樣的、如此的",
    "take": "拿取、採取",
    "than": "比、相較於",
    "that": "那、那個",
    "the": "這個、那個",
    "their": "他們的",
    "them": "他們",
    "then": "然後、那時",
    "there": "那裡、有",
    "these": "這些",
    "they": "他們",
    "thing": "事情、東西",
    "this": "這、這個",
    "time": "時間、次數",
    "to": "到、向、為了",
    "two": "兩個",
    "type": "類型、打字",
    "up": "向上",
    "us": "我們",
    "very": "非常",
    "want": "想要",
    "was": "是、曾經是",
    "way": "方法、道路",
    "we": "我們",
    "well": "好地、健康的",
    "were": "是、曾經是",
    "what": "什麼",
    "when": "何時、當...時",
    "which": "哪一個、那一個",
    "who": "誰",
    "will": "將會、意願",
    "with": "和、帶有",
    "would": "將會、願意",
    "you": "你、你們",
    "your": "你的、你們的",
}


def load_word_data(root: Path) -> list[dict]:
    data_path = root / "app" / "data.js"
    text = data_path.read_text(encoding="utf-8")
    match = re.search(r"window\.WORD_DATA\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not match:
        raise ValueError(f"Cannot parse {data_path}")
    return json.loads(match.group(1))["entries"]


def xhtml(title: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{BOOK_LANG}" xml:lang="{BOOK_LANG}">
  <head>
    <title>{escape(title)}</title>
    <link rel="stylesheet" type="text/css" href="../Styles/book.css" />
  </head>
  <body>
{body}
  </body>
</html>
"""


def meaning_zh(value: str) -> str:
    if not value:
        return ""
    return MEANING_ZH.get(value, value)


def part_note(kind: str, value: str, meaning: str = "") -> str:
    if not value:
        return "無"
    if kind == "prefix":
        return PREFIX_NOTES.get(value) or meaning_zh(meaning) or f"放在字根前，改變「{value}」的方向或語氣"
    if kind == "suffix":
        return SUFFIX_NOTES.get(value) or meaning_zh(meaning) or f"接在字根後，改變詞性或形成新意思"
    if meaning == "core meaning":
        return BASE_WORD_ZH.get(value, "")
    return ROOT_NOTES.get(value, (meaning_zh(meaning) or f"與「{value}」相關的意思", ""))[0]


def morph(entry: dict) -> str:
    return " + ".join(
        [
            entry["prefix"] or "無字首",
            entry["root"] or "無字根",
            entry["suffix"] or "無字尾",
        ]
    )


def group_by_root(entries: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        root = entry.get("root", "")
        if root:
            groups.setdefault(root, []).append(entry)
    for family in groups.values():
        family.sort(key=lambda item: item["rank"])
    return groups


def lesson_roots(entries: list[dict]) -> list[str]:
    groups = group_by_root(entries)
    preferred = [root for root in ROOT_NOTES if len(groups.get(root, [])) >= 2]
    frequent = sorted(
        (
            (root, len(family))
            for root, family in groups.items()
            if root not in preferred and len(root) >= 3 and len(family) >= 4
        ),
        key=lambda item: (-item[1], item[0]),
    )
    return (preferred + [root for root, _ in frequent])[:12]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_static_files(epub_dir: Path, root: Path) -> None:
    write_text(epub_dir / "mimetype", "application/epub+zip")
    write_text(
        epub_dir / "META-INF" / "container.xml",
        """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml" />
  </rootfiles>
</container>
""",
    )
    write_text(
        epub_dir / "OEBPS" / "Styles" / "book.css",
        """body {
  color: #18212f;
  font-family: serif;
  line-height: 1.75;
}
h1, h2, h3 {
  color: #24514a;
  font-family: sans-serif;
  line-height: 1.25;
}
.lead {
  color: #4f5f6f;
}
.parts, .word-table {
  border-collapse: collapse;
  width: 100%;
}
.parts th, .parts td, .word-table th, .word-table td {
  border: 1px solid #d8d0c2;
  padding: 0.45em;
  vertical-align: top;
}
.rank {
  color: #9a6b13;
  font-weight: bold;
}
.family {
  margin: 0 0 1em;
}
""",
    )
    cover_source = root / "app" / "icons" / "icon-512.png"
    (epub_dir / "OEBPS" / "Images").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cover_source, epub_dir / "OEBPS" / "Images" / "cover.png")


def make_cover(epub_dir: Path) -> None:
    body = """    <section class="cover">
      <h1>Word Builder 1200</h1>
      <h2>字根組字彙教學</h2>
      <p class="lead">把常用英文單字拆成看得懂的字首、字根、字尾。</p>
      <img src="../Images/cover.png" alt="Word Builder 1200 cover" />
    </section>
"""
    write_text(epub_dir / "OEBPS" / "Text" / "cover.xhtml", xhtml("Cover", body))


def make_intro(epub_dir: Path, entries: list[dict]) -> None:
    roots = {entry["root"] for entry in entries if entry.get("root")}
    prefixes = {entry["prefix"] for entry in entries if entry.get("prefix")}
    suffixes = {entry["suffix"] for entry in entries if entry.get("suffix")}
    body = f"""    <section>
      <h1>使用這本書</h1>
      <p class="lead">這本 EPUB 由 Word Builder 1200 字根組字彙教學內容產生，適合匯入 Google Play Books 或其他 EPUB 閱讀器。</p>
      <p>全書收錄 {len(entries)} 個常用英文單字，整理出 {len(roots)} 個字根、{len(prefixes)} 個字首、{len(suffixes)} 個字尾。拆解以教學用途為主，目標是幫助讀者建立組字感，不等同完整字源辭典。</p>
      <h2>閱讀方式</h2>
      <ol>
        <li>先讀「字根課程」，掌握一組核心意思。</li>
        <li>再看「拆解示範」，理解字首、字根、字尾如何合作。</li>
        <li>最後查閱 1200 單字表，把同樣的拆解方式套用到更多字。</li>
      </ol>
    </section>
"""
    write_text(epub_dir / "OEBPS" / "Text" / "intro.xhtml", xhtml("使用這本書", body))


def make_lessons(epub_dir: Path, entries: list[dict]) -> list[tuple[str, str]]:
    groups = group_by_root(entries)
    chapters = []
    for index, root in enumerate(lesson_roots(entries), 1):
        meaning, idea = ROOT_NOTES.get(root, ("核心字根", "從同字根單字觀察共同概念。"))
        rows = []
        for entry in groups[root][:12]:
            rows.append(
                f"""          <tr>
            <td><span class="rank">#{entry["rank"]}</span></td>
            <td>{escape(entry["word"])}</td>
            <td>{escape(morph(entry))}</td>
          </tr>"""
            )
        body = f"""    <section>
      <h1>字根 {escape(root)}</h1>
      <p class="lead">{escape(root)} 表示「{escape(meaning)}」。{escape(idea)}</p>
      <table class="word-table">
        <thead>
          <tr><th>頻率</th><th>單字</th><th>拆解</th></tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </section>
"""
        filename = f"lesson-{index:02d}-{root}.xhtml"
        write_text(epub_dir / "OEBPS" / "Text" / filename, xhtml(f"字根 {root}", body))
        chapters.append((filename, f"字根 {root}"))
    return chapters


def make_breakdown(epub_dir: Path, entries: list[dict]) -> None:
    candidates = [
        entry
        for entry in entries
        if entry.get("root") and entry["word"] != entry["root"] and (entry.get("prefix") or entry.get("suffix"))
    ][:24]
    sections = []
    for entry in candidates:
        sections.append(
            f"""      <section>
        <h2>{escape(entry["word"])}</h2>
        <table class="parts">
          <tbody>
            <tr><th>字首</th><td>{escape(entry["prefix"] or "無")}</td><td>{escape(part_note("prefix", entry["prefix"], entry.get("prefixMeaning", "")))}</td></tr>
            <tr><th>字根</th><td>{escape(entry["root"] or "無")}</td><td>{escape(part_note("root", entry["root"], entry.get("rootMeaning", "")))}</td></tr>
            <tr><th>字尾</th><td>{escape(entry["suffix"] or "無")}</td><td>{escape(part_note("suffix", entry["suffix"], entry.get("suffixMeaning", "")))}</td></tr>
          </tbody>
        </table>
      </section>"""
        )
    body = f"""    <section>
      <h1>字根拆解示範</h1>
      <p class="lead">以下用常見單字示範如何拆成字首、字根、字尾。</p>
{chr(10).join(sections)}
    </section>
"""
    write_text(epub_dir / "OEBPS" / "Text" / "breakdown.xhtml", xhtml("字根拆解示範", body))


def make_word_chapters(epub_dir: Path, entries: list[dict], size: int = 100) -> list[tuple[str, str]]:
    chapters = []
    for start in range(0, len(entries), size):
        chunk = entries[start : start + size]
        number = start // size + 1
        rows = []
        for entry in chunk:
            notes = " / ".join(
                part
                for part in [
                    part_note("prefix", entry["prefix"], entry.get("prefixMeaning", "")) if entry.get("prefix") else "",
                    part_note("root", entry["root"], entry.get("rootMeaning", "")) if entry.get("root") else "",
                    part_note("suffix", entry["suffix"], entry.get("suffixMeaning", "")) if entry.get("suffix") else "",
                ]
                if part
            )
            rows.append(
                f"""          <tr>
            <td><span class="rank">#{entry["rank"]}</span></td>
            <td>{escape(entry["word"])}</td>
            <td>{escape(morph(entry))}</td>
            <td>{escape(notes)}</td>
          </tr>"""
            )
        title = f"單字庫 {chunk[0]['rank']}-{chunk[-1]['rank']}"
        filename = f"words-{number:02d}.xhtml"
        body = f"""    <section>
      <h1>{escape(title)}</h1>
      <table class="word-table">
        <thead>
          <tr><th>頻率</th><th>單字</th><th>拆解</th><th>提示</th></tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </section>
"""
        write_text(epub_dir / "OEBPS" / "Text" / filename, xhtml(title, body))
        chapters.append((filename, title))
    return chapters


def make_nav_files(epub_dir: Path, spine: list[tuple[str, str]]) -> None:
    nav_items = "\n".join(
        f'          <li><a href="Text/{escape(filename)}">{escape(title)}</a></li>'
        for filename, title in spine
    )
    write_text(
        epub_dir / "OEBPS" / "nav.xhtml",
        f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{BOOK_LANG}" xml:lang="{BOOK_LANG}">
  <head>
    <title>目錄</title>
  </head>
  <body>
    <nav epub:type="toc" xmlns:epub="http://www.idpf.org/2007/ops">
      <h1>目錄</h1>
      <ol>
{nav_items}
      </ol>
    </nav>
  </body>
</html>
""",
    )
    nav_points = []
    for index, (filename, title) in enumerate(spine, 1):
        nav_points.append(
            f"""    <navPoint id="navPoint-{index}" playOrder="{index}">
      <navLabel><text>{escape(title)}</text></navLabel>
      <content src="Text/{escape(filename)}" />
    </navPoint>"""
        )
    write_text(
        epub_dir / "OEBPS" / "toc.ncx",
        f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{BOOK_IDENTIFIER}" />
    <meta name="dtb:depth" content="1" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
  <docTitle><text>{escape(BOOK_TITLE)}</text></docTitle>
  <navMap>
{chr(10).join(nav_points)}
  </navMap>
</ncx>
""",
    )


def media_type(path: Path) -> str:
    return {
        ".xhtml": "application/xhtml+xml",
        ".css": "text/css",
        ".png": "image/png",
        ".opf": "application/oebps-package+xml",
        ".ncx": "application/x-dtbncx+xml",
    }[path.suffix]


def make_opf(epub_dir: Path, spine: list[tuple[str, str]]) -> None:
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav" />',
        '<item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml" />',
        '<item id="style" href="Styles/book.css" media-type="text/css" />',
        '<item id="cover-image" href="Images/cover.png" media-type="image/png" properties="cover-image" />',
    ]
    spine_items = []
    for index, (filename, _) in enumerate(spine):
        item_id = f"text-{index:02d}"
        manifest.append(f'<item id="{item_id}" href="Text/{escape(filename)}" media-type="application/xhtml+xml" />')
        spine_items.append(f'<itemref idref="{item_id}" />')
    write_text(
        epub_dir / "OEBPS" / "content.opf",
        f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">{BOOK_IDENTIFIER}</dc:identifier>
    <dc:title>{escape(BOOK_TITLE)}</dc:title>
    <dc:language>{BOOK_LANG}</dc:language>
    <dc:creator>{escape(BOOK_AUTHOR)}</dc:creator>
    <dc:description>用字首、字根、字尾拆解 1200 個常用英文單字的教學電子書。</dc:description>
    <meta property="dcterms:modified">{MODIFIED}</meta>
    <meta name="cover" content="cover-image" />
  </metadata>
  <manifest>
    {chr(10).join(manifest)}
  </manifest>
  <spine toc="toc">
    {chr(10).join(spine_items)}
  </spine>
</package>
""",
    )


def validate_xml(epub_dir: Path) -> None:
    for pattern in ("*.xml", "*.opf", "*.ncx", "*.xhtml"):
        for path in epub_dir.rglob(pattern):
            ElementTree.parse(path)


def package_epub(epub_dir: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    with ZipFile(output_path, "w") as epub_zip:
        epub_zip.write(epub_dir / "mimetype", "mimetype", compress_type=ZIP_STORED)
        for file_path in sorted(epub_dir.rglob("*")):
            if file_path.is_dir() or file_path.name == "mimetype":
                continue
            epub_zip.write(file_path, file_path.relative_to(epub_dir).as_posix(), compress_type=ZIP_DEFLATED)


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    last_error = None
    for _ in range(5):
        try:
            shutil.rmtree(path)
            return
        except PermissionError as error:
            last_error = error
            time.sleep(0.4)
    raise last_error


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_root = root / "dist" / "google-play-books"
    epub_dir = out_root / "epub-source-build"
    output_path = out_root / "word-builder-1200-google-play.epub"
    remove_tree(epub_dir)

    entries = load_word_data(root)
    write_static_files(epub_dir, root)
    make_cover(epub_dir)
    make_intro(epub_dir, entries)
    lesson_chapters = make_lessons(epub_dir, entries)
    make_breakdown(epub_dir, entries)
    word_chapters = make_word_chapters(epub_dir, entries)
    spine = [("cover.xhtml", "封面"), ("intro.xhtml", "使用這本書")]
    spine.extend(lesson_chapters)
    spine.append(("breakdown.xhtml", "字根拆解示範"))
    spine.extend(word_chapters)
    make_nav_files(epub_dir, spine)
    make_opf(epub_dir, spine)
    validate_xml(epub_dir)
    package_epub(epub_dir, output_path)
    print(f"Wrote {output_path}")
    print(f"Chapters: {len(spine)}")


if __name__ == "__main__":
    main()
