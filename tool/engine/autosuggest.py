#!/usr/bin/env python3
"""
PIXEL STUDIO v2 - TU GAN CANH THEO NOI DUNG (autosuggest).

100% offline, chi dung luat tu khoa + mau cau trong bang RULES o dau file.
Them / sua tu khoa = chi sua RULES, khong sua logic ben duoi.

API:
    analyze(text) -> dict
    analyze_many(list_text) -> list[dict]

Ket qua analyze:
    {
        "scene": int | None,          # id canh thang (khop scenes.py)
        "name": str | None,           # ten canh
        "reason": str,                # ly do tieng Viet ngan gon
        "chips": [str],               # chip du kien hien tren the cau
        "facts": {...},               # MOI du kien trich duoc tu cau
        "params": {...},              # chi du kien dung cho canh thang
        "match": int,                 # 0..5 (0 khi khong gan)
        "low_match": bool,            # True khi canh nhi >= canh nhat
        "highlights": [               # vi tri ky tu trong cau goc
            {"start": int, "end": int, "cls": str}
        ],
    }
"""

import re

# =====================================================================
# BANG LUAT - NGUON SU THAT DUY NHAT CHO TU KHOA / MAU CAU
# ---------------------------------------------------------------------
# Moi rule:
#   scene       : id canh, khop engine/scenes.py
#   name        : ten canh, khop engine/scenes.py
#   keywords_en : tu / cum tu tieng Anh
#   keywords_vi : tu / cum tu tieng Viet
#   patterns    : [{"regex": str, "weight": int, "label": str}]
#
# Trong so:
#   - tu don trong keywords_*                 -> weight 1 (tu suy ra)
#   - cum nhieu tu trong keywords_* (co " ")  -> weight 2 (tu suy ra)
#   - patterns                                -> weight ghi ro trong bang
#     (mau % va mau vs co weight 2 theo SPEC-V2 muc 2)
# =====================================================================
RULES = [
    {
        "scene": 1,
        "name": "Quả cầu nuốt cảnh",
        "keywords_en": [
            "grew", "growth", "growing", "rise", "rose", "surge",
            "skyrocket", "explode", "exploded", "boom", "doubled",
            "tripled",
        ],
        "keywords_vi": ["tăng trưởng", "phình to", "bùng nổ"],
        "patterns": [
            # So %: "300%", "12.5 %"
            {"regex": r"\d+(?:\.\d+)?\s?%", "weight": 2, "label": "%"},
        ],
    },
    {
        "scene": 2,
        "name": "Cân so sánh A vs B",
        "keywords_en": [
            "or", "better than", "worse than", "which one",
            "compared to",
        ],
        "keywords_vi": ["so sánh", "hay là", "hơn"],
        "patterns": [
            # "vs" / "versus" dung rieng o patterns de co weight 2.
            {"regex": r"\b(?:vs|versus)\b", "weight": 2, "label": "vs"},
        ],
    },
    {
        "scene": 3,
        "name": "Mạng lưới node",
        "keywords_en": [
            "connect", "connects", "connected", "network", "system",
            "link", "links", "integrate", "integrated", "together",
        ],
        "keywords_vi": ["kết nối", "hệ thống", "liên kết"],
        "patterns": [],
    },
    {
        "scene": 4,
        "name": "Dòng thời gian",
        "keywords_en": ["years ago", "history", "decade", "timeline"],
        "keywords_vi": ["năm", "lịch sử", "thập kỷ"],
        "patterns": [
            # So nam 19xx / 20xx
            {"regex": r"\b(?:19|20)\d{2}\b", "weight": 2, "label": "year"},
        ],
    },
    {
        "scene": 5,
        "name": "Rơi & xếp chồng",
        "keywords_en": [
            "reached", "reach", "total", "downloaded", "downloads",
            "download", "users", "dollars", "views",
        ],
        "keywords_vi": ["đạt", "tổng cộng", "lượt tải"],
        "patterns": [
            # So luong lon: "2 million", "500k", "1.5 billion" ...
            {
                "regex": r"\b\d+(?:\.\d+)?\s?(?:million|billion|thousand|k)\b",
                "weight": 2,
                "label": "quantity",
            },
        ],
    },
    {
        "scene": 6,
        "name": "Bản đồ hành trình",
        "keywords_en": ["first", "then", "next", "finally", "how to"],
        "keywords_vi": [
            "đầu tiên", "tiếp theo", "sau đó", "cuối cùng", "bước",
        ],
        "patterns": [
            # "step 1", "step 2" ...
            {"regex": r"\bstep\s*\d+\b", "weight": 2, "label": "step"},
        ],
    },
    {
        "scene": 7,
        "name": "Cỗ máy vận hành",
        "keywords_en": [
            "how it works", "under the hood", "automatically",
            "runs itself", "behind the scenes",
        ],
        "keywords_vi": ["cách nó hoạt động", "tự động", "bên trong"],
        "patterns": [],
    },
    {
        "scene": 8,
        "name": "Người trong cảnh",
        "keywords_en": ["you", "your", "user", "people", "imagine", "feel"],
        "keywords_vi": ["bạn", "người dùng", "tưởng tượng"],
        "patterns": [],
    },
    {
        "scene": 9,
        "name": "Sao băng quét cảnh",
        "keywords_en": ["viral", "skyrocket", "breakout", "meteor",
                        "exploded", "overnight"],
        "keywords_vi": ["bùng nổ", "vụt sáng", "sao băng", "qua một đêm"],
        "patterns": [],
    },
]

# Thu tu uu tien khi bang diem (SPEC-V2 muc 2):
# vs/so sanh -> buoc -> % tang truong -> moc nam -> co che
# -> ket noi -> tich luy -> con nguoi
PRIORITY = [2, 6, 1, 4, 7, 3, 5, 8, 9]

_NAME_BY_SCENE = {rule["scene"]: rule["name"] for rule in RULES}
_PRIORITY_INDEX = {scene: i for i, scene in enumerate(PRIORITY)}

# Du kien nao duoc dua vao params cua tung canh thang.
# (facts van tra day du; params chi loc dung cho canh thang de truyen render)
_PARAMS_KEYS_BY_SCENE = {
    1: ("percent", "span_text"),
    2: ("label_a", "label_b", "winner"),
    3: (),
    4: ("years",),
    5: ("quantity_text", "quantity_value"),
    6: ("stages",),
    7: (),
    8: (),
    9: (),
}

# Tu chi thu tu dung cho dem "stages" va highlight hl-step.
# Day la bo dem du kien (muc 3), khong phai bang luat gan canh.
_STAGE_WORD_RES = [
    r"\bfirst\b", r"\bthen\b", r"\bnext\b", r"\bfinally\b",
    r"đầu tiên", r"tiếp theo", r"sau đó", r"cuối cùng",
]
_STAGE_STEP_RE = r"\bstep\s*(\d+)\b"
_STAGE_BUOC_RE = r"\bbước\s*(\d+)\b"

_FILLER_HEADS = {"the", "a", "an"}


# =====================================================================
# CHAM DIEM THEO RULES
# =====================================================================
def _keyword_weight(keyword):
    """Cum nhieu tu -> 2, tu don -> 1."""
    return 2 if " " in keyword.strip() else 1


def _score_text(text):
    """Tra (scores, matched): diem va manh moi trung theo tung canh."""
    scores = {}
    matched = {}
    for rule in RULES:
        scene = rule["scene"]
        score = 0
        found = []  # (vi tri trong cau, manh moi) de ly do doc theo thu tu cau
        for keyword in rule.get("keywords_en", []) + rule.get("keywords_vi", []):
            pattern = r"\b" + re.escape(keyword) + r"\b"
            m = re.search(pattern, text, flags=re.IGNORECASE)
            if m:
                score += _keyword_weight(keyword)
                found.append((m.start(), m.group(0)))
        for pat in rule.get("patterns", []):
            m = re.search(pat["regex"], text, flags=re.IGNORECASE)
            if m:
                score += int(pat["weight"])
                found.append((m.start(), m.group(0)))
        scores[scene] = score
        matched[scene] = [clue for _, clue in sorted(found)]
    return scores, matched


# =====================================================================
# METADATA CHO BO CHON CANH (nhom + tu khoa tim kiem) — doi va 22/10
# =====================================================================
SCENE_META = {
    1: {"group": "Tăng trưởng",
        "tags": "phinh to tang truong growth bong ball nuot lon len"},
    2: {"group": "So sánh",
        "tags": "can so sanh vs doi dau thang thua wins compare canh tranh"},
    3: {"group": "Công nghệ",
        "tags": "mang luoi node ket noi he thong network connect lien ket"},
    4: {"group": "Thời gian",
        "tags": "dong thoi gian nam moc lich su timeline year history ngay thang"},
    5: {"group": "Tăng trưởng",
        "tags": "roi xep chong tich luy so luong users million stack khoi"},
    6: {"group": "Thời gian",
        "tags": "ban do hanh trinh buoc di duong journey steps first then lo trinh"},
    7: {"group": "Công nghệ",
        "tags": "co may van hanh banh rang tu dong machine works engine he thong chay"},
    8: {"group": "Con người",
        "tags": "nguoi nhan vat cong ty founder person imagine you chu doanh nghiep"},
    9: {"group": "Tăng trưởng",
        "tags": "sao bang quet bung no viral meteor skyrocket breakout vuot troi"},
}


def scene_catalog():
    """Danh muc canh cho UI chon canh: id, ten, nhom, chuoi tu khoa tim kiem."""
    kw_by_scene = {}
    for rule in RULES:
        kw = rule.get("keywords_en", []) + rule.get("keywords_vi", [])
        kw_by_scene.setdefault(rule["scene"], []).extend(kw)
    out = []
    for scene in sorted(_NAME_BY_SCENE):
        meta = SCENE_META.get(scene, {"group": "Khác", "tags": ""})
        tags = " ".join([meta["tags"], _NAME_BY_SCENE[scene]] +
                        kw_by_scene.get(scene, []))
        out.append({"id": scene, "name": _NAME_BY_SCENE[scene],
                    "group": meta["group"], "tags": tags.lower()})
    return out


# =====================================================================
# TRICH DU KIEN (SPEC-V2 muc 3)
# =====================================================================
def _to_number(num_text):
    """'300' -> 300 (int), '12.5' -> 12.5 (float)."""
    value = float(num_text)
    return int(value) if value.is_integer() else value


def _extract_percent(text):
    m = re.search(r"(\d+(?:\.\d+)?)\s?%", text)
    return _to_number(m.group(1)) if m else None


def _extract_span_text(text):
    m = re.search(r"(\d+)\s?(years?|months?|days?)\b", text,
                  flags=re.IGNORECASE)
    if not m:
        return None
    return "%s %s" % (m.group(1), m.group(2).lower())


def _extract_years(text):
    years = [int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", text)]
    return years[:5]


def _word_tokens(segment):
    return list(re.finditer(r"[^\W_]+(?:['\-][^\W_]+)*", segment,
                            flags=re.UNICODE))


def _is_capitalized(token):
    return bool(token) and token[0].isupper()


def _extract_label_a(left_text):
    """Cum <=3 tu ngay truoc vs/versus, uu tien cum viet hoa."""
    if not left_text.strip():
        return None
    # Chi xet menh de gan nhat (sau dau ngat cau cuoi cung).
    segment = re.split(r"[.!?;\n]", left_text)[-1]
    tokens = [m.group(0) for m in _word_tokens(segment)]
    if not tokens:
        return None
    # Uu tien: chuoi tu viet hoa lien tiep GAN vs NHAT (chay cuoi cung),
    # toi da 3 tu. Dung chay cuoi thay vi bat buoc o cuoi cum de cau nhu
    # "ChatGPT wins vs Claude" van bat dung nhan "ChatGPT" (wins la dong
    # tu manh moi, khong phai mot phan cua nhan).
    runs = []
    current = []
    for token in tokens:
        if _is_capitalized(token):
            current.append(token)
        else:
            if current:
                runs.append(current)
                current = []
    if current:
        runs.append(current)
    if runs:
        return " ".join(runs[-1][-3:])
    # Fallback: 3 tu cuoi, bo tu dem the/a/an o dau.
    tail = tokens[-3:]
    while tail and tail[0].lower() in _FILLER_HEADS:
        tail = tail[1:]
    return " ".join(tail) if tail else None


def _extract_label_b(right_text):
    """Cum <=3 tu ngay sau vs/versus, dung o dau : . ? ,"""
    if not right_text.strip():
        return None
    cut = len(right_text)
    for delim in ":.?,":
        idx = right_text.find(delim)
        if idx != -1:
            cut = min(cut, idx)
    segment = right_text[:cut]
    tokens = [m.group(0) for m in _word_tokens(segment)]
    if not tokens:
        return None
    if _is_capitalized(tokens[0]):
        capitalized = []
        for token in tokens:
            if _is_capitalized(token) and len(capitalized) < 3:
                capitalized.append(token)
            else:
                break
        if capitalized:
            return " ".join(capitalized)
    head = tokens[:3]
    while head and head[0].lower() in _FILLER_HEADS:
        head = head[1:]
    return " ".join(head) if head else None


def _extract_vs(text):
    """Tra (label_a, label_b, winner) hoac None neu khong co vs/versus."""
    m = re.search(r"\b(?:vs|versus)\b", text, flags=re.IGNORECASE)
    if not m:
        return None
    label_a = _extract_label_a(text[:m.start()])
    label_b = _extract_label_b(text[m.end():])
    winner = _detect_winner(text, label_a, label_b)
    return label_a, label_b, winner


def _detect_winner(text, label_a, label_b):
    """'a' / 'b' / None tu mau '<ten> wins' hoac '<ten> (is) better'."""
    if not label_a and not label_b:
        return None
    lower = text.lower()
    sides = (("a", label_a), ("b", label_b))
    for side, label in sides:
        if not label:
            continue
        lab = re.escape(label.lower())
        if re.search(r"\b" + lab + r"\s+wins\b", lower):
            return side
        if re.search(r"\b" + lab + r"\s+(?:is\s+)?better\b", lower):
            return side
    # "better than <ten>" -> ben con lai la ben thang.
    for side, label in sides:
        if not label:
            continue
        lab = re.escape(label.lower())
        if re.search(r"\bbetter\s+than\s+" + lab + r"\b", lower):
            return "b" if side == "a" else "a"
    return None


_QUANTITY_RE = (
    r"(\d+(?:\.\d+)?)\s?(million|billion|thousand|k)\b"
    r"(?:\s+(users|downloads|dollars|people|views|subscribers|customers))?"
)
_QUANTITY_MULTIPLIER = {
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "thousand": 1_000,
    "k": 1_000,
}


def _extract_quantity(text):
    """Tra (quantity_text, quantity_value) hoac (None, None)."""
    m = re.search(_QUANTITY_RE, text, flags=re.IGNORECASE)
    if not m:
        return None, None
    num_text, scale = m.group(1), m.group(2).lower()
    quantity_text = "%s %s" % (num_text, scale)
    value = float(num_text) * _QUANTITY_MULTIPLIER[scale]
    quantity_value = int(value) if float(value).is_integer() else value
    return quantity_text, quantity_value


def _extract_stages(text):
    """Dem tu chi thu tu phan biet; chi tra stages khi dem >= 2, kep 2..5."""
    count = 0
    for pattern in _STAGE_WORD_RES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            count += 1
    step_numbers = set(re.findall(_STAGE_STEP_RE, text,
                                  flags=re.IGNORECASE))
    count += len(step_numbers)
    buoc_numbers = set(re.findall(_STAGE_BUOC_RE, text,
                                   flags=re.IGNORECASE))
    if buoc_numbers:
        count += len(buoc_numbers)
    elif re.search(r"\bbước\b", text, flags=re.IGNORECASE):
        # "buoc" khong kem so: tinh la 1 chang (chi khi chua dem o tren).
        # Luu y: tu "buoc" trong keywords cua canh 6 khong tu dong tao
        # stages - can them it nhat 1 dau thu tu nua de tong >= 2.
        count += 0  # giu nguyen: 1 dau don le chua du tao stages
    if count < 2:
        return None
    return max(2, min(5, count))


def _extract_facts(text):
    facts = {}
    percent = _extract_percent(text)
    if percent is not None:
        facts["percent"] = percent
    span_text = _extract_span_text(text)
    if span_text is not None:
        facts["span_text"] = span_text
    years = _extract_years(text)
    if years:
        facts["years"] = years
    vs = _extract_vs(text)
    if vs is not None:
        label_a, label_b, winner = vs
        if label_a is not None:
            facts["label_a"] = label_a
        if label_b is not None:
            facts["label_b"] = label_b
        facts["winner"] = winner
    quantity_text, quantity_value = _extract_quantity(text)
    if quantity_text is not None:
        facts["quantity_text"] = quantity_text
        facts["quantity_value"] = quantity_value
    stages = _extract_stages(text)
    if stages is not None:
        facts["stages"] = stages
    return facts


# =====================================================================
# HIGHLIGHTS (vi tri ky tu trong cau goc, cho giao dien to mau)
# =====================================================================
def _build_highlights(text):
    highlights = []

    def add(pattern, cls):
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = m.span()
            # Bo qua neu da trung voi highlight truoc.
            if any(start < h["end"] and end > h["start"]
                   for h in highlights):
                continue
            highlights.append({"start": start, "end": end, "cls": cls})

    add(r"\d+(?:\.\d+)?\s?%", "hl-pct")
    add(r"\b(?:vs|versus)\b", "hl-vs")
    for pattern in _STAGE_WORD_RES:
        add(pattern, "hl-step")
    add(_STAGE_STEP_RE.replace(r"(\d+)", r"\d+"), "hl-step")
    add(_STAGE_BUOC_RE.replace(r"(\d+)", r"\d+"), "hl-step")
    add(r"\b(?:19|20)\d{2}\b", "hl-year")
    add(_QUANTITY_RE, "hl-num")
    highlights.sort(key=lambda h: (h["start"], h["end"]))
    return highlights


# =====================================================================
# CHIPS + REASON
# =====================================================================
def _build_chips(scene, facts):
    if scene == 1:
        chips = []
        if "percent" in facts:
            chips.append("%s%%" % (facts["percent"],))
        if "span_text" in facts:
            chips.append(facts["span_text"])
        return chips
    if scene == 2:
        chips = []
        if facts.get("label_a"):
            chips.append("A: %s" % (facts["label_a"],))
        if facts.get("label_b"):
            chips.append("B: %s" % (facts["label_b"],))
        return chips
    if scene == 4:
        return [str(y) for y in facts.get("years", [])]
    if scene == 5:
        return [facts["quantity_text"]] if "quantity_text" in facts else []
    if scene == 6:
        return ["%d chặng" % (facts["stages"],)] if "stages" in facts else []
    return []


def _build_reason(scene, clues, facts):
    clue_text = ", ".join("'%s'" % (c,) for c in clues[:3])
    if scene == 1:
        if "percent" in facts:
            word_clues = [c for c in clues[:3] if "%" not in c]
            word_text = ", ".join("'%s'" % (c,) for c in word_clues)
            head = ("có %s + số %s%%" % (word_text, facts["percent"])
                    if word_text else "có số %s%%" % (facts["percent"],))
            return "%s → mức phình của cầu lấy theo %s%%" % (
                head, facts["percent"])
        return "có %s → gợi ý tăng trưởng" % (clue_text,)
    if scene == 2:
        if facts.get("label_a") and facts.get("label_b"):
            return "có 'vs' giữa %s và %s → cân so sánh A vs B" % (
                facts["label_a"], facts["label_b"])
        return "có %s → gợi ý so sánh A vs B" % (clue_text,)
    if scene == 3:
        return "có %s → mạng lưới kết nối" % (clue_text,)
    if scene == 4:
        if facts.get("years"):
            return "có năm %s → dòng thời gian" % (facts["years"][0],)
        return "có %s → dòng thời gian" % (clue_text,)
    if scene == 5:
        if "quantity_text" in facts:
            word_clues = [c for c in clues[:4]
                          if c != facts["quantity_text"]]
            word_text = ", ".join("'%s'" % (c,) for c in word_clues)
            head = ("có %s + số lượng %s" % (word_text, facts["quantity_text"])
                    if word_text else
                    "có số lượng %s" % (facts["quantity_text"],))
            return "%s → rơi & xếp chồng theo số lượng" % (head,)
        return "có %s → gợi ý tích lũy số lượng" % (clue_text,)
    if scene == 6:
        if "stages" in facts:
            return "có %s → bản đồ hành trình %d chặng" % (
                clue_text, facts["stages"])
        return "có %s → gợi ý bản đồ hành trình" % (clue_text,)
    if scene == 7:
        return "có %s → cỗ máy vận hành" % (clue_text,)
    if scene == 8:
        return "có %s → người trong cảnh" % (clue_text,)
    return "không trúng luật nào → chưa gán, cần chọn tay"


# =====================================================================
# HAM CHINH
# =====================================================================
def analyze(text):
    """Phan tich 1 cau, tra dict theo SPEC-V2 (xem docstring dau file)."""
    if not text or not str(text).strip():
        return {
            "scene": None,
            "name": None,
            "reason": "câu trống → chưa gán, cần chọn tay",
            "chips": [],
            "facts": {},
            "params": {},
            "match": 0,
            "low_match": False,
            "highlights": [],
            "top3": [],
        }
    text = str(text)
    scores, matched = _score_text(text)
    facts = _extract_facts(text)
    highlights = _build_highlights(text)

    # Canh thang: diem cao nhat; bang diem thi theo PRIORITY.
    ranked = sorted(
        (s for s in scores if scores[s] > 0),
        key=lambda s: (-scores[s], _PRIORITY_INDEX[s]),
    )
    if not ranked:
        return {
            "scene": None,
            "name": None,
            "reason": "không trúng luật nào → chưa gán, cần chọn tay",
            "chips": [],
            "facts": facts,
            "params": {},
            "match": 0,
            "low_match": False,
            "highlights": highlights,
            "top3": [],
        }

    scene = ranked[0]
    top_score = scores[scene]
    second_score = scores[ranked[1]] if len(ranked) > 1 else 0
    low_match = second_score >= top_score

    params = {
        key: facts[key]
        for key in _PARAMS_KEYS_BY_SCENE.get(scene, ())
        if key in facts
    }
    # winner=None van la du kien hop le cua canh 2 (chua ro ben thang).
    if scene == 2 and "winner" in facts and "winner" not in params:
        params["winner"] = facts["winner"]

    top3 = [{"scene": sc, "name": _NAME_BY_SCENE[sc],
             "match": min(5, max(1, scores[sc]))} for sc in ranked[:3]]

    match = min(5, top_score + (1 if params else 0))
    match = max(1, match)

    return {
        "scene": scene,
        "name": _NAME_BY_SCENE[scene],
        "reason": _build_reason(scene, matched[scene], facts),
        "chips": _build_chips(scene, facts),
        "facts": facts,
        "params": params,
        "match": match,
        "low_match": low_match,
        "highlights": highlights,
        "top3": top3,
    }


def analyze_many(list_text):
    """Phan tich nhieu cau, tra list ket qua cung thu tu dau vao."""
    return [analyze(text) for text in list_text]


# =====================================================================
# TU KIEM TRA: python3 autosuggest.py
# =====================================================================
if __name__ == "__main__":
    samples = [
        "It grew 300% in just 3 years.",
        "ChatGPT vs Claude: which one wins?",
        "First, connect the tools. Then the system runs itself.",
    ]
    for sample in samples:
        print("=" * 72)
        print("TEXT:", sample)
        result = analyze(sample)
        for key in ("scene", "name", "reason", "chips", "facts", "params",
                    "match", "low_match", "highlights"):
            print("  %-10s %r" % (key + ":", result[key]))
