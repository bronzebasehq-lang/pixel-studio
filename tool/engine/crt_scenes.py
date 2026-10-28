#!/usr/bin/env python3
"""CRT SCENES - dang ky 11 mau canh goi "crt" (terminal co).

Cung pattern voi test01_scenes/style2_scenes: moi template co SPEC tham
so, UI tu sinh form; params luu theo cau, id canh trong UI "ct:<key>",
truong tpack="crt" o payload. Moi mau co tham so "layout" (bien the
bo cuc): "" = tu xoay o lop render (packs.resolve_layout), "1"/"2" =
chon tay. draw_template doc layout -> p["_layout"] (0/1).

events_for() phuc vu BO QUET NHIP dung chung (scan_pacing cua
test01_scenes) va lop SFX cua video mau.
"""
import math

import crt_templates as ct
from test01_scenes import scan_pacing  # noqa: F401  (dung chung 1 ban quet)

W, H = ct.W, ct.H


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
def _prep_log(p, dur):
    lines = [x for x in p["lines"].split("|")]
    n = max(1, len(lines))
    stagger = _clamp((dur - 1.2) / n, 0.25, 0.55)
    return {"_starts": [0.45 + i * stagger for i in range(n)],
            "_pct": _clamp(_num(p.get("pct", 72), 72), 0, 100)}


def _prep_odometer(p, dur):
    return {"_target": _num(p["value"], 1298),
            "_count_dur": min(2.2, max(0.5, dur * 0.55))}


def _prep_grid(p, dur):
    total = max(1, int(_num(p["count"], 6)))
    cols = max(1, int(_num(p["cols"], 3)))
    step = _clamp((dur - 1.6) / total, 0.12, 0.4)
    return {"_total": total, "_cols": cols, "_step": step}


def _prep_progress(p, dur):
    fill = min(1.6, max(0.4, dur * 0.35))
    return {"_pct": _clamp(_num(p["pct"], 72), 0, 100),
            "_fill_dur": fill, "_t_lines": 0.3 + fill + 0.15}


def _prep_overclock(p, dur):
    sx = int(_num(p["start_x"], 2))
    mx = int(_num(p["max_x"], 4))
    if mx < sx:
        mx = sx
    step = _clamp((dur - 1.6) / max(1, mx - sx), 0.35, 0.7) if mx > sx else 0.6
    return {"_start_x": sx, "_max_x": mx, "_step": step}


def _prep_follow(p, dur):
    return {"_click_at": min(2.6, max(1.6, dur * 0.55))}


_PREP = {"log_window": _prep_log, "log_list": _prep_log,
         "odometer": _prep_odometer, "process_grid": _prep_grid,
         "progress_blocks": _prep_progress, "overclock": _prep_overclock,
         "follow_end": _prep_follow}


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
_FX = _spec("fx", "Hiệu ứng (trống / static = nhiễu mất sóng đầu+cuối shot)",
            "text", "")

TEMPLATES = {
    "decode_hook": {
        "name": "decode_hook — Móc giải mã",
        "desc": "Dòng lệnh gõ ra + headline scramble từng ký tự về chữ thật, thanh GIẢI MÃ %",
        "tags": "hook giai ma scramble decode lenh command mo dau flop cau hoi",
        "params": [
            _spec("cmd", "Dòng lệnh (không dấu)", "text",
                  "tai_sao_video_cua_ban_FLOP?"),
            _spec("head", "Headline giải mã (có dấu)", "text",
                  "KHÔNG PHẢI DO THUẬT TOÁN."),
            _spec("sub", "Dòng phụ (không dấu, trống = không)", "text",
                  "dang giai ma nguyen nhan ..."),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("decode_hook", ct.decode_hook),
    },
    "log_window": {
        "name": "log_window — Cửa sổ log",
        "desc": "Cửa sổ terminal: dòng log [OK]/[..] kèm mốc giờ hiện dần + thanh khối %",
        "tags": "log window cua so nhat ky kiem tra ok chay tien trinh he thong",
        "params": [
            _spec("title", "Tên cửa sổ (không dấu)", "text",
                  "NHAT_KY_GIU_NGUOI_XEM.LOG"),
            _spec("lines", "Dòng log (giờ::nội dung, ngăn |)", "text",
                  "00:01::hook 3 giay dau|00:04::moi 3 giay 1 bien co|00:07::giu nguoi xem den cuoi"),
            _spec("statuses", "Trạng thái từng dòng (OK/RUN/X, cách ,)", "text",
                  "OK,OK,RUN"),
            _spec("pct", "Phần trăm cuối thanh", "number", "72"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("log_window", ct.log_window),
    },
    "glow_headline": {
        "name": "glow_headline — Headline phát sáng",
        "desc": "Chữ lớn phát sáng giữa màn + dòng phụ gõ chữ + khung HUD 4 góc",
        "tags": "headline phat sang glow chu lon ket luan thong diep chinh",
        "params": [
            _spec("small", "Dòng nhỏ trên", "text", "KẾT QUẢ PHÂN TÍCH:"),
            _spec("big", "Dòng lớn 1 (xanh)", "text", "NHỊP MỚI LÀ"),
            _spec("big2", "Dòng lớn 2 (nhấn, trống = không)", "text",
                  "THUẬT TOÁN."),
            _spec("big2_col", "Màu dòng 2 (amber/red/green)", "text", "amber"),
            _spec("sub", "Dòng phụ gõ chữ dưới", "text",
                  "> cung mot AI - khac nguoi dao dien"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("glow_headline", ct.glow_headline),
    },
    "ab_windows": {
        "name": "ab_windows — So sánh 2 cửa sổ",
        "desc": "Trái: cửa sổ mờ NO SIGNAL; phải: cửa sổ sáng chạy nội dung; huy hiệu VS",
        "tags": "ab windows so sanh 2 cua so vs trai phai before after khac biet",
        "params": [
            _spec("head", "Tiêu đề trên", "text", "CÙNG MỘT HỆ THỐNG"),
            _spec("title_a", "Tên cửa sổ trái", "text", "BAN_CU.EXE"),
            _spec("title_b", "Tên cửa sổ phải", "text", "BAN_MOI.EXE"),
            _spec("label_a", "Nhãn trái", "text", "KHÔNG NHỊP"),
            _spec("label_b", "Nhãn phải", "text", "CÓ NHỊP GIỮ CHÂN"),
            _spec("lines_b", "Dòng nội dung phải (ngăn |)", "text",
                  "hook: 3 giay|bien co: moi 3 giay|moc treo: mo som|ket: phan 2"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("ab_windows", ct.ab_windows),
    },
    "log_list": {
        "name": "log_list — Danh sách log",
        "desc": "Danh sách [OK]/[..] hiện dần toàn khung, mở đầu bằng dòng lệnh",
        "tags": "log list danh sach kiem tra cac muc ok cong thuc thanh phan",
        "params": [
            _spec("cmd", "Dòng lệnh mở đầu (không dấu)", "text",
                  "chay kiem_tra_giu_chan(video.mp4)"),
            _spec("lines", "Mục (giờ::nội dung, ngăn |)", "text",
                  "00:01::hook 3 giay dau|00:04::moi 3 giay 1 bien co|00:07::giu nguoi xem den cuoi"),
            _spec("statuses", "Trạng thái từng dòng (cách ,)", "text",
                  "OK,OK,RUN"),
            _spec("pct", "(không dùng)", "number", "72"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("log_list", ct.log_list),
    },
    "odometer": {
        "name": "odometer — Số odometer",
        "desc": "Số mono chạy tăng kiểu đồng hồ cơ, chữ số cuối loan tới khi dừng + thước tick",
        "tags": "odometer so lon chay tang dem so lieu thong ke dong ho",
        "params": [
            _spec("value", "Số đích", "number", "1298"),
            _spec("label", "Nhãn dưới số", "text", "HIỆU ỨNG ÂM THANH"),
            _spec("label_col", "Màu nhãn (amber/red/green)", "text", "amber"),
            _spec("sub", "Dòng phụ (trống = không)", "text", ""),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("odometer", ct.odometer),
    },
    "process_grid": {
        "name": "process_grid — Lưới tiến trình",
        "desc": "Lưới ô tiến trình PID sáng dần, mỗi ô có thanh chạy riêng",
        "tags": "process grid luoi tien trinh pid o he thong chay ngam modules",
        "params": [
            _spec("title", "Tiêu đề", "text", "HỆ THỐNG ĐANG CHẠY:"),
            _spec("count", "Tổng số ô", "number", "6"),
            _spec("cols", "Số cột", "number", "3"),
            _spec("caption", "Chú thích dưới (trống = không)", "text",
                  "6 tien trinh - tat ca deu phuc vu nhip giu chan"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("process_grid", ct.process_grid),
    },
    "progress_blocks": {
        "name": "progress_blocks — Thanh khối / thanh nhiệt",
        "desc": "Thanh [████░░] chạy % rồi lật câu hỏi; biến thể style=heat là thanh nhiệt",
        "tags": "progress blocks thanh khoi phan tram nhiet heat tien trinh 72",
        "params": [
            _spec("style", "Kiểu thanh (blocks / heat)", "text", "blocks"),
            _spec("pct", "Phần trăm đích", "number", "72"),
            _spec("line1", "Dòng 1 (gõ chữ)", "text",
                  "He thong lo 72% ..."),
            _spec("question", "Câu hỏi lật (gõ chữ)", "text",
                  "28% con lai la gi?"),
            _spec("question_col", "Màu câu hỏi (amber/red/green)", "text",
                  "amber"),
            _spec("answer", "Dòng trả lời (gõ chữ)", "text",
                  "LA BAN. Y TUONG CUA BAN."),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("progress_blocks", ct.progress_blocks),
    },
    "overclock": {
        "name": "overclock — Overclock leo thang",
        "desc": "OVERCLOCK ×2 ×3... + bảng thông số + thanh nhiệt tăng dần + cảnh báo đỏ",
        "tags": "overclock leo thang x2 x3 nhiet do toc do tang dan kich tran",
        "params": [
            _spec("cmd", "Dòng lệnh (không dấu)", "text",
                  "kich hoat che do OVERCLOCK"),
            _spec("start_x", "Bắt đầu (×)", "number", "2"),
            _spec("max_x", "Tối đa (×)", "number", "4"),
            _spec("specs", "Thông số (nhãn::giá trị, ngăn |)", "text",
                  "toc do cat canh::+240%|bien co moi::2.5 giay|do tre chuyen canh::0 khung hinh"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("overclock", ct.overclock),
    },
    "follow_end": {
        "name": "follow_end — Màn hình cuối terminal",
        "desc": "2 dòng chốt phát sáng + dòng follow gõ chữ + nút bấm chuyển [OK] ĐÃ THEO DÕI",
        "tags": "follow end man hinh cuoi theo doi enter ket thuc phan 2 subscribe",
        "params": [
            _spec("main", "Dòng chốt 1", "text", "Phần khó đã có hệ thống lo."),
            _spec("sub", "Dòng chốt 2", "text", "Việc của bạn chỉ là BẮT ĐẦU."),
            _spec("prompt", "Dòng lệnh follow (không dấu)", "text",
                  "follow de xem phan 2"),
            _spec("button", "Chữ nút trước khi bấm", "text", "THEO DÕI [ENTER]"),
            _spec("done_text", "Chữ sau khi bấm", "text", "ĐÃ THEO DÕI"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("follow_end", ct.follow_end),
    },
    "alert_warn": {
        "name": "alert_warn — Cảnh báo đỏ",
        "desc": "Khung viền đỏ nhấp nháy + sọc hazard + headline cảnh báo + dòng [!] (mẫu mới)",
        "tags": "alert warn canh bao do nhap nhay nguy hiem loi bao dong alarm",
        "params": [
            _spec("head", "Headline cảnh báo (có dấu)", "text",
                  "CẢNH BÁO: SẮP HẾT THỜI GIAN"),
            _spec("sub", "Dòng phụ gõ chữ (không dấu)", "text",
                  "he thong phat hien rui ro ..."),
            _spec("lines", "Dòng cảnh báo (ngăn |)", "text",
                  "nhip video qua cham|hook qua yeu|khong co moc treo"),
            _FX,
            _LAYOUT,
        ],
        "build": _builder("alert_warn", ct.alert_warn),
    },
}

VARIANTS = {k: 2 for k in TEMPLATES}


def template_catalog():
    return [{"key": k, "name": v["name"], "desc": v["desc"],
             "tags": v["tags"], "params": v["params"]}
            for k, v in TEMPLATES.items()]


def draw_template(name, params, tm, dur, text, typed=None, popup=None):
    """Ve 1 frame CRT tai tm. Dau shot co giat cat ngang 0.14s.
    fx=static (tuy chon): them nhieu mat song o dau + cuoi shot."""
    p = _full_params(name, params, dur)
    fn = TEMPLATES[name]["build"](p, {"text": text})
    img = fn(tm, dur)
    if tm < 0.14:
        img = ct.fx_glitch_cut(img, tm, 0.0, 0.14)
    if str(p.get("fx", "") or "").strip().lower() == "static":
        img = ct.fx_static(img, tm, dur)
    return img


# ------------------------------------------------------------------ su kien
def events_for(name, params, dur):
    p = _full_params(name, params, dur)
    ev = []
    if name == "decode_hook":
        ev = [(0.15, "type"), (0.55, "scan"), (1.0, "beep"), (1.8, "beep_hi")]
    elif name in ("log_window", "log_list"):
        ev = [(0.12, "type")] + [(s, "beep") for s in p["_starts"]]
        ev.append((0.4, "tick"))
    elif name == "glow_headline":
        ev = [(0.1, "beep"), (0.55, "beep_hi"), (1.0, "type")]
    elif name == "ab_windows":
        ev = [(0.1, "beep"), (0.35, "type"), (0.75, "beep"),
              (1.05, "beep_hi"), (1.3, "beep")]
    elif name == "odometer":
        cd = p["_count_dur"]
        ev = [(0.25 + cd * k / 8.0, "tick") for k in range(9)]
        ev.append((0.25 + cd, "beep_hi"))
    elif name == "process_grid":
        ev = [(0.1, "type")]
        ev += [(0.45 + i * p["_step"], "beep")
               for i in range(int(p["_total"]))]
    elif name == "progress_blocks":
        fill = p["_fill_dur"]
        ev = [(0.3 + fill * k / 4.0, "tick") for k in range(5)]
        tl = p["_t_lines"]
        ev += [(tl, "type"), (tl + 0.55, "beep"), (tl + 1.10, "beep_hi")]
    elif name == "overclock":
        sx, mx, step = p["_start_x"], p["_max_x"], p["_step"]
        for i, n in enumerate(range(sx, mx + 1)):
            at = 0.4 + i * step
            ev += [(at, "beep_hi"), (at, "tick")]
        ev.append((0.4 + (mx - sx) * step + 0.2, "alarm"))
    elif name == "follow_end":
        ev = [(0.15, "beep"), (0.9, "type"), (p["_click_at"], "enter")]
    elif name == "alert_warn":
        ev = [(0.1, "alarm"), (0.7, "type"), (1.1, "alarm"),
              (1.5, "beep"), (1.9, "beep"), (2.3, "alarm")]
    ev = [(round(o, 3), k) for (o, k) in ev if o <= dur]
    return sorted(ev)
