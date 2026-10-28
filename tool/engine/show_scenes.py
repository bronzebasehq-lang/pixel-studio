#!/usr/bin/env python3
"""SHOW SCENES - dang ky 10 mau canh goi "show" (gameshow TV).

Cung pattern voi crt_scenes: moi template co SPEC tham so, UI tu sinh
form; id canh trong UI "sh:<key>", truong tpack="show". Moi mau co
tham so "layout": "" = tu xoay (packs.resolve_layout), "1"/"2" = tay.

events_for() phuc vu bo quet nhip + lop SFX cua video mau.
"""
import show_templates as sw
from test01_scenes import scan_pacing  # noqa: F401

W, H = sw.W, sw.H


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
    return {"_starts": [0.55 + i * stagger for i in range(n)]}


def _prep_list(p, dur):
    rows = [x for x in p["rows"].split("|")]
    n = max(1, len(rows))
    stagger = _clamp((dur - 1.2) / n, 0.22, 0.5)
    return {"_starts": [0.5 + i * stagger for i in range(n)]}


def _prep_verdict(p, dur):
    return {"_verdict_at": min(1.1, max(0.5, dur * 0.36))}


def _prep_score(p, dur):
    return {"_target": _num(p["value"], 98600),
            "_count_dur": min(2.4, max(0.6, dur * 0.55))}


def _prep_grid(p, dur):
    total = max(1, int(_num(p["count"], 8)))
    cols = max(1, int(_num(p["cols"], 4)))
    step = _clamp((dur - 1.6) / total, 0.10, 0.35)
    return {"_total": total, "_cols": cols, "_step": step}


def _prep_wheel(p, dur):
    return {"_pct": _clamp(_num(p["pct"], 75), 0, 100),
            "_spin_dur": min(2.6, max(0.8, dur * 0.55))}


def _prep_end(p, dur):
    return {"_click_at": min(2.6, max(1.6, dur * 0.55))}


_PREP = {"show_window": _prep_window, "score_list": _prep_list,
         "verdict_sign": _prep_verdict, "big_score": _prep_score,
         "light_grid": _prep_grid, "wheel_progress": _prep_wheel,
         "show_end": _prep_end}


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
    "marquee_hook": {
        "name": "marquee_hook — Móc biển marquee",
        "desc": "Biển marquee viền bóng đèn nhấp nháy đuổi nhau, chữ vàng + từ nhấn hồng",
        "tags": "hook moc marquee bien bong den gameshow mo dau cau hoi show",
        "params": [
            _spec("line1", "Dòng 1", "text", "AI GIÀU NHANH NHẤT?"),
            _spec("accent", "Từ nhấn (màu hồng, nằm trong dòng 1)", "text",
                  "GIÀU"),
            _spec("line2", "Dòng 2 (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("marquee_hook", sw.marquee_hook),
    },
    "verdict_sign": {
        "name": "verdict_sign — Biển phán quyết",
        "desc": "Biển marquee bật sáng chứa chữ phán quyết, đèn xanh báo đúng 2 bên, bóng đèn đuổi nhanh",
        "tags": "verdict phan quyet bien marquee dung sai ket luan gameshow show",
        "params": [
            _spec("head", "Câu hỏi trên", "text", "LIỆU CÓ THẬT KHÔNG?"),
            _spec("verdict", "Chữ phán quyết", "text", "THẬT 100%!"),
            _spec("verdict_col", "Màu chữ (yel/pink/cyan/white)", "text",
                  "yel"),
            _spec("sub", "Dòng phụ dưới (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("verdict_sign", sw.verdict_sign),
    },
    "show_window": {
        "name": "show_window — Cửa sổ LED",
        "desc": "Bảng LED đen, dòng mono vàng hiện dần kèm vệt quét sáng chạy dọc bảng",
        "tags": "window cua so led demo noi dung dong gameshow show",
        "params": [
            _spec("title", "Tiêu đề bảng", "text", "BÊN TRONG CÔNG CỤ"),
            _spec("lines", "Dòng nội dung (ngăn |)", "text",
                  "mo file kich ban|tool tu gan canh|bam render la xong"),
            _LAYOUT,
        ],
        "build": _builder("show_window", sw.show_window),
    },
    "show_ab": {
        "name": "show_ab — So sánh 2 biển",
        "desc": "Biển trái tắt đèn mờ (cách cũ) vs biển phải marquee sáng đuổi đèn (cách mới), huy hiệu VS",
        "tags": "ab so sanh 2 bien vs cu moi gameshow show",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "CÙNG MỘT Ý TƯỞNG"),
            _spec("label_a", "Nhãn biển trái", "text", "CÁCH CŨ"),
            _spec("note_a", "Ghi chú trái", "text", "làm tay 3 ngày"),
            _spec("label_b", "Nhãn biển phải", "text", "CÁCH MỚI"),
            _spec("note_b", "Ghi chú phải", "text", "xong trong 1 giờ"),
            _LAYOUT,
        ],
        "build": _builder("show_ab", sw.show_ab),
    },
    "score_list": {
        "name": "score_list — Bảng điểm danh sách",
        "desc": "Bảng LED liệt kê từng mục kèm điểm số mono vàng, hiện dần từng dòng",
        "tags": "score list bang diem danh sach muc diem so gameshow show",
        "params": [
            _spec("title", "Tiêu đề bảng", "text", "BẢNG ĐIỂM TUẦN NÀY"),
            _spec("rows", "Dòng (tên::điểm, ngăn |)", "text",
                  "Video 1::98.600|Video 2::87.200|Video 3::76.450"),
            _LAYOUT,
        ],
        "build": _builder("score_list", sw.score_list),
    },
    "big_score": {
        "name": "big_score — Số điểm LED khổng lồ",
        "desc": "Số điểm mono vàng đếm tăng trong khung marquee viền đèn trên bảng LED đen",
        "tags": "big score diem so led khong lo dem tang gameshow show",
        "params": [
            _spec("value", "Số đích", "number", "98600"),
            _spec("label", "Nhãn dưới bảng", "text", "LƯỢT XEM TUẦN NÀY"),
            _spec("sub", "Dòng phụ (trống = không)", "text", ""),
            _LAYOUT,
        ],
        "build": _builder("big_score", sw.big_score),
    },
    "light_grid": {
        "name": "light_grid — Lưới đèn sân khấu",
        "desc": "Lưới bóng đèn tròn sân khấu bật sáng lần lượt nhiều màu kèm hào quang",
        "tags": "light grid luoi den san khau bong sang gameshow show",
        "params": [
            _spec("title", "Tiêu đề", "text", "CẢ SÂN KHẤU BẬT SÁNG:"),
            _spec("count", "Tổng số đèn", "number", "8"),
            _spec("cols", "Số cột", "number", "4"),
            _spec("caption", "Chú thích dưới (trống = không)", "text",
                  "đèn cuối cùng là đèn quan trọng nhất"),
            _LAYOUT,
        ],
        "build": _builder("light_grid", sw.light_grid),
    },
    "wheel_progress": {
        "name": "wheel_progress — Vòng quay tiến trình",
        "desc": "Vòng quay 8 múi quay chậm dần dừng ở múi theo % + bảng LED % bên cạnh",
        "tags": "wheel vong quay tien trinh phan tram may man gameshow show",
        "params": [
            _spec("pct", "Phần trăm đích (quyết định múi dừng)", "number",
                  "75"),
            _spec("mult", "Nhãn múi đích", "text", "×10"),
            _spec("label", "Dòng chốt dưới (trống = không)", "text",
                  "Vòng quay không nói dối."),
            _LAYOUT,
        ],
        "build": _builder("wheel_progress", sw.wheel_progress),
    },
    "podium_steps": {
        "name": "podium_steps — Bục leo thang 2-1-3",
        "desc": "Bục trao giải 2-1-3 dựng lên lần lượt, hộp quà phát sáng trên bục số 1",
        "tags": "podium buc leo thang giai 1 2 3 thang hang gameshow show",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "BẢNG XẾP HẠNG TUẦN NÀY"),
            _spec("labels", "Nhãn bục 1|2|3 (ngăn |)", "text",
                  "VIDEO A|VIDEO B|VIDEO C"),
            _LAYOUT,
        ],
        "build": _builder("podium_steps", sw.podium_steps),
    },
    "show_end": {
        "name": "show_end — Màn cuối marquee + pháo giấy",
        "desc": "Biển marquee dòng chốt + nút theo dõi, bấm xong pháo giấy rơi đầy khung",
        "tags": "end man cuoi marquee phao giay theo doi ket thuc gameshow show",
        "params": [
            _spec("main", "Dòng chốt chính", "text",
                  "Phần khó đã có hệ thống lo."),
            _spec("sub", "Dòng chốt phụ", "text",
                  "Việc của bạn chỉ là BẮT ĐẦU."),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI"),
            _spec("done_text", "Chữ sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _LAYOUT,
        ],
        "build": _builder("show_end", sw.show_end),
    },
}

VARIANTS = {k: 2 for k in TEMPLATES}


def template_catalog():
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    """Ve 1 frame SHOW tai tm."""
    p = _full_params(name, params, dur)
    fn = TEMPLATES[name]["build"](p, {"text": text})
    return fn(tm, dur)


# ------------------------------------------------------------------ su kien
def events_for(name, params, dur):
    p = _full_params(name, params, dur)
    ev = []
    if name == "marquee_hook":
        ev = [(0.35, "sparkle"), (0.8, "sparkle"), (1.3, "bell")]
    elif name == "verdict_sign":
        ev = [(p["_verdict_at"], "bell"), (p["_verdict_at"] + 0.25, "bell"),
              (p["_verdict_at"] + 0.55, "sparkle")]
    elif name == "show_window":
        ev = [(0.12, "tick")] + [(s, "tick") for s in p["_starts"]]
    elif name == "show_ab":
        ev = [(0.35, "buzz"), (0.6, "sparkle"), (1.0, "bell")]
    elif name == "score_list":
        ev = [(s, "tick") for s in p["_starts"]]
        ev.append((p["_starts"][-1] + 0.3, "bell"))
    elif name == "big_score":
        cd = p["_count_dur"]
        ev = [(0.3 + cd * k / 10.0, "tick") for k in range(11)]
        ev.append((0.3 + cd, "fanfare"))
    elif name == "light_grid":
        ev = [(0.4 + i * p["_step"], "tick")
              for i in range(0, int(p["_total"]), 2)]
        ev.append((0.4 + int(p["_total"]) * p["_step"], "bell"))
    elif name == "wheel_progress":
        spin = p["_spin_dur"]
        ev = [(0.25 + spin * (k / 14.0) ** 1.6, "tick") for k in range(15)]
        ev.append((0.25 + spin, "fanfare"))
    elif name == "podium_steps":
        ev = [(0.35, "tick"), (0.7, "tick"), (1.05, "tick"),
              (1.55, "fanfare")]
    elif name == "show_end":
        ev = [(0.35, "sparkle"), (p["_click_at"], "fanfare"),
              (p["_click_at"] + 0.3, "bell")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)
