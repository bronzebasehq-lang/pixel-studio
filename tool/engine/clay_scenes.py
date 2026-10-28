#!/usr/bin/env python3
"""CLAY SCENES - dang ky 10 mau canh goi "clay" (dat set stop-motion).

Cung pattern voi crt_scenes/test01_scenes: moi template co SPEC tham
so, UI tu sinh form; params luu theo cau, id canh trong UI "cl:<key>",
truong tpack="clay" o payload. Moi mau co tham so "layout" (bien the
bo cuc): "" = tu xoay o lop render (packs.resolve_layout), "1"/"2" =
chon tay. draw_template doc layout -> p["_layout"] (0/1).

events_for() phuc vu BO QUET NHIP dung chung (scan_pacing cua
test01_scenes) va lop SFX cua video mau.
"""
import math

import clay_templates as cl
from test01_scenes import scan_pacing  # noqa: F401  (dung chung 1 ban quet)

W, H = cl.W, cl.H


def _s(v, default=""):
    return default if v is None else str(v)


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


def _layout_of(p):
    raw = str(p.get("layout", "") or "").strip()
    return 1 if raw == "2" else 0


# ------------------------------------------------------------------ prep
def _prep_window(p, dur):
    lines = [x for x in p["lines"].split("|")]
    n = max(1, len(lines))
    stagger = _clamp((dur - 1.2) / n, 0.22, 0.5)
    return {"_starts": [0.5 + i * stagger for i in range(n)]}


def _prep_list(p, dur):
    items = [x for x in p["items"].split(",")]
    n = max(1, len(items))
    stagger = _clamp((dur - 1.0) / n, 0.22, 0.5)
    return {"_starts": [0.4 + i * stagger for i in range(n)]}


def _prep_stamp(p, dur):
    return {"_stamp_at": min(1.15, max(0.55, dur * 0.38))}


def _prep_number(p, dur):
    return {"_target": _num(p["value"], 1298),
            "_count_dur": min(2.2, max(0.5, dur * 0.55))}


def _prep_grid(p, dur):
    total = max(1, int(_num(p["count"], 6)))
    cols = max(1, int(_num(p["cols"], 3)))
    step = _clamp((dur - 1.6) / total, 0.10, 0.35)
    return {"_total": total, "_cols": cols, "_step": step}


def _prep_worm(p, dur):
    fill = min(1.6, max(0.4, dur * 0.35))
    return {"_pct": _clamp(_num(p["pct"], 70), 0, 100),
            "_fill_dur": fill, "_t_lines": 0.3 + fill + 0.35}


def _prep_end(p, dur):
    return {"_click_at": min(2.6, max(1.6, dur * 0.55))}


_PREP = {"clay_window": _prep_window, "clay_list": _prep_list,
         "stamp_verdict": _prep_stamp, "big_number": _prep_number,
         "clay_grid": _prep_grid, "worm_progress": _prep_worm,
         "clay_button_end": _prep_end}


def _full_params(key, params, dur):
    info = TEMPLATES[key]
    p = _merged(info["params"], params)
    p["_layout"] = _layout_of(p)
    prep = _PREP.get(key)
    if prep:
        p.update(prep(p, dur))
    return p


def _builder(key, draw_fn):
    def build(p, ctx):
        def fn(t, dur):
            full = _full_params(key, p, dur)
            return draw_fn(t, dur, full)
        return fn
    return build


def _spec(key, label, typ, default):
    return {"key": key, "label": label, "type": typ, "def": default}


_LAYOUT = _spec("layout", "Biến thể bố cục (trống = tự xoay, 1/2)",
                "text", "")

TEMPLATES = {
    "clay_hook": {
        "name": "clay_hook — Móc phiến đất sét",
        "desc": "Phiến đất sét lớn nảy squash vào khung, chữ trắng đúc trên phiến + 3 cục đất sét nhỏ nảy quanh",
        "tags": "hook moc phien dat set clay mo dau cau hoi squash nay",
        "params": [
            _spec("head1", "Dòng chữ 1", "text", "AI VIẾT CODE"),
            _spec("head2", "Dòng chữ 2", "text", "THAY BẠN RỒI"),
            _spec("color", "Màu phiến (coral/teal/must/sky)", "text", "coral"),
            _spec("sub", "Dòng phụ dưới (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("clay_hook", cl.clay_hook),
    },
    "stamp_verdict": {
        "name": "stamp_verdict — Phán quyết con dấu đất sét",
        "desc": "Phiến kem + headline mực, con dấu đất sét tròn dập xuống kèm chữ phán quyết",
        "tags": "verdict phan quyet con dau stamp ket luan dung sai dat set",
        "params": [
            _spec("head", "Headline", "text", "CÁCH NÀY CÓ THẬT SỰ HIỆU QUẢ?"),
            _spec("verdict", "Chữ trong con dấu", "text", "ĐÚNG!"),
            _spec("stamp_col", "Màu dấu (teal/coral/must/sky)", "text", "teal"),
            _spec("sub", "Dòng phụ dưới (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("stamp_verdict", cl.stamp_verdict),
    },
    "clay_window": {
        "name": "clay_window — Cửa sổ đất sét",
        "desc": "Khung cửa sổ đất sét xanh trời, các dòng nội dung nảy vào kèm viên màu đánh dấu",
        "tags": "window cua so demo noi dung dong code giao dien dat set",
        "params": [
            _spec("title", "Tiêu đề cửa sổ", "text", "BÊN TRONG CÔNG CỤ"),
            _spec("lines", "Dòng nội dung (ngăn |)", "text",
                  "mở file kịch bản|tool tự gán cảnh|bấm render là xong"),
            _LAYOUT,
        ],
        "build": _builder("clay_window", cl.clay_window),
    },
    "clay_ab": {
        "name": "clay_ab — So sánh 2 phiến đất sét",
        "desc": "Phiến trái xám nhỏ (cách cũ) vs phiến phải màu lớn (cách mới), bóng VS ở giữa",
        "tags": "ab so sanh 2 phien vs trai phai cu moi khac biet dat set",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "CÙNG MỘT Ý TƯỞNG"),
            _spec("label_a", "Nhãn trái", "text", "CÁCH CŨ"),
            _spec("note_a", "Ghi chú trái", "text", "làm tay 3 ngày"),
            _spec("label_b", "Nhãn phải", "text", "CÁCH MỚI"),
            _spec("note_b", "Ghi chú phải", "text", "xong trong 1 giờ"),
            _spec("color_b", "Màu phiến phải (coral/teal/must/sky)", "text",
                  "coral"),
            _LAYOUT,
        ],
        "build": _builder("clay_ab", cl.clay_ab),
    },
    "clay_list": {
        "name": "clay_list — Danh sách viên xếp chồng",
        "desc": "Các viên/phiến đất sét màu xếp chồng, nảy squash từng mục",
        "tags": "list danh sach vien xep chong muc thanh phan cong thuc dat set",
        "params": [
            _spec("title", "Tiêu đề", "text", "CHỈ CẦN 3 THỨ NÀY"),
            _spec("items", "Các mục (ngăn ,)", "text",
                  "1 NGƯỜI,1 Ý TƯỞNG,0 ĐỒNG VỐN"),
            _LAYOUT,
        ],
        "build": _builder("clay_list", cl.clay_list),
    },
    "big_number": {
        "name": "big_number — Số đất sét khổng lồ",
        "desc": "Số đếm tăng nặn trên phiến đất sét lớn, nảy nhẹ khi chạm đích",
        "tags": "big number so lon dem tang so lieu thong ke dat set",
        "params": [
            _spec("value", "Số đích", "number", "1298"),
            _spec("color", "Màu phiến (must/coral/teal/sky)", "text", "must"),
            _spec("label", "Nhãn dưới số", "text", "VIDEO ĐÃ LÀM XONG"),
            _spec("sub", "Dòng phụ (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("big_number", cl.big_number),
    },
    "clay_grid": {
        "name": "clay_grid — Lưới viên đất sét",
        "desc": "Lưới viên đất sét tròn đánh số, nảy vào lần lượt",
        "tags": "grid luoi vien o modules he thong nhieu muc dat set",
        "params": [
            _spec("title", "Tiêu đề", "text", "CẢ HỆ THỐNG GỒM:"),
            _spec("count", "Tổng số viên", "number", "6"),
            _spec("cols", "Số cột", "number", "3"),
            _spec("caption", "Chú thích dưới (trống = không)", "text",
                  "viên nào cũng nảy đúng nhịp"),
            _LAYOUT,
        ],
        "build": _builder("clay_grid", cl.clay_grid),
    },
    "worm_progress": {
        "name": "worm_progress — Tiến trình con sâu đất sét",
        "desc": "Con sâu đất sét uốn khúc lấp đầy rãnh tới % đích, rồi lật câu hỏi + trả lời",
        "tags": "worm progress tien trinh con sau phan tram ranh dat set",
        "params": [
            _spec("pct", "Phần trăm đích", "number", "70"),
            _spec("line1", "Dòng 1", "text", "Mới đi được 70% chặng..."),
            _spec("question", "Câu hỏi lật", "text", "30% còn lại là gì?"),
            _spec("answer", "Dòng trả lời", "text", "LÀ KỶ LUẬT MỖI NGÀY."),
            _LAYOUT,
        ],
        "build": _builder("worm_progress", cl.worm_progress),
    },
    "steps_up": {
        "name": "steps_up — Bậc thang nặn leo thang",
        "desc": "3 bậc thang đất sét tăng dần, bóng đất sét nhảy lên từng bậc",
        "tags": "steps leo thang bac thang nac tang dan level dat set",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "LEO TỪNG NẤC MỘT"),
            _spec("labels", "Nhãn 3 bậc (ngăn |)", "text",
                  "BẮT ĐẦU|ĐỀU ĐẶN|BỨT PHÁ"),
            _LAYOUT,
        ],
        "build": _builder("steps_up", cl.steps_up),
    },
    "clay_button_end": {
        "name": "clay_button_end — Màn cuối nút đất sét",
        "desc": "2 dòng chốt + nút đất sét lớn tự ép xuống (đã bấm) và đổi màu",
        "tags": "end man cuoi nut bam theo doi ket thuc phan 2 dat set",
        "params": [
            _spec("main", "Dòng chốt chính", "text",
                  "Phần khó đã có tool lo."),
            _spec("sub", "Dòng chốt phụ", "text",
                  "Việc của bạn chỉ là BẮT ĐẦU."),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI"),
            _spec("done_text", "Chữ sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _LAYOUT,
        ],
        "build": _builder("clay_button_end", cl.clay_button_end),
    },
}

VARIANTS = {k: 2 for k in TEMPLATES}


def template_catalog():
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    """Ve 1 frame CLAY tai tm."""
    p = _full_params(name, params, dur)
    fn = TEMPLATES[name]["build"](p, {"text": text})
    return fn(tm, dur)


# ------------------------------------------------------------------ su kien
def events_for(name, params, dur):
    p = _full_params(name, params, dur)
    ev = []
    if name == "clay_hook":
        ev = [(0.15, "boing"), (0.55, "pop"), (0.71, "pop"), (0.87, "pop"),
              (1.25, "plip")]
    elif name == "stamp_verdict":
        ev = [(0.12, "pop"), (p["_stamp_at"], "splat"),
              (p["_stamp_at"] + 0.45, "plip")]
    elif name == "clay_window":
        ev = [(0.12, "pop")] + [(s, "pop") for s in p["_starts"]]
    elif name == "clay_ab":
        ev = [(0.35, "pop"), (0.6, "pop"), (1.0, "boing")]
    elif name == "clay_list":
        ev = [(s, "pop") for s in p["_starts"]]
    elif name == "big_number":
        cd = p["_count_dur"]
        ev = [(0.25 + cd * k / 8.0, "plip") for k in range(9)]
        ev.append((0.25 + cd, "boing"))
    elif name == "clay_grid":
        ev = [(0.45 + i * p["_step"], "pop")
              for i in range(0, int(p["_total"]), 3)]
        ev.append((0.45 + int(p["_total"]) * p["_step"], "plip"))
    elif name == "worm_progress":
        fill = p["_fill_dur"]
        ev = [(0.3 + fill * k / 4.0, "pop") for k in range(5)]
        tl = p["_t_lines"]
        ev += [(tl, "plip"), (tl + 0.55, "pop"), (tl + 1.10, "boing")]
    elif name == "steps_up":
        ev = [(0.35, "pop"), (0.7, "pop"), (1.05, "pop"),
              (0.75, "boing"), (1.15, "boing"), (1.55, "boing")]
    elif name == "clay_button_end":
        ev = [(0.15, "pop"), (1.0, "pop"), (p["_click_at"], "splat"),
              (p["_click_at"] + 0.2, "chime")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)
