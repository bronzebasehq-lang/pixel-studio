#!/usr/bin/env python3
"""FLAT SCENES - dang ky 10 mau canh goi "flat" (do hoa phang).

Cung pattern voi crt_scenes: moi template co SPEC tham so, UI tu sinh
form; id canh trong UI "fl:<key>", truong tpack="flat". Moi mau co
tham so "layout": "" = tu xoay (packs.resolve_layout), "1"/"2" = tay.

events_for() phuc vu bo quet nhip + lop SFX cua video mau.
"""
import flat_templates as fl
from test01_scenes import scan_pacing  # noqa: F401

W, H = fl.W, fl.H


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


def _prep_verdict(p, dur):
    return {"_stamp_at": min(1.1, max(0.5, dur * 0.38))}


def _prep_grid(p, dur):
    total = max(1, int(_num(p["count"], 6)))
    cols = max(1, int(_num(p["cols"], 3)))
    step = _clamp((dur - 1.6) / total, 0.10, 0.35)
    return {"_total": total, "_cols": cols, "_step": step}


def _prep_progress(p, dur):
    fill = min(1.6, max(0.4, dur * 0.35))
    return {"_pct": _clamp(_num(p["pct"], 72), 0, 100),
            "_fill_dur": fill, "_t_lines": 0.3 + fill + 0.15}


def _prep_end(p, dur):
    return {"_click_at": min(2.6, max(1.6, dur * 0.55))}


_PREP = {"flat_window": _prep_window, "flat_list": _prep_list,
         "verdict_block": _prep_verdict, "flat_grid": _prep_grid,
         "flat_progress": _prep_progress, "flat_end": _prep_end}


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
    "flat_hook": {
        "name": "flat_hook — Móc vòng tròn hệ số",
        "desc": "Nền trơn + vòng tròn trắng lớn chứa hệ số ×N, headline trái + gạch chân vàng",
        "tags": "hook moc vong tron he so x3 mo dau phang flat",
        "params": [
            _spec("head1", "Dòng chữ 1", "text", "TỐC ĐỘ"),
            _spec("head2", "Dòng chữ 2", "text", "GẤP 3 LẦN"),
            _spec("mult", "Hệ số trong vòng tròn", "text", "×3"),
            _spec("bgc", "Màu nền (coral/teal/yel/navy)", "text", "coral"),
            _LAYOUT,
        ],
        "build": _builder("flat_hook", fl.flat_hook),
    },
    "verdict_block": {
        "name": "verdict_block — Phán quyết khối màu",
        "desc": "Headline trên nền navy, khối màu phẳng dập xuống chứa chữ phán quyết",
        "tags": "verdict phan quyet khoi mau ket luan dung sai phang flat",
        "params": [
            _spec("head", "Headline", "text", "CÁCH NÀY CÓ HIỆU QUẢ KHÔNG?"),
            _spec("verdict", "Chữ phán quyết", "text", "CÓ. RẤT RÕ."),
            _spec("color", "Màu khối (teal/coral/yel)", "text", "teal"),
            _spec("sub", "Dòng phụ dưới (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("verdict_block", fl.verdict_block),
    },
    "flat_window": {
        "name": "flat_window — Cửa sổ phẳng",
        "desc": "Cửa sổ trắng thanh tiêu đề navy trên nền ngọc, dòng nội dung kèm ô màu",
        "tags": "window cua so demo noi dung dong phang flat",
        "params": [
            _spec("title", "Tiêu đề cửa sổ", "text", "BÊN TRONG CÔNG CỤ"),
            _spec("lines", "Dòng nội dung (ngăn |)", "text",
                  "mở file kịch bản|tool tự gán cảnh|bấm render là xong"),
            _LAYOUT,
        ],
        "build": _builder("flat_window", fl.flat_window),
    },
    "flat_ab": {
        "name": "flat_ab — So sánh chia đôi",
        "desc": "Nửa navy đống khối xám lộn xộn (cách cũ) vs nửa vàng 1 vòng tròn gọn (cách mới)",
        "tags": "ab so sanh chia doi cu moi vs phang flat",
        "params": [
            _spec("label_a", "Nhãn bên cũ", "text", "CÁCH CŨ"),
            _spec("label_b", "Nhãn bên mới", "text", "CÁCH MỚI"),
            _spec("question", "Câu hỏi dải dưới", "text",
                  "BẠN CHỌN BÊN NÀO?"),
            _LAYOUT,
        ],
        "build": _builder("flat_ab", fl.flat_ab),
    },
    "flat_list": {
        "name": "flat_list — Danh sách hàng phẳng",
        "desc": "Các hàng màu phẳng trượt vào lần lượt trên nền sáng",
        "tags": "list danh sach hang truot muc thanh phan phang flat",
        "params": [
            _spec("title", "Tiêu đề", "text", "3 THỨ CẦN CÓ"),
            _spec("items", "Các mục (ngăn ,)", "text",
                  "Một ý tưởng rõ ràng,Một công cụ tự động,Một giờ mỗi ngày"),
            _LAYOUT,
        ],
        "build": _builder("flat_list", fl.flat_list),
    },
    "flat_data": {
        "name": "flat_data — Cột phẳng + số khổng lồ",
        "desc": "4 cột phẳng tăng dần + số liệu khổng lồ bên cạnh",
        "tags": "data so lieu cot bieu do phan tram khong lo phang flat",
        "params": [
            _spec("values", "4 giá trị cột (ngăn ,)", "text", "25,40,65,90"),
            _spec("big", "Số khổng lồ", "text", "94,6%"),
            _spec("big_label", "Nhãn dưới số", "text", "ĐÚNG HƠN HẲN"),
            _spec("note", "Chú thích nhỏ (trống = không)", "text",
                  "tỉ lệ trả lời đúng — bản mới so với bản cũ"),
            _LAYOUT,
        ],
        "build": _builder("flat_data", fl.flat_data),
    },
    "flat_grid": {
        "name": "flat_grid — Lưới ô phẳng",
        "desc": "Lưới ô vuông màu phẳng đánh số trên nền navy, ô cuối màu nhấn",
        "tags": "grid luoi o vuong modules he thong phang flat",
        "params": [
            _spec("title", "Tiêu đề", "text", "HỆ THỐNG GỒM:"),
            _spec("count", "Tổng số ô", "number", "6"),
            _spec("cols", "Số cột", "number", "3"),
            _spec("caption", "Chú thích dưới (trống = không)", "text",
                  "ô cuối là ô quan trọng nhất"),
            _LAYOUT,
        ],
        "build": _builder("flat_grid", fl.flat_grid),
    },
    "flat_progress": {
        "name": "flat_progress — Thanh phẳng / phần trăm",
        "desc": "Thanh phẳng chạy % trên nền sáng rồi lật câu hỏi + trả lời",
        "tags": "progress thanh phan tram tien trinh phang flat",
        "params": [
            _spec("pct", "Phần trăm đích", "number", "72"),
            _spec("line1", "Dòng 1", "text", "Hệ thống đã lộ 72%..."),
            _spec("question", "Câu hỏi lật", "text", "28% còn lại là gì?"),
            _spec("answer", "Dòng trả lời", "text", "LÀ BẠN. Ý TƯỞNG CỦA BẠN."),
            _LAYOUT,
        ],
        "build": _builder("flat_progress", fl.flat_progress),
    },
    "flat_steps": {
        "name": "flat_steps — Bậc phẳng leo thang",
        "desc": "3 cột/bậc phẳng cao dần, huy hiệu tròn ×N trên bậc cao nhất",
        "tags": "steps leo thang bac cot tang dan x2 x3 phang flat",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "MỖI TUẦN MỘT BẬC"),
            _spec("labels", "Nhãn 3 bậc (ngăn |)", "text",
                  "TUẦN 1|TUẦN 2|TUẦN 3"),
            _spec("mult", "Huy hiệu bậc cao nhất", "text", "×4"),
            _LAYOUT,
        ],
        "build": _builder("flat_steps", fl.flat_steps),
    },
    "flat_end": {
        "name": "flat_end — Màn cuối phẳng",
        "desc": "Vòng tròn vàng + dòng chốt trắng trên navy + nút theo dõi đổi trạng thái",
        "tags": "end man cuoi theo doi nut bam ket thuc phan 2 phang flat",
        "params": [
            _spec("main", "Dòng chốt chính", "text",
                  "Phần khó đã có hệ thống lo."),
            _spec("sub", "Dòng chốt phụ", "text",
                  "Việc của bạn chỉ là BẮT ĐẦU."),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI"),
            _spec("done_text", "Chữ sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _LAYOUT,
        ],
        "build": _builder("flat_end", fl.flat_end),
    },
}

VARIANTS = {k: 2 for k in TEMPLATES}


def template_catalog():
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    """Ve 1 frame FLAT tai tm."""
    p = _full_params(name, params, dur)
    fn = TEMPLATES[name]["build"](p, {"text": text})
    return fn(tm, dur)


# ------------------------------------------------------------------ su kien
def events_for(name, params, dur):
    p = _full_params(name, params, dur)
    ev = []
    if name == "flat_hook":
        ev = [(0.15, "pop"), (0.4, "pop"), (0.55, "click")]
    elif name == "verdict_block":
        ev = [(0.15, "click"), (p["_stamp_at"], "pop"),
              (p["_stamp_at"] + 0.5, "ding")]
    elif name == "flat_window":
        ev = [(0.12, "pop")] + [(s, "click") for s in p["_starts"]]
    elif name == "flat_ab":
        ev = [(0.15, "click"), (0.4, "click"), (0.65, "pop"),
              (0.95, "click")]
    elif name == "flat_list":
        ev = [(s, "swipe") for s in p["_starts"]]
    elif name == "flat_data":
        ev = [(0.3 + i * 0.22, "click") for i in range(4)]
        ev.append((0.7, "pop"))
        ev.append((1.5, "ding"))
    elif name == "flat_grid":
        ev = [(0.4 + i * p["_step"], "click")
              for i in range(0, int(p["_total"]), 3)]
        ev.append((0.4 + int(p["_total"]) * p["_step"], "pop"))
    elif name == "flat_progress":
        fill = p["_fill_dur"]
        ev = [(0.3 + fill * k / 4.0, "click") for k in range(5)]
        tl = p["_t_lines"]
        ev += [(tl, "click"), (tl + 0.55, "pop"), (tl + 1.10, "ding")]
    elif name == "flat_steps":
        ev = [(0.35, "pop"), (0.7, "pop"), (1.05, "pop"), (1.55, "ding")]
    elif name == "flat_end":
        ev = [(0.15, "pop"), (0.8, "click"), (p["_click_at"], "ding")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)
