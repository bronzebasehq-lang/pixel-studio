#!/usr/bin/env python3
"""PACKS - dang ky trung tam 5 GOI PHONG CACH cua Pixel Studio (V2.4).

5 goi:
  pixel : PIXEL 16-BIT - canh code scenes.py (id 1..8) + template style2
          (id "s2:<key>"). Day la goi goc: job cu thuoc goi nay giu
          nguyen hanh vi 100% (khong tiem bien the, khong doi dispatch).
  stage : STAGE (ten cu "test01", kinetic giu chan) - id "t1:<key>",
          module test01_scenes. Alias "test01" van duoc chap nhan o
          moi lop (payload cu, job cu) -> normalize thanh "stage".
  crt   : CRT - terminal xanh la, id "ct:<key>", module crt_scenes.
  paper : PAPER - giay & muc, id "pp:<key>", module paper_scenes.
  zine  : ZINE - cat dan tap chi, id "zn:<key>", module zine_scenes.

Chiu trach nhiem:
  - module_for(pack): module scenes cua goi template (draw_template /
    events_for / TEMPLATES / VARIANTS dong nhat chu ky voi style2/test01).
  - LOP BIEN THE (spec V2.4 muc 5): moi mau cua 4 goi template co tham
    so "layout" ("" = tu xoay, "1"/"2"/"3" = chon tay). resolve_layout()
    quyet dinh bien the thuc te theo vi tri cau + seed cua job:
    cung job render lai = cung ket qua, job khac = to hop khac.
  - scan_duplicates(): canh bao trung khuon (1 mau dung >2 lan trong
    1 video, hoac 1 bien the cua 1 mau lap >3 lan) - ghi vao log render
    canh ket qua quet nhip.
  - suggest(): tu gan canh cho cac goi template (khop tu khoa trong
    tags/ten mau voi noi dung cau, bo dau tieng Viet; thua thi xoay
    vong theo thu tu vai tro, tranh lap mau lien tiep).
"""
import hashlib
import unicodedata

import crt_scenes
import paper_scenes
import style2_scenes as s2s_mod
import test01_scenes as stage_mod
import zine_scenes

# ------------------------------------------------------------------ registry
PACKS = [
    {"id": "pixel", "label": "PIXEL 16-BIT", "prefix": None,
     "desc": "Cảnh pixel 16-bit vẽ bằng code + template số liệu Style2 "
             "(gói gốc của kênh 16bit_exe).",
     "color": "#584ca8"},
    {"id": "stage", "label": "STAGE", "prefix": "t1:",
     "desc": "Kinetic giữ chân: sân khấu gỗ, chữ lớn nảy nhịp, đóng dấu, "
             "combo lên cấp (tên cũ: test01).",
     "color": "#e8442e"},
    {"id": "crt", "label": "CRT", "prefix": "ct:",
     "desc": "Terminal máy tính cổ: chữ xanh lá phát sáng, giải mã "
             "scramble, dòng log, thanh khối, overclock.",
     "color": "#33ff66"},
    {"id": "paper", "label": "PAPER", "prefix": "pp:",
     "desc": "Giấy & mực viết tay: nền sáng, note dán, quẹt dạ quang, "
             "khoanh đỏ, tem mực, checklist tích tay.",
     "color": "#f5c542"},
    {"id": "zine", "label": "ZINE", "prefix": "zn:",
     "desc": "Cắt dán tạp chí: mỗi từ 1 ô giấy cắt, font/màu/góc xáo "
             "theo từng video, tem nhãn giá, poster phần 2.",
     "color": "#ffc800"},
]

ALIASES = {"test01": "stage"}
TEMPLATE_MODULES = {
    "style2": s2s_mod,
    "stage": stage_mod,
    "crt": crt_scenes,
    "paper": paper_scenes,
    "zine": zine_scenes,
}
# goi co lop bien the bo cuc (pixel co y KHONG co - giu nguyen job cu)
VARIANT_PACKS = ("stage", "crt", "paper", "zine")

_PREFIX_TO_PACK = {"s2:": "style2", "t1:": "stage", "ct:": "crt",
                   "pp:": "paper", "zn:": "zine"}


def normalize_pack(pack):
    """'test01' -> 'stage'; None/la -> None."""
    if not pack:
        return None
    p = str(pack).strip().lower()
    return ALIASES.get(p, p)


def module_for(pack):
    """Module scenes cua 1 goi template (da normalize). None neu la pixel."""
    return TEMPLATE_MODULES.get(normalize_pack(pack) or "")


def job_pack_of(item_pack):
    """Anh xa pack cap cau (tpack) -> pack cap job: style2 thuoc pixel."""
    p = normalize_pack(item_pack)
    if p in ("style2", "pixel", None):
        return "pixel"
    return p


def pack_of_scene_id(scene_id):
    """Id canh trong UI -> pack cap job: so nguyen/s2: -> pixel,
    t1: -> stage, ct:/pp:/zn: -> goi tuong ung. Khong ro -> None."""
    if scene_id is None:
        return None
    s = str(scene_id)
    for pre, pk in _PREFIX_TO_PACK.items():
        if s.startswith(pre):
            return job_pack_of(pk)
    if s.lstrip("-").isdigit():
        return "pixel"
    return None


# ------------------------------------------------------------------ bien the
def variant_count(pack, key):
    mod = module_for(pack)
    if mod is None:
        return 1
    return int(getattr(mod, "VARIANTS", {}).get(key, 1))


def resolve_layout(pack, key, tparams, shot_index, job_seed):
    """Tra (layout_int_0based, nguon) cho 1 canh.

    Nguon "tay" neu nguoi dung da ghi tham so layout = "1"/"2"/"3"
    (khong phai "" / "auto" / "0"); nguoc lai "tu xoay": bien the =
    (job_seed + shot_index + hash(mau)) % so bien the -> on dinh cho
    cung 1 job, khac nhau giua cac job va giua cac vi tri cau.
    """
    n = variant_count(pack, key)
    raw = ""
    if isinstance(tparams, dict):
        raw = str(tparams.get("layout", "") or "").strip().lower()
    if raw not in ("", "auto", "0"):
        try:
            v = int(float(raw)) - 1
        except ValueError:
            v = -1
        if 0 <= v < n:
            return v, "tay"
    h = int(hashlib.md5(("%s:%s" % (pack, key)).encode("utf-8")
                        ).hexdigest()[:6], 16)
    return (int(job_seed) + int(shot_index) + h) % n, "tu xoay"


def job_seed_of(texts):
    """Seed cua job: crc cua toan bo kich ban (on dinh, khong phu thuoc
    thoi gian) - dung cho bien the + xao o ZINE."""
    import zlib
    blob = "\n".join(str(t) for t in texts).encode("utf-8")
    return zlib.crc32(blob) & 0xFFFFFFFF


# ------------------------------------------------------------------ quet trung
def scan_duplicates(shots):
    """Canh bao trung khuon. shots = [{pack, name, layout}] (layout =
    so nguyen 0-based hoac None neu goi khong co bien the).
    Rules (spec V2.4): 1 mau dung >2 lan/video -> canh bao; 1 bien the
    cua 1 mau lap >3 lan -> canh bao."""
    warnings = []
    by_tpl = {}
    by_var = {}
    for sh in shots:
        k = (sh.get("pack"), sh.get("name"))
        by_tpl[k] = by_tpl.get(k, 0) + 1
        if sh.get("layout") is not None:
            kv = (sh.get("pack"), sh.get("name"), sh.get("layout"))
            by_var[kv] = by_var.get(kv, 0) + 1
    for (pk, name), c in sorted(by_tpl.items()):
        if c > 2:
            warnings.append(
                "mau %s:%s dung %d lan trong 1 video (>2) - de trung khuon"
                % (pk, name, c))
    for (pk, name, lay), c in sorted(by_var.items()):
        if c > 3:
            warnings.append(
                "bien the %d cua mau %s:%s lap %d lan (>3)"
                % (lay + 1, pk, name, c))
    return warnings


def scan_pacing(shots):
    """Quet nhip dung chung cho moi goi (dinh nghia goc o
    test01_scenes.scan_pacing — doan >5s khong bien co thi canh bao)."""
    return stage_mod.scan_pacing(shots)


# ------------------------------------------------------------------ goi y gan
def _fold(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d")


def suggest(pack, text, index=0, used=None):
    """Tu gan 1 mau cua goi template cho 1 cau.

    Tra {scene: '<prefix><key>', name, reason, match (0..5), top3}.
    Diem: so tu khoa trong tags/ten mau xuat hien trong cau (da bo dau).
    Khong khop tu khoa nao -> xoay vong theo thu tu registry, uu tien
    mau chua dung trong job nay (used = dict key -> so lan)."""
    mod = module_for(pack)
    pack_info = next((p for p in PACKS if p["id"] == normalize_pack(pack)),
                     None)
    if mod is None or pack_info is None:
        return {"scene": None, "name": "", "reason": "", "match": 0,
                "top3": []}
    prefix = pack_info["prefix"]
    folded = " " + _fold(text) + " "
    used = used or {}
    scored = []
    keys = list(mod.TEMPLATES.keys())
    for pos, key in enumerate(keys):
        info = mod.TEMPLATES[key]
        hay = _fold(info.get("tags", "") + " " + info.get("name", ""))
        words = {w for w in hay.replace(",", " ").split() if len(w) >= 3}
        score = sum(1 for w in words if (" " + w) in folded
                    or (w + " ") in folded)
        scored.append((score, pos, key))
    scored.sort(key=lambda x: (-x[0], used.get(x[2], 0), x[1]))
    best_score, _pos, best_key = scored[0]
    if best_score <= 0:
        # xoay vong theo vi tri cau, tranh mau vua dung o cau truoc
        rot = keys[index % len(keys):] + keys[:index % len(keys)]
        best_key = min(rot, key=lambda k: used.get(k, 0))
        reason = ("xoay vong vai tro (câu chưa có manh mối rõ) — "
                  "đổi tay nếu chưa ưng")
        match = 1
    else:
        reason = "khớp từ khóa nội dung với mẫu %s" % best_key
        match = min(5, 1 + best_score)
    top3 = []
    for sc, _p, key in scored[:3]:
        if sc <= 0 and key != best_key:
            continue
        top3.append({"scene": prefix + key,
                     "name": mod.TEMPLATES[key]["name"],
                     "match": min(5, 1 + sc) if sc > 0 else match})
    if not top3:
        top3 = [{"scene": prefix + best_key,
                 "name": mod.TEMPLATES[best_key]["name"], "match": match}]
    used[best_key] = used.get(best_key, 0) + 1
    return {"scene": prefix + best_key,
            "name": mod.TEMPLATES[best_key]["name"],
            "reason": reason, "match": match, "top3": top3,
            "highlights": [], "chips": [], "low_match": best_score <= 0,
            "params": {}}
