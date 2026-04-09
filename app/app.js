const entries = window.WORD_DATA.entries;

const els = {
  wordCount: document.querySelector("#word-count"),
  prefixCount: document.querySelector("#prefix-count"),
  suffixCount: document.querySelector("#suffix-count"),
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
  sourceNote: document.querySelector("#source-note"),
};

const prefixes = collectUnique("prefix");
const roots = collectUnique("root");
const suffixes = collectUnique("suffix");
const wordIndex = new Map(entries.map((entry) => [entry.word, entry]));

function collectUnique(key) {
  return [...new Set(entries.map((entry) => entry[key]).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b)
  );
}

function fillSelect(select, items, placeholder) {
  const options = [`<option value="">${placeholder}</option>`]
    .concat(items.map((item) => `<option value="${item}">${item}</option>`))
    .join("");
  select.innerHTML = options;
}

function fillDatalist(datalist, items) {
  datalist.innerHTML = items.map((item) => `<option value="${item}"></option>`).join("");
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
      if (vowelConsonant.test(base) && base.length <= 4) {
        base += base.at(-1);
      }
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
    alert("這個瀏覽器不支援語音朗讀。");
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

function renderConstructedWord() {
  const prefix = els.prefixSelect.value;
  const root = els.rootSelect.value.trim().toLowerCase();
  const suffix = els.suffixSelect.value;

  if (!prefix && !root && !suffix) {
    els.constructedWord.textContent = "-";
    els.constructedAnalysis.textContent = "請先選擇字首、字根、字尾。";
    renderMatches([]);
    return;
  }

  if (!root) {
    els.constructedWord.textContent = `${prefix || ""}${suffix || ""}` || "-";
    els.constructedAnalysis.textContent = "選了字首或字尾，但還沒有字根。";
    renderMatches(filterMatches(prefix, "", suffix));
    return;
  }

  const built = composeWord(prefix, root, suffix);
  const exactMatch = wordIndex.get(built);
  els.constructedWord.textContent = built;
  els.constructedAnalysis.textContent = exactMatch
    ? `找到字庫單字：${built}。拆解：${formatMorph(exactMatch)}`
    : "這個組合目前不在 1200 字庫中，但仍可拿來做形態拼字練習。";

  renderMatches(filterMatches(prefix, root, suffix), exactMatch?.word);
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
    els.matches.innerHTML = `<span class="muted">沒有找到完全符合的單字，試著只選字根或移除一個條件。</span>`;
    return;
  }

  els.matches.innerHTML = items
    .slice(0, 48)
    .map(
      (entry) => `
        <button class="chip ${entry.word === activeWord ? "active" : ""}" type="button" data-word="${entry.word}">
          ${entry.word}
        </button>
      `
    )
    .join("");
}

function formatMorph(entry) {
  return [entry.prefix || "∅", entry.root || "∅", entry.suffix || "∅"].join(" + ");
}

function formatGloss(entry) {
  const parts = [];
  if (entry.prefix) parts.push(`字首 ${entry.prefix}: ${entry.prefixMeaning || "prefix"}`);
  if (entry.root) parts.push(`字根 ${entry.root}: ${entry.rootMeaning || "root"}`);
  if (entry.suffix) parts.push(`字尾 ${entry.suffix}: ${entry.suffixMeaning || "suffix"}`);
  return parts.join(" / ");
}

function renderWordList() {
  const q = els.searchInput.value.trim().toLowerCase();
  const filtered = entries.filter((entry) => {
    if (!q) return true;
    return (
      entry.word.includes(q) ||
      entry.prefix.includes(q) ||
      entry.root.includes(q) ||
      entry.suffix.includes(q)
    );
  });

  els.wordList.innerHTML = filtered
    .slice(0, 180)
    .map(
      (entry) => `
        <article class="word-card">
          <div class="word-top">
            <div>
              <div class="rank">#${entry.rank}</div>
              <h3>${entry.word}</h3>
            </div>
            <button class="ghost-btn" type="button" data-speak="${entry.word}">發音</button>
          </div>
          <div class="morph-row">
            <span class="morph ${entry.prefix ? "" : "empty"}">P: ${entry.prefix || "∅"}</span>
            <span class="morph root">R: ${entry.root || "∅"}</span>
            <span class="morph ${entry.suffix ? "" : "empty"}">S: ${entry.suffix || "∅"}</span>
          </div>
          <p class="gloss">${formatGloss(entry)}</p>
        </article>
      `
    )
    .join("");
}

function pickRandom() {
  const candidate = entries.filter((entry) => entry.root && (entry.prefix || entry.suffix));
  const entry = candidate[Math.floor(Math.random() * candidate.length)];
  els.prefixSelect.value = entry.prefix;
  els.rootSelect.value = entry.root;
  els.suffixSelect.value = entry.suffix;
  renderConstructedWord();
}

function bindEvents() {
  [els.prefixSelect, els.rootSelect, els.suffixSelect].forEach((select) => {
    select.addEventListener("change", renderConstructedWord);
    select.addEventListener("input", renderConstructedWord);
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

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const word = target.dataset.word || target.dataset.speak;
    if (!word) return;

    const entry = wordIndex.get(word);
    if (entry) {
      els.prefixSelect.value = entry.prefix;
      els.rootSelect.value = entry.root;
      els.suffixSelect.value = entry.suffix;
      renderConstructedWord();
    }
    speak(word);
  });
}

function init() {
  fillSelect(els.prefixSelect, prefixes, "不選字首");
  fillDatalist(els.rootOptions, roots);
  fillSelect(els.suffixSelect, suffixes, "不選字尾");
  els.rootSelect.value = "";

  els.wordCount.textContent = entries.length.toString();
  els.prefixCount.textContent = prefixes.length.toString();
  els.suffixCount.textContent = suffixes.length.toString();
  els.sourceNote.textContent = `${window.WORD_DATA.source.base} ${window.WORD_DATA.source.note}`;

  renderConstructedWord();
  renderWordList();
  bindEvents();
}

init();
