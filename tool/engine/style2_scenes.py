#!/usr/bin/env python3
"""STYLE2 SCENES - dang ky 8 template style2 thanh MAU CANH THAT cua tool (V2.3).

Moi template co SPEC tham so (key / nhan / kieu / mac dinh = so lieu mau
Nokia cua ban goc, de render mac dinh khop GIF xem truoc cu). UI (server.py)
tu sinh form sua tham so tren the cau tu SPEC nay; params luu theo cau va
di kem payload render.

Tham so chung cho moi template (xu ly o draw_template):
  typed : {on, text} - CHU CHAY go tung ky tu kieu style2 (helper
          draw_typed cua style2_templates), mac dinh lay chu cua cau,
          tat duoc hoac ghi de bang o chu rieng. Khi typed BAT, shot
          template KHONG ve phu de tinh nua (chu chay dong vai phu de,
          dung nhu video Nokia goc).
  popup : {on, text} - CAPTION POP-UP chu lon vang giua man hinh,
          pop-in trong ~1.2s dau shot, phu len tren media.

API:
  TEMPLATES            : dict key -> {name, desc, tags, params, build}
  template_catalog()   : ban JSON-safe (khong co ham build) cho UI
  draw_template(name, params, tm, dur, text, typed, popup) -> RGBA 1920x1080
"""
import math

from PIL import Image, ImageDraw, ImageFont

import style2_templates as s2
from painter import clamp, ease_out_cubic

W, H = s2.W, s2.H
POP_YELLOW = (255, 216, 79, 255)


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


# ------------------------------------------------------------------ builders
# Moi builder nhan (params_da_merge, ctx) -> fn(t, dur) -> RGBA 1920x1080.
# ctx = {"text": chu cua cau}. Cac moc thoi gian dai (at/grow/t_lines...)
# duoc co theo dur ben trong fn de shot ngan van hien du noi dung.

def _build_counter(p, ctx):
    target = int(_num(p["value"], 126000000))
    fmt = "{:,}" + p["suffix"]
    label = p["label"]

    def fn(t, dur):
        return s2.counter(t, dur, label=label, target=target, fmt=fmt,
                          count_dur=min(1.3, max(0.4, dur * 0.45)))
    return fn


def _build_chart(p, ctx):
    vals = []
    for chunk in p["points"].split(","):
        chunk = chunk.strip()
        if chunk:
            vals.append(clamp(_num(chunk, 0.0), 0.0, 100.0))
    if not vals:
        vals = [85.0, 78.0, 62.0, 42.0, 20.0, 8.0]
    if len(vals) == 1:
        vals = vals * 2
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = 220 + (1700 - 220) * (i / float(n - 1))
        y = 830 - (v / 100.0) * 680
        pts.append((int(x), int(y)))
    title = p["title"].strip() or None
    end_label = p["labels"].strip() or None

    def fn(t, dur):
        return s2.chart(t, dur, points=pts, col=s2.RED, title=title,
                        end_label=end_label)
    return fn


def _build_price_bars(p, ctx):
    title = p["title"].strip() or None
    b1 = {"label": p["bar1_label"], "value_text": p["bar1_text"],
          "frac": clamp(_num(p["bar1_pct"], 15) / 100.0, 0.0, 1.0),
          "col": s2.YEL}
    b2 = {"label": p["bar2_label"], "value_text": p["bar2_text"],
          "frac": clamp(_num(p["bar2_pct"], 100) / 100.0, 0.0, 1.0),
          "col": s2.TEAL}

    def fn(t, dur):
        bars = [dict(b1, at=0.2, grow=min(1.6, max(0.5, dur * 0.3))),
                dict(b2, at=min(2.2, dur * 0.42),
                     grow=min(3.0, max(0.6, dur * 0.45)))]
        return s2.price_bars(t, dur, bars=bars, title=title)
    return fn


def _build_death_spiral(p, ctx):
    items = [x.strip() for x in p["items"].split(",") if x.strip()]
    label_a = items[0] if len(items) > 0 else "NO APPS"
    label_b = items[1] if len(items) > 1 else "NO USERS"
    caption = p["title"]

    def fn(t, dur):
        ca = min(2.0, dur * 0.55) if caption else None
        return s2.death_spiral(t, dur, label_a=label_a, label_b=label_b,
                               caption=caption, caption_at=ca)
    return fn


def _build_quote_card(p, ctx):
    """Ban quote_card viet lai day noi (dung helper typed_ps/chunks_timing
    cua style2_templates) de moc thoi gian dong khong phu thuoc caption —
    nho vay cong tac CHU CHAY chung cua tool ap dung duoc nhu moi
    template khac. Ban goc quote_card() trong module van giu nguyen."""
    attrib = p["author"]
    quote = p["quote"].strip()
    anchor = (ctx.get("text") or "").strip() or quote

    def fn(t, dur):
        tim = s2.chunks_timing([anchor], dur)
        img = Image.new("RGBA", (W, H), (8, 10, 22, 255))
        d = ImageDraw.Draw(img)
        if attrib:
            d.text((120, 110), attrib,
                   font=ImageFont.truetype(s2.PS, 26), fill=(150, 160, 190))
        if quote:
            words = quote.split()
            if len(quote) <= 46 or len(words) < 4:
                lines = [(quote, 430, 38, 0.3)]
            else:
                best, bi = None, 1
                for i in range(1, len(words)):
                    a, b = " ".join(words[:i]), " ".join(words[i:])
                    sc = abs(len(a) - len(b))
                    if best is None or sc < best:
                        best, bi = sc, i
                lines = [(" ".join(words[:bi]), 400, 34, 0.3),
                         (" ".join(words[bi:]), 472, 34, 0.9)]
            t0 = tim[0][0]
            for (txt, y, size, delay) in lines:
                start = t0 + delay
                if t >= start:
                    s2.typed_ps(img, txt, 0, y, size, t, start,
                                start + max(0.8, len(txt) * 0.045),
                                col=s2.WHITE, center=True)
        return img
    return fn


def _build_definition_card(p, ctx):
    parts = [x.strip() for x in p["lines"].split("|")]
    line1 = parts[0] if len(parts) > 0 else ""
    line2 = parts[1] if len(parts) > 1 else ""
    term = p["term"]

    def fn(t, dur):
        return s2.definition_card(t, dur, title=term, line1=line1,
                                  line2=line2,
                                  t_lines=min(1.5, max(0.3, dur * 0.3)))
    return fn


def _build_game_over(p, ctx):
    main = p["main"]
    sub = p["sub"].strip()

    def fn(t, dur):
        img = s2.game_over(t, dur, text=main)
        if sub and t >= 1.2:
            s2.typed_ps(img, sub, 0, 640, 26, t, 1.2, 2.2,
                        col=s2.GREY, center=True)
        return img
    return fn


def _build_end_card(p, ctx):
    main = p["main"]
    sub = p["sub"].strip()

    def fn(t, dur):
        img = s2.end_card(t, dur, text=main)
        if sub and t >= 1.0:
            s2.typed_ps(img, sub, 0, 600, 22, t, 1.0, 2.0,
                        col=s2.GREY, center=True)
        return img
    return fn


# ------------------------------------------------------------------ registry
def _spec(key, label, typ, default):
    return {"key": key, "label": label, "type": typ, "def": default}


TEMPLATES = {
    "counter": {
        "name": "counter — Bộ đếm số chạy",
        "desc": "Số chạy từ 0 lên số đích trong hộp panel",
        "tags": "counter bo dem so chay tien doanh thu so luong count up number",
        "params": [
            _spec("label", "Nhãn (chữ trước số)", "text", "SOLD:"),
            _spec("value", "Số đích", "number", "126000000"),
            _spec("suffix", "Hậu tố sau số (vd: +)", "text", ""),
        ],
        "build": _build_counter,
    },
    "chart": {
        "name": "chart — Biểu đồ đường",
        "desc": "Đường vẽ dần qua các điểm số (100 = đỉnh, 0 = đáy)",
        "tags": "chart bieu do duong tang truong lao doc sup do line growth collapse",
        "params": [
            _spec("title", "Tiêu đề (để trống = không)", "text", ""),
            _spec("points", "Các điểm 0–100 (cách nhau dấu phẩy)", "text",
                  "85, 78, 62, 42, 20, 8"),
            _spec("labels", "Nhãn đóng dấu ở cuối (để trống = không)",
                  "text", ""),
        ],
        "build": _build_chart,
    },
    "price_bars": {
        "name": "price_bars — Thanh giá so sánh",
        "desc": "2 thanh ngang so sánh độ lớn, lớn dần theo thời gian",
        "tags": "price bars thanh gia so sanh gia ban doanh thu comparison",
        "params": [
            _spec("title", "Tiêu đề", "text", "THE PRICE"),
            _spec("bar1_label", "Thanh 1 — nhãn", "text", ""),
            _spec("bar1_text", "Thanh 1 — chữ giá trị", "text",
                  "EUR 5.44 BILLION"),
            _spec("bar1_pct", "Thanh 1 — độ dài %", "number", "15"),
            _spec("bar2_label", "Thanh 2 — nhãn", "text",
                  "REVENUE IN 2007 ALONE:"),
            _spec("bar2_text", "Thanh 2 — chữ giá trị", "text",
                  "EUR 51 BILLION"),
            _spec("bar2_pct", "Thanh 2 — độ dài %", "number", "100"),
        ],
        "build": _build_price_bars,
    },
    "death_spiral": {
        "name": "death_spiral — Vòng xoáy chết",
        "desc": "Vòng chấm xoay + 2 nhãn đối nhau + chú thích kết",
        "tags": "death spiral vong xoay chet no apps no users loop vong lap",
        "params": [
            _spec("title", "Chú thích kết (dưới vòng)", "text",
                  "A DEATH SPIRAL"),
            _spec("items", "2 nhãn đối nhau (cách nhau dấu phẩy)", "text",
                  "NO APPS, NO USERS"),
        ],
        "build": _build_death_spiral,
    },
    "quote_card": {
        "name": "quote_card — Thẻ trích dẫn",
        "desc": "Câu trích dẫn gõ từng ký tự giữa màn hình",
        "tags": "quote card the trich dan cau noi memo burning platform",
        "params": [
            _spec("quote", "Câu trích dẫn", "text",
                  "WE ARE STANDING ON A BURNING PLATFORM"),
            _spec("author", "Nguồn / tác giả (góc trên trái)", "text",
                  "CEO MEMO, 2011"),
        ],
        "build": _build_quote_card,
    },
    "definition_card": {
        "name": "definition_card — Thẻ định nghĩa",
        "desc": "Thuật ngữ vàng + 2 dòng giải thích",
        "tags": "definition card the dinh nghia giai thich thuat ngu osborne effect",
        "params": [
            _spec("term", "Thuật ngữ", "text", "THE OSBORNE EFFECT"),
            _spec("lines", "2 dòng giải thích (ngăn cách bằng |)", "text",
                  "ANNOUNCE THE FUTURE TOO EARLY -|KILL THE PRESENT "
                  "BEFORE IT ARRIVES"),
        ],
        "build": _build_definition_card,
    },
    "game_over": {
        "name": "game_over — Màn GAME OVER",
        "desc": "Màn đen + chữ lớn gõ từng ký tự ở giữa",
        "tags": "game over man ket thuc thua end screen",
        "params": [
            _spec("main", "Chữ chính", "text", "GAME OVER."),
            _spec("sub", "Chữ phụ dưới (để trống = không)", "text", ""),
        ],
        "build": _build_game_over,
    },
    "end_card": {
        "name": "end_card — Thẻ kết kênh",
        "desc": "Thẻ kết: tên kênh gõ chữ ở giữa màn đen",
        "tags": "end card the ket thuc logo kenh outro 16bit_exe",
        "params": [
            _spec("main", "Chữ chính", "text", "16BIT_EXE"),
            _spec("sub", "Chữ phụ dưới (để trống = không)", "text", ""),
        ],
        "build": _build_end_card,
    },
}


def template_catalog():
    """Danh muc JSON-safe cho UI: id, ten, nhom tu khoa + SPEC tham so."""
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


# ------------------------------------------------------------------ ve frame
def _draw_popup(img, text, tm):
    """Caption pop-up: chu lon vang giua man hinh, pop-in ~1.2s dau shot."""
    if tm < 0.05 or tm > 1.25 or not text:
        return
    p = clamp((tm - 0.05) / 0.35)
    scale = (0.5 + 0.5 * ease_out_cubic(p)) * (1.0 + 0.08 * math.sin(p * math.pi))
    size, lines = s2.layout_big(text, max_size=118)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(s2.VT, size)
    y0 = (H - size * len(lines)) // 2
    for j, ln in enumerate(lines):
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y0 + j * size), ln, font=f, fill=POP_YELLOW,
               stroke_width=6, stroke_fill=(0, 0, 0, 255))
    if scale != 1.0:
        nw, nh = max(2, int(W * scale)), max(2, int(H * scale))
        lay = lay.resize((nw, nh), Image.NEAREST)
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(lay, ((W - nw) // 2, (H - nh) // 2))
        lay = out
    img.alpha_composite(lay)


def typed_enabled(typed):
    """typed=None -> mac dinh BAT (dung nhu spec V2.3)."""
    if typed is None:
        return True
    return bool(typed.get("on", True))


def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    """Ve 1 frame template tai thoi diem tm (giay) cua shot dai dur (giay).

    Tra RGBA 1920x1080. Ap dung tham so chung: chu chay + caption pop-up.
    """
    info = TEMPLATES[name]
    p = _merged(info["params"], params)
    fn = info["build"](p, {"text": text})
    img = fn(tm, dur)
    if typed_enabled(typed):
        tt = ""
        if isinstance(typed, dict):
            tt = (typed.get("text") or "").strip()
        if not tt:
            tt = (text or "").strip()
        if tt:
            s2.draw_typed(img, tt, tm, 0.12, max(0.45, dur - 0.35))
    if isinstance(popup, dict) and popup.get("on"):
        pt = (popup.get("text") or "").strip() or (text or "").strip()
        if pt:
            _draw_popup(img, pt, tm)
    return img
