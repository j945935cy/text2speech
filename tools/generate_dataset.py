import json
from pathlib import Path

from wordfreq import top_n_list


PREFIXES = {
    "anti": "against",
    "auto": "self",
    "co": "together",
    "de": "down, remove",
    "dis": "not, opposite",
    "ex": "out",
    "fore": "before",
    "im": "not",
    "in": "not, into",
    "inter": "between",
    "mis": "wrongly",
    "non": "not",
    "over": "too much, above",
    "post": "after",
    "pre": "before",
    "re": "again",
    "sub": "under",
    "super": "above",
    "trans": "across",
    "un": "not",
    "under": "below",
}

SUFFIXES = {
    "ability": "state of being able",
    "able": "capable of",
    "al": "related to",
    "ation": "process or result",
    "ed": "past",
    "en": "make, become",
    "er": "one who, more",
    "est": "most",
    "ful": "full of",
    "hood": "state of",
    "ible": "capable of",
    "ic": "related to",
    "ing": "ongoing action",
    "ion": "act, process",
    "ish": "somewhat",
    "ist": "person who",
    "ity": "state or quality",
    "ive": "having the nature of",
    "ize": "make",
    "less": "without",
    "ly": "in a ... way",
    "ment": "result, process",
    "ness": "state of",
    "or": "person or thing that",
    "ous": "full of",
    "ship": "state, skill, relation",
    "y": "characterized by",
}

ROOT_HINTS = {
    "act": "do",
    "appear": "show up",
    "build": "construct",
    "care": "care",
    "clear": "clear",
    "color": "color",
    "comfort": "comfort",
    "connect": "join",
    "create": "make",
    "cycle": "circle",
    "develop": "grow",
    "direct": "guide",
    "educate": "teach",
    "equal": "same",
    "fair": "just",
    "form": "shape",
    "friend": "friend",
    "govern": "rule",
    "happy": "happy",
    "harm": "damage",
    "help": "help",
    "hope": "hope",
    "inform": "tell",
    "kind": "kind",
    "logic": "reason",
    "measure": "measure",
    "move": "move",
    "music": "music",
    "nation": "nation",
    "nature": "nature",
    "observe": "watch",
    "operate": "work",
    "paint": "paint",
    "pay": "pay",
    "play": "play",
    "port": "carry",
    "power": "power",
    "predict": "say before",
    "press": "press",
    "protect": "guard",
    "quiet": "quiet",
    "read": "read",
    "relate": "connect",
    "respect": "look back at",
    "safe": "safe",
    "science": "knowledge",
    "select": "choose",
    "speak": "speak",
    "sport": "play",
    "state": "state",
    "struct": "build",
    "teach": "teach",
    "tract": "pull",
    "use": "use",
    "view": "see",
    "visit": "go see",
    "wonder": "wonder",
    "work": "work",
    "write": "write",
}

IRREGULAR = {
    "beautiful": ("", "beauty", "ful"),
    "careful": ("", "care", "ful"),
    "careless": ("", "care", "less"),
    "childhood": ("", "child", "hood"),
    "colorful": ("", "color", "ful"),
    "development": ("", "develop", "ment"),
    "education": ("", "educate", "ion"),
    "friendship": ("", "friend", "ship"),
    "happiness": ("", "happy", "ness"),
    "helpful": ("", "help", "ful"),
    "hopeless": ("", "hope", "less"),
    "impossible": ("im", "possible", ""),
    "incorrect": ("in", "correct", ""),
    "international": ("inter", "nation", "al"),
    "kindness": ("", "kind", "ness"),
    "logical": ("", "logic", "al"),
    "movement": ("", "move", "ment"),
    "musical": ("", "music", "al"),
    "national": ("", "nation", "al"),
    "natural": ("", "nature", "al"),
    "payment": ("", "pay", "ment"),
    "powerful": ("", "power", "ful"),
    "prediction": ("pre", "dict", "ion"),
    "protection": ("", "protect", "ion"),
    "quietly": ("", "quiet", "ly"),
    "readable": ("", "read", "able"),
    "selection": ("", "select", "ion"),
    "speaker": ("", "speak", "er"),
    "statement": ("", "state", "ment"),
    "teacher": ("", "teach", "er"),
    "transport": ("trans", "port", ""),
    "useful": ("", "use", "ful"),
    "visitor": ("", "visit", "or"),
    "wonderful": ("", "wonder", "ful"),
    "worker": ("", "work", "er"),
    "writer": ("", "write", "er"),
}


def get_words():
    words = []
    for word in top_n_list("en", 4000):
        if not word.isalpha():
            continue
        if len(word) < 2:
            continue
        words.append(word.lower())
        if len(words) == 1200:
            break
    return words


def normalize_root(root):
    if root in ROOT_HINTS:
        return root
    if root.endswith("i") and root[:-1] + "y" in ROOT_HINTS:
        return root[:-1] + "y"
    if root.endswith("e") and root[:-1] in ROOT_HINTS:
        return root[:-1]
    if root + "e" in ROOT_HINTS:
        return root + "e"
    if len(root) > 3 and root[-1:] == root[-2:-1]:
        shorter = root[:-1]
        if shorter in ROOT_HINTS:
            return shorter
        if shorter + "e" in ROOT_HINTS:
            return shorter + "e"
    return root


def split_word(word):
    if word in IRREGULAR:
        prefix, root, suffix = IRREGULAR[word]
    else:
        prefix = ""
        suffix = ""
        middle = word

        for candidate in sorted(PREFIXES, key=len, reverse=True):
            if word.startswith(candidate) and len(word) - len(candidate) >= 3:
                prefix = candidate
                middle = word[len(candidate):]
                break

        for candidate in sorted(SUFFIXES, key=len, reverse=True):
            if middle.endswith(candidate) and len(middle) - len(candidate) >= 2:
                suffix = candidate
                middle = middle[: -len(candidate)]
                break

        root = normalize_root(middle)

    root_key = normalize_root(root)
    return {
        "word": word,
        "prefix": prefix,
        "prefixMeaning": PREFIXES.get(prefix, ""),
        "root": root,
        "rootMeaning": ROOT_HINTS.get(root_key, "core meaning"),
        "suffix": suffix,
        "suffixMeaning": SUFFIXES.get(suffix, ""),
    }


def main():
    entries = []
    for rank, word in enumerate(get_words(), start=1):
        item = split_word(word)
        item["rank"] = rank
        entries.append(item)

    data = {
        "source": {
            "base": "Top 1200 English words generated from the local wordfreq package.",
            "note": "Morphology split is rule-based for learning, not a strict etymology dictionary.",
        },
        "entries": entries,
    }

    out = Path(__file__).resolve().parents[1] / "app" / "data.js"
    out.write_text("window.WORD_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
