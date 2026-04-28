const entries = window.WORD_DATA?.entries ?? [];

const els = {
  wordCount: document.querySelector("#word-count"),
  rootCount: document.querySelector("#root-count"),
  prefixCount: document.querySelector("#prefix-count"),
  suffixCount: document.querySelector("#suffix-count"),
  lessonGrid: document.querySelector("#lesson-grid"),
  prefixSelect: document.querySelector("#prefix-select"),
  rootSelect: document.querySelector("#root-select"),
  rootOptions: document.querySelector("#root-options"),
  suffixSelect: document.querySelector("#suffix-select"),
  constructedWord: document.querySelector("#constructed-word"),
  constructedAnalysis: document.querySelector("#constructed-analysis"),
  matchCount: document.querySelector("#match-count"),
  matches: document.querySelector("#matches"),
  wordList: document.querySelector("#word-list"),
  searchInput: document.querySelector("#search-input"),
  speakCurrent: document.querySelector("#speak-current"),
  clearBtn: document.querySelector("#clear-btn"),
  randomBtn: document.querySelector("#random-btn"),
  heroRandom: document.querySelector("#hero-random"),
  sourceNote: document.querySelector("#source-note"),
  demoWord: document.querySelector("#demo-word"),
  demoSummary: document.querySelector("#demo-summary"),
  demoParts: document.querySelector("#demo-parts"),
  demoFamily: document.querySelector("#demo-family"),
  speakDemo: document.querySelector("#speak-demo"),
  nextDemo: document.querySelector("#next-demo"),
};

const ROOT_NOTES = {
  act: { meaning: "做、行動", idea: "act 是動作的核心，常延伸成行為、互動、反應。" },
  form: { meaning: "形狀、形成", idea: "form 把抽象想法變成形狀，也常用在制度與格式。" },
  port: { meaning: "帶、搬運", idea: "port 讓你看到 transport、support、report 這類移動或承載的概念。" },
  view: { meaning: "看、觀點", idea: "view 連到看見、檢視、觀點，也能延伸到 review。" },
  play: { meaning: "玩、演出", idea: "play 從遊戲延伸到表演、播放與角色運作。" },
  use: { meaning: "使用", idea: "use 可變成 useful、user、reuse，適合觀察字尾改變詞性。" },
  move: { meaning: "移動", idea: "move 連到 remove、movement，能看出字首如何改變方向。" },
  press: { meaning: "壓、推", idea: "press 常出現在 pressure、express、impress 等壓力與表達概念。" },
  light: { meaning: "光、輕", idea: "light 有光亮與輕的雙核心，要靠語境判斷。" },
};

const PREFIX_NOTES = {
  re: "再、回來",
  un: "不、相反",
  pre: "之前",
  dis: "分開、否定",
  in: "在內、不",
  im: "不、進入",
  over: "過度、在上",
  under: "不足、在下",
};

const SUFFIX_NOTES = {
  er: "人或比較級",
  ing: "正在、動名詞",
  ed: "過去、完成",
  ly: "副詞",
  tion: "名詞化",
  ment: "結果或狀態",
  ness: "性質",
  ful: "充滿",
  less: "缺少",
};

const prefixes = collectUnique("prefix");
const roots = collectUnique("root");
const suffixes = collectUnique("suffix");
const wordIndex = new Map(entries.map((entry) => [entry.word, entry]));
let currentDemo = null;

function collectUnique(key) {
  return [...new Set(entries.map((entry) => entry[key]).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b)
  );
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function fillSelect(select, items, placeholder) {
  select.innerHTML = [`<option value="">${placeholder}</option>`]
    .concat(items.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`))
    .join("");
}

function fillDatalist(datalist, items) {
  datalist.innerHTML = items.map((item) => `<option value="${escapeHtml(item)}"></option>`).join("");
}

function composeWord(prefix, root, suffix) {
  let base = `${prefix}${root}`;

  if (suffix) {
    const startsWithVowel = /^[aeiou]/.test(suffix);
    if (base.endsWith("y") && ["ness", "ful", "less", "ly"].includes(suffix)) {
      base = `${base.slice(0, -1)}i`;
    } else if (base.endsWith("e") && startsWithVowel && !["ee", "ye"].some((tail) => base.endsWith(tail))) {
      base = base.slice(0, -1);
    } else if (/^[bcdfghjklmnpqrstvwxyz]$/.test(base.at(-1) || "") && suffix === "er") {
      const vowelConsonant = /[aeiou][bcdfghjklmnpqrstvwxyz]$/;
      if (vowelConsonant.test(base) && base.length <= 4) base += base.at(-1);
    }
  }

  return `${base}${suffix}`;
}

function speak(text) {
  if (window.AndroidTTS && typeof window.AndroidTTS.speak === "function") {
    window.AndroidTTS.speak(text);
    return;
  }
  if (!("speechSynthesis" in window)) {
    alert("這個瀏覽器不支援語音播放。");
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.92;
  window.speechSynthesis.speak(utterance);
}

function describePart(type, value) {
  if (!value) return "";
  if (type === "prefix") return PREFIX_NOTES[value] ? `${value}: ${PREFIX_NOTES[value]}` : `${value}: 字首`;
  if (type === "suffix") return SUFFIX_NOTES[value] ? `${value}: ${SUFFIX_NOTES[value]}` : `${value}: 字尾`;
  return ROOT_NOTES[value] ? `${value}: ${ROOT_NOTES[value].meaning}` : `${value}: 核心字根`;
}

function formatMorph(entry) {
  return [entry.prefix || "無字首", entry.root || "無字根", entry.suffix || "無字尾"].join(" + ");
}

function formatGloss(entry) {
  const parts = [
    describePart("prefix", entry.prefix),
    describePart("root", entry.root),
    describePart("suffix", entry.suffix),
  ].filter(Boolean);
  return parts.length ? parts.join(" / ") : "常用基礎字";
}

function getRootFamily(root, limit = 8) {
  return entries
    .filter((entry) => entry.root === root)
    .sort((a, b) => a.rank - b.rank)
    .slice(0, limit);
}

function getLessonRoots() {
  const preferred = Object.keys(ROOT_NOTES).filter((root) => getRootFamily(root, 3).length >= 2);
  const frequent = roots
    .map((root) => ({ root, count: entries.filter((entry) => entry.root === root).length }))
    .filter((item) => item.count >= 4 && !preferred.includes(item.root))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
    .map((item) => item.root);
  return [...preferred, ...frequent].slice(0, 9);
}

function renderLessons() {
  els.lessonGrid.innerHTML = getLessonRoots()
    .map((root) => {
      const note = ROOT_NOTES[root] ?? { meaning: "核心意思", idea: "從同字根單字觀察共同概念。" };
      const family = getRootFamily(root, 5);
      return `
        <article class="lesson-card">
          <div>
            <p class="eyebrow">root</p>
            <h3>${escapeHtml(root)}</h3>
          </div>
          <p><strong>${escapeHtml(note.meaning)}</strong>。${escapeHtml(note.idea)}</p>
          <div class="tag-row">
            ${family.map((entry) => `<button class="tag" type="button" data-word="${escapeHtml(entry.word)}">${escapeHtml(entry.word)}</button>`).join("")}
          </div>
          <button class="secondary-btn" type="button" data-root="${escapeHtml(root)}">看這組字根</button>
        </article>
      `;
    })
    .join("");
}

function filterMatches(prefix, root, suffix) {
  return entries.filter((entry) => {
    const samePrefix = !prefix || entry.prefix === prefix;
    const sameRoot = !root || entry.root === root;
    const sameSuffix = !suffix || entry.suffix === suffix;
    return samePrefix && sameRoot && sameSuffix;
  });
}

function renderMatches(items, activeWord = "") {
  els.matchCount.textContent = `${items.length} 筆`;
  if (!items.length) {
    els.matches.innerHTML = `<span class="muted">目前沒有完全符合的收錄單字，可以換一個字首或字尾試試。</span>`;
    return;
  }

  els.matches.innerHTML = items
    .slice(0, 64)
    .map(
      (entry) => `
        <button class="chip ${entry.word === activeWord ? "active" : ""}" type="button" data-word="${escapeHtml(entry.word)}">
          ${escapeHtml(entry.word)}
        </button>
      `
    )
    .join("");
}

function renderConstructedWord() {
  const prefix = els.prefixSelect.value;
  const root = els.rootSelect.value.trim().toLowerCase();
  const suffix = els.suffixSelect.value;

  if (!prefix && !root && !suffix) {
    els.constructedWord.textContent = "-";
    els.constructedAnalysis.textContent = "選擇零件後會顯示分析。";
    renderMatches([]);
    return;
  }

  if (!root) {
    els.constructedWord.textContent = `${prefix}${suffix}` || "-";
    els.constructedAnalysis.textContent = "組字需要一個核心字根。";
    renderMatches(filterMatches(prefix, "", suffix));
    return;
  }

  const built = composeWord(prefix, root, suffix);
  const exactMatch = wordIndex.get(built);
  els.constructedWord.textContent = built;
  els.constructedAnalysis.textContent = exactMatch
    ? `已收錄：${built} = ${formatMorph(exactMatch)}`
    : `可作為組字觀察：${[describePart("prefix", prefix), describePart("root", root), describePart("suffix", suffix)].filter(Boolean).join(" / ")}`;

  renderMatches(filterMatches(prefix, root, suffix), exactMatch?.word);
}

function renderWordList() {
  const q = els.searchInput.value.trim().toLowerCase();
  const filtered = entries.filter((entry) => {
    if (!q) return true;
    return [entry.word, entry.prefix, entry.root, entry.suffix].some((value) => value.includes(q));
  });

  els.wordList.innerHTML = filtered
    .slice(0, 180)
    .map(
      (entry) => `
        <article class="word-card">
          <div class="word-top">
            <div>
              <div class="rank">#${entry.rank}</div>
              <h3>${escapeHtml(entry.word)}</h3>
            </div>
            <button class="secondary-btn" type="button" data-speak="${escapeHtml(entry.word)}">發音</button>
          </div>
          <div class="morph-row">
            <span class="morph ${entry.prefix ? "" : "empty"}">P: ${escapeHtml(entry.prefix || "無")}</span>
            <span class="morph root">R: ${escapeHtml(entry.root || "無")}</span>
            <span class="morph ${entry.suffix ? "" : "empty"}">S: ${escapeHtml(entry.suffix || "無")}</span>
          </div>
          <p class="gloss">${escapeHtml(formatGloss(entry))}</p>
        </article>
      `
    )
    .join("");
}

function pickRandom() {
  const candidate = entries.filter((entry) => entry.root && (entry.prefix || entry.suffix));
  const entry = candidate[Math.floor(Math.random() * candidate.length)];
  selectEntry(entry);
  document.querySelector("#builder")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function selectEntry(entry) {
  els.prefixSelect.value = entry.prefix;
  els.rootSelect.value = entry.root;
  els.suffixSelect.value = entry.suffix;
  renderConstructedWord();
}

function buildDemo() {
  const demoPool = entries.filter((entry) => {
    const familySize = entries.filter((item) => item.root === entry.root).length;
    return entry.root && entry.word !== entry.root && (entry.prefix || entry.suffix) && familySize >= 3;
  });
  currentDemo = demoPool[Math.floor(Math.random() * demoPool.length)];
  renderDemo(currentDemo);
}

function renderDemo(entry) {
  const rootNote = ROOT_NOTES[entry.root];
  const family = getRootFamily(entry.root, 10).filter((item) => item.word !== entry.word);
  els.demoWord.textContent = entry.word;
  els.demoSummary.textContent = rootNote
    ? `${entry.root} 表示「${rootNote.meaning}」。${rootNote.idea}`
    : `${entry.word} 可以拆成 ${formatMorph(entry)}，先抓住 ${entry.root} 這個核心字根。`;
  els.demoParts.innerHTML = [
    { label: "字首 Prefix", value: entry.prefix || "無", note: describePart("prefix", entry.prefix) || "沒有字首，直接從字根開始。" },
    { label: "字根 Root", value: entry.root || "無", note: describePart("root", entry.root) },
    { label: "字尾 Suffix", value: entry.suffix || "無", note: describePart("suffix", entry.suffix) || "沒有字尾，詞形維持基本樣子。" },
  ]
    .map(
      (part) => `
        <article class="demo-part">
          <span>${escapeHtml(part.label)}</span>
          <strong>${escapeHtml(part.value)}</strong>
          <p>${escapeHtml(part.note)}</p>
        </article>
      `
    )
    .join("");
  els.demoFamily.innerHTML = family.length
    ? family
        .map((item) => `<button class="chip" type="button" data-word="${escapeHtml(item.word)}">${escapeHtml(item.word)}</button>`)
        .join("")
    : `<span class="muted">這個字根目前沒有更多同族範例。</span>`;
}

function bindEvents() {
  [els.prefixSelect, els.rootSelect, els.suffixSelect].forEach((field) => {
    field.addEventListener("change", renderConstructedWord);
    field.addEventListener("input", renderConstructedWord);
  });

  els.searchInput.addEventListener("input", renderWordList);
  els.speakCurrent.addEventListener("click", () => {
    const text = els.constructedWord.textContent.trim();
    if (text && text !== "-") speak(text);
  });
  els.clearBtn.addEventListener("click", () => {
    els.prefixSelect.value = "";
    els.rootSelect.value = "";
    els.suffixSelect.value = "";
    renderConstructedWord();
  });
  els.randomBtn.addEventListener("click", pickRandom);
  els.heroRandom.addEventListener("click", pickRandom);
  els.nextDemo.addEventListener("click", buildDemo);
  els.speakDemo.addEventListener("click", () => {
    if (currentDemo) speak(currentDemo.word);
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    if (target.dataset.root) {
      els.rootSelect.value = target.dataset.root;
      els.prefixSelect.value = "";
      els.suffixSelect.value = "";
      renderConstructedWord();
      document.querySelector("#builder")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    const word = target.dataset.word || target.dataset.speak;
    if (!word) return;
    const entry = wordIndex.get(word);
    if (entry) selectEntry(entry);
    speak(word);
  });
}

function init() {
  fillSelect(els.prefixSelect, prefixes, "無字首");
  fillDatalist(els.rootOptions, roots);
  fillSelect(els.suffixSelect, suffixes, "無字尾");

  els.wordCount.textContent = entries.length.toString();
  els.rootCount.textContent = roots.length.toString();
  els.prefixCount.textContent = prefixes.length.toString();
  els.suffixCount.textContent = suffixes.length.toString();
  els.sourceNote.textContent = "資料以常用字頻產生，字根拆解偏向教學用途，不等同完整字源辭典。";

  renderLessons();
  renderConstructedWord();
  renderWordList();
  buildDemo();
  bindEvents();
}

init();
