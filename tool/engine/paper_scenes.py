#!/usr/bin/env python3
"""PAPER SCENES - dang ky 10 mau canh goi "paper" (giay & muc).

Cung pattern registry cua test01_scenes: SPEC tham so -> UI tu sinh
form; id canh "pp:<key>", tpack="paper". Moi mau co tham so "layout"
(bien the bo cuc, "" = tu xoay) va "bg" (ruled/plain/grid).
draw_template them hieu ung LAT TRANG 0.32s o dau shot.
"""
import math

import paper_templates as pt
from test01_scenes import scan_pacing  # noqa: F401

W, H = pt.W, pt.H


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
    return 1 if str(p.get("layout", "") or "").strip() == "2" else 0


# ------------------------------------------------------------------ prep
def _prep_stamp(p, dur):
    return {"_stamp_at": min(1.1, max(0.5, dur * 0.4))}


def _prep_notebook(p, dur):
    lines = [x for x in p["lines"].split("|")]
    raw = [_clamp(len(x) * 0.030, 0.4, 1.2) for x in lines]
    budget = max(0.6, dur - 1.3)
    tot = sum(raw)
    if tot > budget:
        raw = [r * budget / tot for r in raw]
    starts, acc = [], 0.55
    for r in raw:
        starts.append((acc, acc + r))
        acc += r
    return {"_line_starts": starts}


def _prep_items(p, dur):
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    n = max(1, len(items))
    stagger = _clamp((dur - 1.1) / n, 0.25, 0.55)
    return {"_starts": [0.5 + i * stagger for i in range(n)]}


def _prep_steps(p, dur):
    steps = [x.strip() for x in p["steps"].split("|") if x.strip()]
    n = max(1, len(steps))
    stagger = _clamp((dur - 1.2) / n, 0.3, 0.6)
    return {"_starts": [0.4 + i * stagger for i in range(n)]}


def _prep_counter(p, dur):
    return {"_target": _num(p["value"], 1298),
            "_count_dur": min(2.2, max(0.5, dur * 0.55))}


def _prep_grid(p, dur):
    total = max(1, int(_num(p["count"], 6)))
    cols = max(1, int(_num(p["cols"], 3)))
    step = _clamp((dur - 1.6) / total, 0.1, 0.35)
    return {"_total": total, "_cols": cols, "_step": step}


def _prep_progress(p, dur):
    fill = min(1.6, max(0.4, dur * 0.35))
    return {"_pct": _clamp(_num(p["pct"], 75), 0, 100),
            "_fill_dur": fill, "_t_lines": 0.3 + fill + 0.15}


def _prep_follow(p, dur):
    return {"_click_at": min(2.4, max(1.5, dur * 0.55))}


_PREP = {"stamp_verdict": _prep_stamp, "notebook_demo": _prep_notebook,
         "checklist": _prep_items, "note_grid": _prep_grid,
         "steps_up": _prep_steps, "big_number_ink": _prep_counter,
         "progress_hand": _prep_progress, "follow_end_paper": _prep_follow}


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
            return draw_fn(t, dur, _full_params(key, p, dur))
        return fn
    return build


def _spec(key, label, typ, default):
    return {"key": key, "label": label, "type": typ, "def": default}


_LAYOUT = _spec("layout", "Biến thể bố cục (trống = tự xoay, 1/2)",
                "text", "")
_BG = _spec("bg", "Nền giấy (ruled/plain/grid)", "text", "ruled")

TEMPLATES = {
    "note_hook": {
        "name": "note_hook — Note dán mở đầu",
        "desc": "Note vàng rơi xuống dán lệch + headline mực đen, quẹt dạ quang dưới từ khóa, mũi tên đỏ vẽ tay",
        "tags": "hook note dan mo dau cau hoi flop quang cao mui ten",
        "params": [
            _spec("note", "Chữ trên note (viết tay)", "text",
                  "sao video nào cũng flop?"),
            _spec("head", "Headline mực lớn", "text",
                  "KHÔNG PHẢI DO THUẬT TOÁN."),
            _spec("accent", "Từ được quẹt dạ quang", "text", "THUẬT TOÁN."),
            _spec("sub", "Dòng viết tay dưới (trống = không)", "text", ""),
            _LAYOUT, _BG,
        ],
        "build": _builder("note_hook", pt.note_hook),
    },
    "stamp_verdict": {
        "name": "stamp_verdict — Tem phán quyết",
        "desc": "Chữ mực lớn + tem đỏ đóng xuống (mực mòn) + rung giấy nhẹ",
        "tags": "stamp verdict tem phan quyet ket luan sai dung dong dau",
        "params": [
            _spec("big", "Chữ lớn", "text", "HỎI SAI CÂU RỒI."),
            _spec("stamp", "Chữ trong tem", "text", "SAI!"),
            _spec("stamp_col", "Màu tem (red/blue)", "text", "red"),
            _spec("sub", "Dòng viết tay dưới (trống = không)", "text",
                  "hỏi đúng câu mới ra video đúng"),
            _LAYOUT, _BG,
        ],
        "build": _builder("stamp_verdict", pt.stamp_verdict),
    },
    "notebook_demo": {
        "name": "notebook_demo — Trang sổ demo",
        "desc": "Trang sổ có lỗ xoắn, chữ viết tay hiện dần từng dòng như đang viết thật",
        "tags": "notebook demo trang so viet tay dong dan giai thich skill ghi chep",
        "params": [
            _spec("title", "Tiêu đề trang", "text", "Công thức giữ người xem"),
            _spec("lines", "Các dòng viết tay (ngăn |)", "text",
                  "Hook trong 3 giây đầu.|Mỗi 3 giây 1 biến cố mới.|Móc treo mở sớm, trả muộn.|Kết mở để kéo phần 2."),
            _LAYOUT, _BG,
        ],
        "build": _builder("notebook_demo", pt.notebook_demo),
    },
    "paper_ab": {
        "name": "paper_ab — So sánh 2 tờ giấy",
        "desc": "Trái: tờ phác xám trống rỗng; phải: tờ mực đầy đủ có biểu đồ; băng dính + huy hiệu VS",
        "tags": "ab so sanh 2 to giay vs trai phai before after khac biet",
        "params": [
            _spec("head", "Tiêu đề viết tay", "text", "cùng một ý tưởng:"),
            _spec("label_a", "Nhãn tờ trái", "text", "không ai đạo diễn"),
            _spec("label_b", "Nhãn tờ phải", "text", "có người đạo diễn"),
            _LAYOUT, _BG,
        ],
        "build": _builder("paper_ab", pt.paper_ab),
    },
    "checklist": {
        "name": "checklist — Checklist tích tay",
        "desc": "Ô vuông vẽ tay, dấu tích đỏ vẽ dần từng mục, mục cuối được khoanh tròn từ khóa",
        "tags": "checklist tich tay danh sach cac muc cong thuc kiem tra",
        "params": [
            _spec("title", "Tiêu đề", "text", "Công thức giữ người xem"),
            _spec("items", "Các mục (cách nhau dấu phẩy, tối đa 6)", "text",
                  "Hook trong 3 giây đầu,Mỗi 3 giây 1 biến cố mới,Kết mở để kéo phần 2"),
            _spec("circle", "Từ khoanh tròn ở mục cuối", "text", "phần 2"),
            _LAYOUT, _BG,
        ],
        "build": _builder("checklist", pt.checklist),
    },
    "big_number_ink": {
        "name": "big_number_ink — Số mực lớn",
        "desc": "Số mực đen chạy tăng khổ lớn, đếm xong bị khoanh tròn đỏ 2 vòng",
        "tags": "big number so lon muc chay tang so lieu khoanh tron thong ke",
        "params": [
            _spec("value", "Số đích", "number", "1298"),
            _spec("label", "Nhãn viết tay", "text", "hiệu ứng âm thanh"),
            _spec("sub", "Dòng phụ (trống = không)", "text", ""),
            _LAYOUT, _BG,
        ],
        "build": _builder("big_number_ink", pt.big_number_ink),
    },
    "note_grid": {
        "name": "note_grid — Lưới note dán",
        "desc": "Lưới note dán nhiều màu bật vào lần lượt, đánh số từng note",
        "tags": "note grid luoi note dan nhieu mau danh so phong cach cac muc",
        "params": [
            _spec("title", "Tiêu đề", "text", "6 thứ phải có:"),
            _spec("items", "Chữ từng note (cách nhau dấu phẩy)", "text",
                  "hook,nhịp,móc treo,số liệu,leo thang,kết mở"),
            _spec("count", "Tổng số note", "number", "6"),
            _spec("cols", "Số cột", "number", "3"),
            _spec("caption", "Chú thích dưới (trống = không)", "text", ""),
            _LAYOUT, _BG,
        ],
        "build": _builder("note_grid", pt.note_grid),
    },
    "progress_hand": {
        "name": "progress_hand — Thanh tiến trình vẽ tay",
        "desc": "Thanh viền vẽ tay điền gạch chéo xanh + 3 dòng chữ viết tay lật câu hỏi",
        "tags": "progress hand thanh tien trinh ve tay phan tram gach cheo 75 25",
        "params": [
            _spec("pct", "Phần trăm đích", "number", "75"),
            _spec("line1", "Dòng 1", "text", "Hệ thống lo 75%..."),
            _spec("question", "Câu hỏi lật (đỏ)", "text", "25% còn lại?"),
            _spec("answer", "Dòng trả lời", "text",
                  "Là BẠN. Ý tưởng của BẠN."),
            _LAYOUT, _BG,
        ],
        "build": _builder("progress_hand", pt.progress_hand),
    },
    "steps_up": {
        "name": "steps_up — Bậc thang leo ý",
        "desc": "Thẻ giấy xếp bậc thang leo lên, mũi tên tay nối từng bậc, tem đỏ chốt trên đỉnh",
        "tags": "steps bac thang leo y tuong tang dan cac buoc thang",
        "params": [
            _spec("title", "Tiêu đề nhỏ", "text", "3 ý tưởng, 1 chiếc thang:"),
            _spec("steps", "Các bậc (Tiêu đề::mô tả, ngăn |)", "text",
                  "Ý 1::hook thật mạnh|Ý 2::biến cố liên tục|Ý 3::kết mở phần 2"),
            _spec("stamp", "Tem chốt (trống = không)", "text",
                  "GIỮ ĐƯỢC NGƯỜI XEM"),
            _LAYOUT, _BG,
        ],
        "build": _builder("steps_up", pt.steps_up),
    },
    "follow_end_paper": {
        "name": "follow_end_paper — Màn hình cuối giấy",
        "desc": "Chữ chốt mực + nút giấy THEO DÕI, bấm xong nút hóa đen + khoanh đỏ",
        "tags": "follow end man hinh cuoi theo doi nut giay phan 2 subscribe",
        "params": [
            _spec("main", "Dòng chốt 1", "text", "Phần khó đã có người làm."),
            _spec("sub", "Dòng chốt 2", "text", "Việc của bạn chỉ là BẮT ĐẦU."),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI"),
            _spec("done_text", "Chữ nút sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _spec("side_text", "Chữ cạnh nút (trống = không)", "text",
                  "để xem PHẦN 2"),
            _LAYOUT, _BG,
        ],
        "build": _builder("follow_end_paper", pt.follow_end_paper),
    },
}

VARIANTS = {k: 2 for k in TEMPLATES}


def template_catalog():
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    p = _full_params(name, params, dur)
    fn = TEMPLATES[name]["build"](p, {"text": text})
    img = fn(tm, dur)
    return pt.page_in(img, tm)


def events_for(name, params, dur):
    p = _full_params(name, params, dur)
    ev = [(0.0, "flip")]
    if name == "note_hook":
        ev += [(0.15, "pop"), (0.65, "draw"), (1.05, "draw"), (1.5, "draw")]
    elif name == "stamp_verdict":
        ev += [(0.1, "draw"), (p["_stamp_at"], "stamp")]
    elif name == "notebook_demo":
        ev += [(s, "draw") for (s, _e) in p["_line_starts"]]
    elif name == "paper_ab":
        ev += [(0.1, "draw"), (0.35, "pop"), (0.7, "pop"), (1.0, "pop")]
    elif name == "checklist":
        ev += [(s, "tick") for s in p["_starts"]]
        ev.append((0.15, "draw"))
    elif name == "big_number_ink":
        cd = p["_count_dur"]
        ev += [(0.25 + cd * k / 8.0, "tick") for k in range(9)]
        ev.append((0.25 + cd, "draw"))
    elif name == "note_grid":
        ev += [(0.45 + i * p["_step"], "pop")
               for i in range(int(p["_total"]))]
    elif name == "progress_hand":
        fill = p["_fill_dur"]
        ev += [(0.3 + fill * k / 4.0, "tick") for k in range(5)]
        tl = p["_t_lines"]
        ev += [(tl, "draw"), (tl + 0.55, "draw"), (tl + 1.10, "draw")]
    elif name == "steps_up":
        ev += [(s, "pop") for s in p["_starts"]]
    elif name == "follow_end_paper":
        ev += [(0.15, "draw"), (0.9, "pop"), (p["_click_at"], "stamp")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)
