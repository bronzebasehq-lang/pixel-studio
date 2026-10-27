#!/usr/bin/env python3
"""TEST01 SCENES - dang ky 11 mau canh goi "test01" thanh MAU CANH THAT.

Cung pattern voi style2_scenes (V2.3): moi template co SPEC tham so,
UI tu sinh form sua tham so; params luu theo cau va di kem payload render
(id canh trong UI: "t1:<key>", truong tpack="t1" o payload).

Khac style2: mau test01 TU mang chu cua minh (tham so hoa), khong dung
lop chu chay/phu de chung. draw_template tra RGBA 1280x720 (khung goc
cua goi); pipeline chinh phong NEAREST len khung xuat.

Kem theo BO QUET NHIP (spec muc 1): events_for() liet ke cac bien co
hinh anh trong 1 canh; scan_pacing() tim doan > max_gap giay khong co
bien co nao tren toan truc thoi gian video -> canh bao.
"""
import math

import test01_templates as t1

W, H = t1.W, t1.H


# ------------------------------------------------------------------ helpers
def _s(v, default=""):
    if v is None:
        return default
    return str(v)


def _num(v, default=0.0):
    try:
        return float(str(v).replace(",", "").replace(" ", ""))
    except (TypeError, ValueError):
        return default


def _merged(spec_params, params):
    out = {p["key"]: p["def"] for p in spec_params}
    if isinstance(params, dict):
        for k, v in params.items():
            if k in out:
                out[k] = _s(v, out[k])
    return out


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ------------------------------------------------------------------ timing
# Moi ham _prep_<key>(p, dur) tra dict khoa tinh toan (bat dau bang "_")
# dung chung cho builder (ve) va events_for (quet nhip/SFX) -> 1 nguon that.

def _prep_stamp_big(p, dur):
    return {"_stamp_at": min(1.1, max(0.5, dur * 0.38))}


def _prep_type_window(p, dur):
    lines = [x for x in p["lines"].split("|")]
    raw = [_clamp(len(x) * 0.028, 0.35, 1.1) for x in lines]
    budget = max(0.6, dur - 1.15)
    tot = sum(raw)
    if tot > budget:
        raw = [r * budget / tot for r in raw]
    starts, acc = [], 0.5
    for r in raw:
        starts.append((acc, acc + r))
        acc += r
    return {"_line_starts": starts}


def _prep_stage_text(p, dur):
    return {"_glitch_at": 0.80}


def _prep_item_rows(p, dur):
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    n = max(1, len(items))
    stagger = _clamp((dur - 1.0) / n, 0.22, 0.5)
    return {"_starts": [0.45 + i * stagger for i in range(n)]}


def _prep_big_counter(p, dur):
    return {"_target": _num(p["value"], 1298),
            "_count_dur": min(2.2, max(0.5, dur * 0.55))}


def _prep_cell_grid(p, dur):
    total = max(1, int(_num(p["count"], 20)))
    cols = max(1, int(_num(p["cols"], 5)))
    rows = int(math.ceil(total / float(cols)))
    step = _clamp((dur - 1.6) / total, 0.04, 0.12)
    return {"_total": total, "_cols": cols, "_rows": rows, "_step": step}


def _prep_progress_bar(p, dur):
    fill = min(1.6, max(0.4, dur * 0.35))
    return {"_pct": _clamp(_num(p["pct"], 75), 0, 100),
            "_fill_dur": fill, "_t_lines": 0.25 + fill + 0.15}


def _prep_follow_end(p, dur):
    return {"_click_at": min(2.4, max(1.5, dur * 0.55))}


def _prep_combo_chain(p, dur):
    sx = int(_num(p["start_x"], 2))
    mx = int(_num(p["max_x"], 5))
    if mx < sx:
        mx = sx
    step = _clamp((dur - 1.4) / max(1, mx - sx), 0.3, 0.55) if mx > sx else 0.5
    return {"_start_x": sx, "_max_x": mx, "_step": step}


_PREP = {
    "stamp_big": _prep_stamp_big,
    "type_window": _prep_type_window,
    "stage_text": _prep_stage_text,
    "item_rows": _prep_item_rows,
    "big_counter": _prep_big_counter,
    "cell_grid": _prep_cell_grid,
    "progress_bar": _prep_progress_bar,
    "follow_end": _prep_follow_end,
    "combo_chain": _prep_combo_chain,
}


def _full_params(key, params, dur):
    info = TEMPLATES[key]
    p = _merged(info["params"], params)
    prep = _PREP.get(key)
    if prep:
        p.update(prep(p, dur))
    return p


# ------------------------------------------------------------------ builders
def _builder(key, draw_fn):
    def build(p, ctx):
        def fn(t, dur):
            info = TEMPLATES[key]
            full = _merged(info["params"], p)
            prep = _PREP.get(key)
            if prep:
                full.update(prep(full, dur))
            return draw_fn(t, dur, full)
        return fn
    return build


# ------------------------------------------------------------------ registry
def _spec(key, label, typ, default):
    return {"key": key, "label": label, "type": typ, "def": default}


TEMPLATES = {
    "hook_cards": {
        "name": "hook_cards — Thẻ hook xòe quạt",
        "desc": "5 thẻ xòe quạt từ dưới lên + câu hỏi lớn ở trên",
        "tags": "hook cards the xoe quat cau hoi prompt mo dau fan",
        "params": [
            _spec("kicker", "Dòng nhỏ trên cùng", "text", "Bạn hay hỏi:"),
            _spec("pre", "Câu hỏi — phần chữ trắng", "text", "dùng "),
            _spec("accent", "Câu hỏi — phần chữ nhấn", "text", "PROMPT GÌ?"),
            _spec("accent_col", "Màu chữ nhấn (red/teal/yellow/cream)",
                  "text", "red"),
            _spec("sub", "Dòng dưới câu hỏi", "text",
                  "để AI dựng được video THẾ NÀY?"),
        ],
        "build": _builder("hook_cards", t1.hook_cards),
    },
    "stamp_big": {
        "name": "stamp_big — Đóng dấu kết luận",
        "desc": "Chữ lớn + tem đỏ đóng xuống, rung màn hình",
        "tags": "stamp dong dau tem ket luan sai stamp shake",
        "params": [
            _spec("big", "Chữ lớn", "text", "HỎI SAI RỒI."),
            _spec("big_col", "Màu chữ lớn (cream/red/teal/yellow)", "text",
                  "cream"),
            _spec("stamp", "Chữ trong tem", "text", "SAI!"),
            _spec("sub", "Dòng phụ dưới (để trống = không)", "text",
                  "câu hỏi đúng mới ra video đúng"),
        ],
        "build": _builder("stamp_big", t1.stamp_big),
    },
    "type_window": {
        "name": "type_window — Cửa sổ gõ chữ",
        "desc": "Khung file/chat, chữ gõ từng dòng + con trỏ nhấp nháy",
        "tags": "type window cua so go chu skill md chat file typing cursor",
        "params": [
            _spec("title", "Tên cửa sổ", "text", "SKILL.md"),
            _spec("head_small", "Tiêu đề trái — dòng nhỏ", "text",
                  "được viết thành"),
            _spec("head_big", "Tiêu đề trái — dòng lớn", "text", "bộ SKILL."),
            _spec("head_col", "Màu dòng lớn (teal/red/yellow/cream)",
                  "text", "teal"),
            _spec("lines", "Các dòng gõ (ngăn cách bằng |)", "text",
                  "Đạo diễn, KHÔNG phải máy nhắc chữ."
                  "|1. Đọc TASTE.md TRƯỚC."
                  "|2. Khóa mốc trong beats.json."
                  "|3. Chữ chạy theo ÂM TIẾT."
                  "|4. Xem trước. Duyệt. Rồi xuất."
                  "|Không qua duyệt -> KHÔNG xuất."),
            _spec("colors", "Màu từng dòng (cách nhau dấu phẩy)", "text",
                  "cream,teal,teal,yellow,cream,red"),
        ],
        "build": _builder("type_window", t1.type_window),
    },
    "stage_text": {
        "name": "stage_text — Sân khấu chữ",
        "desc": "Set phòng gỗ + đèn rọi + hạt pixel + câu chữ lớn, glitch ở từ khóa",
        "tags": "stage text san khau chu den roi phong go glitch rgb",
        "params": [
            _spec("small", "Dòng nhỏ", "text", "Khác biệt nằm ở"),
            _spec("big1", "Dòng lớn 1 (trắng)", "text", "NGƯỜI"),
            _spec("big2", "Dòng lớn 2 (nhấn, có glitch)", "text", "ĐẠO DIỄN."),
            _spec("big2_col", "Màu dòng lớn 2 (red/teal/yellow)", "text",
                  "red"),
            _spec("sub", "Dòng phụ pixel dưới (để trống = không)", "text",
                  "cùng một AI - khác người đạo diễn"),
        ],
        "build": _builder("stage_text", t1.stage_text),
    },
    "ab_compare": {
        "name": "ab_compare — So sánh A/B",
        "desc": "Chia đôi khung: bên xám rỗng vs bên đầy đủ + huy hiệu VS",
        "tags": "ab compare so sanh a b vs trai phai before after",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "CÙNG MỘT AI"),
            _spec("label_a", "Nhãn bên trái (xám)", "text",
                  "KHÔNG AI ĐẠO DIỄN"),
            _spec("label_b", "Nhãn bên phải (đầy đủ)", "text",
                  "CÓ NGƯỜI ĐẠO DIỄN"),
        ],
        "build": _builder("ab_compare", t1.ab_compare),
    },
    "item_rows": {
        "name": "item_rows — Hàng mục hiện dần",
        "desc": "Các mục pop lần lượt theo nhịp, mỗi mục 1 biểu tượng + số thứ tự",
        "tags": "item rows hang muc hien dan danh sach ekip list stagger pop",
        "params": [
            _spec("title", "Tiêu đề", "text", "Ê-KÍP ĐẠO DIỄN GỒM:"),
            _spec("items", "Các mục (cách nhau dấu phẩy, tối đa 6)", "text",
                  "Kịch bản,Phân cảnh,Chuyển động,Phụ đề,Lồng tiếng,Âm thanh"),
        ],
        "build": _builder("item_rows", t1.item_rows),
    },
    "big_counter": {
        "name": "big_counter — Bộ đếm số lớn",
        "desc": "Số pixel chạy tăng tới đích + sóng âm nhảy + nhãn đỏ",
        "tags": "big counter bo dem so lon chay tang hieu ung am thanh count",
        "params": [
            _spec("value", "Số đích", "number", "1298"),
            _spec("label", "Nhãn dưới số", "text", "HIỆU ỨNG ÂM THANH"),
            _spec("label_col", "Màu nhãn (red/teal/yellow/cream)", "text",
                  "red"),
            _spec("sub", "Dòng phụ pixel dưới (để trống = không)", "text", ""),
        ],
        "build": _builder("big_counter", t1.big_counter),
    },
    "cell_grid": {
        "name": "cell_grid — Lưới ô đánh số",
        "desc": "Lưới ô vuông đánh số hiện dần (vd 20 ô phong cách)",
        "tags": "cell grid luoi o danh so phong cach styles cells",
        "params": [
            _spec("title", "Tiêu đề", "text", "PHONG CÁCH DỰNG SẴN"),
            _spec("count", "Tổng số ô", "number", "20"),
            _spec("cols", "Số cột", "number", "5"),
            _spec("caption", "Chú thích dưới (để trống = không)", "text",
                  "20 PHONG CÁCH dựng sẵn - chọn là chạy"),
        ],
        "build": _builder("cell_grid", t1.cell_grid),
    },
    "progress_bar": {
        "name": "progress_bar — Thanh tiến trình / HP",
        "desc": "Thanh % chạy rồi lật câu hỏi phần còn lại; biến thể HP kiểu game",
        "tags": "progress bar thanh tien trinh phan tram hp mana game 75 25",
        "params": [
            _spec("variant", "Biến thể (percent / hp)", "text", "percent"),
            _spec("pct", "Phần trăm đích", "number", "75"),
            _spec("line1", "Dòng 1", "text", "Skill lo 75%..."),
            _spec("question", "Câu hỏi lật (vàng)", "text", "25% còn lại?"),
            _spec("question_col", "Màu câu hỏi (yellow/red/teal)", "text",
                  "yellow"),
            _spec("answer", "Dòng trả lời", "text",
                  "Là BẠN. Ý TƯỞNG CỦA BẠN. GU CỦA BẠN."),
        ],
        "build": _builder("progress_bar", t1.progress_bar),
    },
    "follow_end": {
        "name": "follow_end — Màn hình cuối THEO DÕI",
        "desc": "Chữ chốt + nút THEO DÕI giả, con trỏ bay vào bấm đổi trạng thái",
        "tags": "follow end man hinh cuoi theo doi nut bam con tro subscribe cta",
        "params": [
            _spec("main", "Dòng chốt 1", "text", "Phần khó đã có người làm."),
            _spec("sub", "Dòng chốt 2", "text",
                  "Việc của bạn chỉ là BẮT ĐẦU."),
            _spec("accent", "Từ nhấn trong dòng 2", "text", "BẮT ĐẦU."),
            _spec("accent_col", "Màu từ nhấn (red/teal/yellow)", "text",
                  "red"),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI"),
            _spec("done_text", "Chữ nút sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _spec("side_text", "Chữ cạnh nút (để trống = không)", "text",
                  "để xem PHẦN 2"),
        ],
        "build": _builder("follow_end", t1.follow_end),
    },
    "combo_chain": {
        "name": "combo_chain — Combo lên cấp",
        "desc": "COMBO ×2 ×3 ×4... + thanh năng lượng chia đoạn kiểu game",
        "tags": "combo chain combo len cap nang luong game x2 x3 energy",
        "params": [
            _spec("label", "Nhãn trên", "text", "COMBO"),
            _spec("start_x", "Combo bắt đầu (×)", "number", "2"),
            _spec("max_x", "Combo tối đa (×)", "number", "5"),
            _spec("plus_text", "Chữ cộng nhịp", "text", "+1 Ý MỚI"),
            _spec("caption", "Chú thích dưới (để trống = không)", "text",
                  "mỗi ý mới = +1 combo - nhịp leo thang tới cuối video"),
        ],
        "build": _builder("combo_chain", t1.combo_chain),
    },
}


def template_catalog():
    """Danh muc JSON-safe cho UI: id, ten, nhom tu khoa + SPEC tham so."""
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


# ------------------------------------------------------------------ ve frame
def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    """Ve 1 frame test01 tai thoi diem tm (giay) cua shot dai dur (giay).

    Tra RGBA 1280x720. typed/popup nhan cho tuong thich chu ky cua
    render.py nhung mau test01 TU mang chu (tham so) nen khong ap dung.
    Dau moi shot co hieu ung vo pixel giai dan trong 0.14s dau (muc 7).
    """
    info = TEMPLATES[name]
    p = _merged(info["params"], params)
    fn = info["build"](p, {"text": text})
    img = fn(tm, dur)
    if tm < 0.14:
        block = int(13 * (1.0 - tm / 0.14)) + 1
        if block > 1:
            img = t1.fx_pixelate(img, block)
    return img


# ------------------------------------------------------------------ quet nhip
def events_for(name, params, dur):
    """Liet ke bien co hinh anh trong 1 canh: [(offset_giay, loai), ...].

    Loai: pop / stamp / type / tick / glitch / click — dung cho bo quet
    nhip va cho lop SFX cua video mau (tieng khop bien co).
    """
    p = _full_params(name, params, dur)
    ev = []
    if name == "hook_cards":
        ev = [(0.10, "pop"), (0.30, "pop"), (0.55, "pop")]
        ev += [(0.50 + i * 0.11, "pop") for i in range(5)]
    elif name == "stamp_big":
        ev = [(0.12, "pop"), (p["_stamp_at"], "stamp"),
              (p["_stamp_at"] + 0.28, "pop")]
    elif name == "type_window":
        ev = [(0.10, "pop"), (0.30, "pop")]
        ev += [(s, "type") for (s, _e) in p["_line_starts"]]
    elif name == "stage_text":
        ev = [(0.15, "pop"), (0.45, "pop"), (0.80, "pop"),
              (0.80, "glitch"), (1.15, "pop")]
    elif name == "ab_compare":
        ev = [(0.10, "pop"), (0.35, "pop"), (0.75, "pop"), (1.00, "pop"),
              (1.10, "pop"), (1.25, "pop")]
    elif name == "item_rows":
        ev = [(0.10, "pop")] + [(s, "pop") for s in p["_starts"]]
    elif name == "big_counter":
        cd = p["_count_dur"]
        ev = [(0.20 + cd * k / 10.0, "tick") for k in range(11)]
        ev.append((0.20 + cd * 0.55, "pop"))
    elif name == "cell_grid":
        total, step = p["_total"], p["_step"]
        ev = [(0.10, "pop")]
        ev += [(0.40 + i * step, "pop") for i in range(0, total, 5)]
        ev.append((0.40 + total * step + 0.15, "pop"))
    elif name == "progress_bar":
        fill = p["_fill_dur"]
        ev = [(0.25 + fill * k / 4.0, "tick") for k in range(5)]
        tl = p["_t_lines"]
        ev += [(tl, "pop"), (tl + 0.55, "pop"), (tl + 1.10, "pop")]
    elif name == "follow_end":
        ev = [(0.15, "pop"), (0.60, "pop"), (1.00, "pop"),
              (p["_click_at"], "click")]
    elif name == "combo_chain":
        sx, mx, step = p["_start_x"], p["_max_x"], p["_step"]
        for i, n in enumerate(range(sx, mx + 1)):
            at = 0.35 + i * step
            ev += [(at, "pop"), (at, "tick")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)


def scan_pacing(shots, max_gap=5.0):
    """Quet toan truc thoi gian: tim doan > max_gap giay khong bien co.

    shots = [{"name":..., "dur":..., "events":[(offset, kind), ...]}]
    Tra ve list canh bao dang chuoi (rong = nhip dat chuan spec).
    """
    warnings = []
    points = [0.0]
    starts = []
    acc = 0.0
    for i, sh in enumerate(shots):
        starts.append(acc)
        for (off, _k) in sh.get("events", []):
            points.append(acc + off)
        acc += float(sh["dur"])
    points.append(acc)
    points = sorted(set(points))
    for a, b in zip(points, points[1:]):
        if b - a > max_gap:
            idx = max(i for i, s in enumerate(starts) if s <= a + 1e-6)
            warnings.append(
                "giay %.1f-%.1f (%.1fs khong bien co) - canh #%d (%s)"
                % (a, b, b - a, idx + 1, shots[idx].get("name", "?")))
    return warnings
