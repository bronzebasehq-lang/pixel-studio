#!/usr/bin/env python3
"""ZINE SCENES - dang ky 10 mau canh goi "zine" (cat dan tap chi).

Cung pattern registry: SPEC tham so -> UI tu sinh form; id canh
"zn:<key>", tpack="zine". Moi mau co tham so "layout" (bien the bo
cuc, "" = tu xoay).

SEED: bien the ruot cua goi - o dan xao font/mau/goc theo seed.
render.py goi set_shot_context(seed) truoc moi doan (seed = seed job
+ vi tri cau); _prep tron seed voi hash(mau + tham so) thanh p["_seed"]
-> cung job + cung tham so render lai ra DUNG to hop cu; job khac ra
to hop khac. Khong goi set_shot_context (preview/sample doc lap) thi
dung seed mac dinh on dinh.
"""
import hashlib
import math

import zine_templates as zt
from test01_scenes import scan_pacing  # noqa: F401

W, H = zt.W, zt.H

_SHOT_SEED = 20261027


def set_shot_context(seed):
    """render.py goi truoc moi doan render cua goi zine."""
    global _SHOT_SEED
    _SHOT_SEED = int(seed) & 0x7FFFFFFF


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


def _seed_for(key, p):
    blob = key + "|" + "|".join("%s=%s" % (k, p[k]) for k in sorted(p)
                                if not k.startswith("_"))
    h = int(hashlib.md5(blob.encode("utf-8")).hexdigest()[:8], 16)
    return (_SHOT_SEED * 1000003 + h) & 0x7FFFFFFF


# ------------------------------------------------------------------ prep
def _prep_verdict(p, dur):
    return {"_tag_at": min(1.3, max(0.7, dur * 0.35))}


def _prep_clipping(p, dur):
    lines = [x for x in p["lines"].split("|")]
    raw = [_clamp(len(x) * 0.026, 0.35, 1.0) for x in lines]
    budget = max(0.6, dur - 1.6)
    tot = sum(raw)
    if tot > budget:
        raw = [r * budget / tot for r in raw]
    starts, acc = [], 0.9
    for r in raw:
        starts.append((acc, acc + r))
        acc += r
    return {"_line_starts": starts}


def _prep_items(p, dur):
    items = [x.strip() for x in p["items"].split("|") if x.strip()]
    n = max(1, len(items))
    stagger = _clamp((dur - 1.2) / n, 0.25, 0.5)
    return {"_starts": [0.55 + i * stagger for i in range(n)]}


def _prep_counter(p, dur):
    return {"_target": _num(p["value"], 1298),
            "_count_dur": min(2.2, max(0.5, dur * 0.55))}


def _prep_grid(p, dur):
    total = max(1, int(_num(p["count"], 20)))
    cols = max(1, int(_num(p["cols"], 5)))
    step = _clamp((dur - 1.6) / total, 0.04, 0.12)
    return {"_total": total, "_cols": cols, "_step": step}


def _prep_progress(p, dur):
    fill = min(1.6, max(0.4, dur * 0.35))
    return {"_pct": _clamp(_num(p["pct"], 70), 0, 100),
            "_fill_dur": fill, "_t_lines": 0.3 + fill + 0.15}


def _prep_combo(p, dur):
    sx = int(_num(p["start_x"], 2))
    mx = int(_num(p["max_x"], 4))
    if mx < sx:
        mx = sx
    step = _clamp((dur - 1.5) / max(1, mx - sx), 0.3, 0.55) if mx > sx else 0.5
    return {"_start_x": sx, "_max_x": mx, "_step": step}


def _prep_follow(p, dur):
    return {"_click_at": min(2.4, max(1.5, dur * 0.55))}


_PREP = {"verdict_tag": _prep_verdict, "clipping_window": _prep_clipping,
         "pinned_list": _prep_items, "price_number": _prep_counter,
         "tile_grid": _prep_grid, "ruler_progress": _prep_progress,
         "stack_combo": _prep_combo, "poster_end": _prep_follow}


def _full_params(key, params, dur):
    info = TEMPLATES[key]
    p = _merged(info["params"], params)
    p["_layout"] = _layout_of(p)
    p["_seed"] = _seed_for(key, p)
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
_FX = _spec("fx", "Hiệu ứng (trống / tape = băng dính kéo ngang đầu shot / jitter = ô chữ rung, chỉ tile_hook)",
            "text", "")

TEMPLATES = {
    "tile_hook": {
        "name": "tile_hook — Móc ô chữ cắt dán",
        "desc": "Note xé ghim đỏ + headline xếp bằng ô cắt dán nhiều font/màu, mỗi từ 1 ô nghiêng khác nhau",
        "tags": "hook tile o chu cat dan mo dau cau hoi flop tap chi",
        "params": [
            _spec("note", "Chữ trên note xé", "text",
                  "video đăng hoài, không ai xem?"),
            _spec("head", "Headline ô chữ", "text",
                  "KHÔNG PHẢI DO THUẬT TOÁN ĐÂU!"),
            _spec("sub", "Dòng ô nhỏ dưới (trống = không)", "text", ""),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("tile_hook", zt.tile_hook),
    },
    "verdict_tag": {
        "name": "verdict_tag — Nhãn sao phán quyết",
        "desc": "Headline ô chữ + nhãn sao bung đỏ (kiểu nhãn giá) đóng vào kết luận",
        "tags": "verdict tag nhan sao phan quyet ket luan sai dung gia",
        "params": [
            _spec("head", "Headline ô chữ", "text", "HỎI SAI CÂU RỒI"),
            _spec("tag", "Chữ nhãn sao (2 dòng ngăn |)", "text", "SAI!|BÉT NHÈ"),
            _spec("sub", "Dòng ô nhỏ dưới (trống = không)", "text", ""),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("verdict_tag", zt.verdict_tag),
    },
    "clipping_window": {
        "name": "clipping_window — Mẩu báo demo",
        "desc": "Mẩu báo cắt dán có băng dính, tiêu đề ô chữ + dòng viết tay hiện dần",
        "tags": "clipping window mau bao demo cua so viet tay skill giai thich",
        "params": [
            _spec("title", "Tiêu đề ô chữ", "text", "VIẾT THÀNH SKILL"),
            _spec("lines", "Dòng viết tay trong mẩu báo (ngăn |)", "text",
                  "Đạo diễn, không phải máy nhắc chữ.|1. Đọc gu trước.|2. Khóa mốc nhịp.|3. Chữ chạy theo nhịp nói."),
            _spec("side", "Ô chữ phụ bên phải (biến thể 2)", "text", "ĐỌC KỸ"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("clipping_window", zt.clipping_window),
    },
    "ab_clippings": {
        "name": "ab_clippings — So sánh 2 mẩu dán",
        "desc": "Trái: mẩu dán xám mờ nhàm; phải: mẩu dán sống động; ô VS ở giữa",
        "tags": "ab clippings so sanh 2 mau dan vs trai phai before after",
        "params": [
            _spec("head", "Tiêu đề ô chữ", "text", "CÙNG MỘT AI"),
            _spec("label_a", "Nhãn mẩu trái", "text", "KHÔNG AI ĐẠO DIỄN"),
            _spec("label_b", "Nhãn mẩu phải", "text", "CÓ NGƯỜI ĐẠO DIỄN"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("ab_clippings", zt.ab_clippings),
    },
    "pinned_list": {
        "name": "pinned_list — Bảng ghim danh sách",
        "desc": "Bảng gỗ bần, các mẩu giấy ghim đỏ dán vào lần lượt kèm nhãn BƯỚC",
        "tags": "pinned list bang ghim danh sach cac buoc mau giay cong thuc",
        "params": [
            _spec("title", "Tiêu đề ô chữ", "text", "CÔNG THỨC GIỮ CHÂN"),
            _spec("items", "Mục (Nhãn::nội dung, ngăn |)", "text",
                  "BƯỚC 1::hook 3 giây đầu|BƯỚC 2::3 giây 1 biến cố|QUAN TRỌNG::kết mở kéo phần 2"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("pinned_list", zt.pinned_list),
    },
    "price_number": {
        "name": "price_number — Số thẻ giá",
        "desc": "Thẻ giá vàng khổ lớn có dây treo, số chạy tăng + nhãn sao bung đỏ",
        "tags": "price number so the gia vang lon chay tang so lieu nhan gia",
        "params": [
            _spec("value", "Số đích", "number", "1298"),
            _spec("label", "Nhãn ô chữ dưới thẻ", "text", "HIỆU ỨNG ÂM THANH"),
            _spec("burst", "Chữ nhãn sao (ngăn |)", "text", "ĐÃ|ĐẾM HẾT"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("price_number", zt.price_number),
    },
    "tile_grid": {
        "name": "tile_grid — Lưới ô dán",
        "desc": "Lưới ô cắt dán đánh số dán vào lần lượt, mỗi ô 1 font/màu khác nhau",
        "tags": "tile grid luoi o dan danh so phong cach cac o tap chi",
        "params": [
            _spec("title", "Tiêu đề ô chữ", "text", "PHONG CÁCH DỰNG SẴN"),
            _spec("count", "Tổng số ô", "number", "20"),
            _spec("cols", "Số cột", "number", "5"),
            _spec("caption", "Ô chữ chú thích (trống = không)", "text",
                  "CHỌN LÀ CHẠY"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("tile_grid", zt.tile_grid),
    },
    "ruler_progress": {
        "name": "ruler_progress — Dải thước tiến trình",
        "desc": "Dải giấy dài chia ô, ô màu dán chồng dần tới % đích + 3 dòng ô chữ lật câu hỏi",
        "tags": "ruler progress dai thuoc tien trinh phan tram o dan 70",
        "params": [
            _spec("pct", "Phần trăm đích", "number", "70"),
            _spec("line1", "Dòng 1", "text", "Hệ thống lo 70%"),
            _spec("question", "Câu hỏi lật", "text", "30% còn lại?"),
            _spec("answer", "Dòng trả lời", "text", "Là BẠN. Gu của BẠN."),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("ruler_progress", zt.ruler_progress),
    },
    "stack_combo": {
        "name": "stack_combo — Combo ô số dán chồng",
        "desc": "Ô ×2 ×3 ×4 dán chồng leo thang to dần + nhãn sao đỏ + dải năng lượng",
        "tags": "stack combo o so dan chong leo thang x2 x3 cang ve cuoi",
        "params": [
            _spec("start_x", "Bắt đầu (×)", "number", "2"),
            _spec("max_x", "Tối đa (×)", "number", "4"),
            _spec("burst", "Chữ nhãn sao (ngăn |)", "text",
                  "CÀNG VỀ CUỐI|CÀNG DÍCH"),
            _spec("caption", "Ô chữ chú thích (trống = không)", "text",
                  "MỖI Ý MỚI = +1 COMBO"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("stack_combo", zt.stack_combo),
    },
    "poster_end": {
        "name": "poster_end — Poster PHẦN 2",
        "desc": "Poster ô lớn dán tường bằng băng dính + nút THEO DÕI ô giấy, bấm xong hóa đen",
        "tags": "poster end man hinh cuoi phan 2 theo doi nut dan tuong",
        "params": [
            _spec("main", "Dòng ô chữ trên (trống = không)", "text",
                  "HẸN GẶP LẠI Ở"),
            _spec("big", "Chữ poster lớn", "text", "PHẦN 2"),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI"),
            _spec("done_text", "Chữ nút sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _spec("side", "Chữ cạnh nút (viết tay)", "text",
                  "dán tiếp tại đây"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("poster_end", zt.poster_end),
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
    img = zt.tear_in(img, tm)
    if "tape" in str(p.get("fx", "") or "").lower():
        # fx=tape: dai bang dinh keo ngang lau canh ngay sau xe giay
        img = zt.tape_wipe(img, tm)
    return img


def events_for(name, params, dur):
    p = _full_params(name, params, dur)
    ev = [(0.0, "tear")]
    if name == "tile_hook":
        ev += [(0.12, "pin"), (0.45, "paste"), (0.8, "paste"),
               (1.2, "paste"), (1.6, "paste")]
    elif name == "verdict_tag":
        ev += [(0.25, "paste"), (0.6, "paste"), (p["_tag_at"], "stamp")]
    elif name == "clipping_window":
        ev += [(0.15, "paste"), (0.35, "paste")]
        ev += [(s, "pop") for (s, _e) in p["_line_starts"]]
    elif name == "ab_clippings":
        ev += [(0.15, "paste"), (0.4, "paste"), (0.75, "paste"),
               (1.1, "pop")]
    elif name == "pinned_list":
        ev += [(s, "paste") for s in p["_starts"]]
        ev += [(s + 0.06, "pin") for s in p["_starts"]]
    elif name == "price_number":
        cd = p["_count_dur"]
        ev += [(0.2, "paste"), (0.5, "stamp")]
        ev += [(0.35 + cd * k / 8.0, "pop") for k in range(9)]
    elif name == "tile_grid":
        ev += [(0.45 + i * p["_step"], "paste")
               for i in range(0, int(p["_total"]), 4)]
    elif name == "ruler_progress":
        fill = p["_fill_dur"]
        ev += [(0.3 + fill * k / 4.0, "paste") for k in range(5)]
        tl = p["_t_lines"]
        ev += [(tl, "paste"), (tl + 0.55, "paste"), (tl + 1.10, "paste")]
    elif name == "stack_combo":
        sx, mx, step = p["_start_x"], p["_max_x"], p["_step"]
        for i, n in enumerate(range(sx, mx + 1)):
            ev.append((0.35 + i * step, "paste"))
        ev.append((0.35 + (mx - sx) * step + 0.15, "stamp"))
    elif name == "poster_end":
        ev += [(0.25, "paste"), (0.3, "paste"), (0.8, "paste"),
               (p["_click_at"], "pin")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)
