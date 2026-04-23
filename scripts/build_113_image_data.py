#!/usr/bin/env python3
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "113-crops"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TESSDATA = ROOT / "tessdata"
THUMB = "/tmp/thumbnail"
NS = {"x": "http://www.w3.org/1999/xhtml"}

EXAMS = {
    "113-E1-1A": {"pdf": "113-1st-外匯1A-ADJ.pdf", "pages": 11},
    "113-E1-2A": {"pdf": "113-1st-外匯2A-ADJ.pdf", "pages": 11},
    "113-E2-1A": {"pdf": "113-2nd-外匯1A-ADJ.pdf", "pages": 12},
    "113-E2-2A": {"pdf": "113-2nd-外匯2A-ADJ.pdf", "pages": 12},
}

ANSWERS = {
    "113-E1-1A": [4,3,1,4,3,3,1,2,4,2,2,3,2,3,2,4,4,4,4,4,2,1,2,1,3,1,4,4,2,3,4,1,4,4,4,4,3,4,1,2,1,3,4,3,3,1,3,4,2,2,4,1,4,3,4,3,1,3,2,1,3,1,4,2,2,1,4,3,2,2,4,1,4,3,4,1,3,1,2,3],
    "113-E1-2A": [4,1,3,4,4,2,2,3,3,4,2,4,1,1,4,4,3,3,2,2,1,1,4,3,4,4,2,2,2,3,1,2,1,3,4,4,3,3,2,3,4,2,3,3,4,1,1,3,1,1,4,2,3,1,4,1,2,4,4,3,1,2,1,3,4,1,1,2,3,4,3,1,4,1,1,3,4,1,1,3],
    "113-E2-1A": [4,1,3,2,4,1,2,2,3,3,4,4,1,4,1,4,4,1,3,4,1,4,1,3,2,3,2,2,4,1,2,1,3,3,3,1,2,3,3,1,4,1,4,1,2,2,1,1,3,3,1,4,4,3,3,1,2,3,1,4,2,4,4,2,3,1,2,1,4,4,2,3,4,3,3,4,2,1,1,1],
    "113-E2-2A": [3,2,4,1,4,2,3,4,4,1,2,3,2,2,1,2,1,1,4,3,2,1,1,2,3,1,3,2,3,3,3,1,4,3,4,1,1,1,2,1,2,3,4,2,4,1,2,1,2,3,4,3,3,1,4,3,2,1,1,3,3,4,4,3,4,4,4,2,3,4,1,1,4,4,4,1,4,1,4,4],
}

MANUAL_ANCHORS = {
    "113-E1-1A": [{"page": 10, "n": 77, "y": 1102, "title": "有關出口押匯拒付，下列敘述何者正確？"}],
    "113-E1-2A": [{"page": 6, "n": 45, "y": 1470, "title": "辦理DBU信用狀通知，如應受益人之要求須致電開狀行作確認或通知時，應徵得受益人之書面證明，每筆並收取多少郵電費？"}],
    "113-E2-2A": [{"page": 9, "n": 65, "y": 1492, "title": "有關本行國際應收帳款承購及融資種類，下列敘述何者錯誤？"}],
}


def render_page(pdf: Path, page_num: int, out_png: Path) -> None:
    if out_png.exists():
        return
    out_png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [THUMB, str(pdf), str(page_num), str(out_png), "1200", "1700"],
        check=True,
    )


def hocr_lines(image_path: Path) -> list[dict]:
    cmd = [
        "tesseract",
        str(image_path),
        "stdout",
        "-l",
        "chi_tra",
        "--psm",
        "6",
        "-c",
        "tessedit_create_hocr=1",
    ]
    xml = subprocess.check_output(cmd, text=True, env={**os.environ, "TESSDATA_PREFIX": str(TESSDATA)})
    root = ET.fromstring(xml)
    lines = []
    for span in root.findall('.//x:span[@class="ocr_line"]', NS):
        title = span.attrib.get("title", "")
        match = re.search(r"bbox (\d+) (\d+) (\d+) (\d+)", title)
        if not match:
            continue
        text = " ".join("".join(span.itertext()).split())
        text = text.replace("【 】", "【】").replace("】】", "】").replace("0BU", "OBU")
        lines.append(
            {
                "y1": int(match.group(2)),
                "y2": int(match.group(4)),
                "text": text,
            }
        )
    return lines


def auto_anchors(lines: list[dict]) -> list[dict]:
    anchors = []
    for line in lines:
        match = re.search(r"【\s*】\s*(\d+)[、,，.]", line["text"])
        if not match:
            continue
        title = re.sub(r"^.*?【\s*】\s*\d+[、,，.]\s*", "", line["text"]).strip()
        title = re.sub(r"\s+", "", title)
        anchors.append({"n": int(match.group(1)), "y": line["y1"], "title": title})
    return anchors


def stitch_images(parts: list[tuple[Path, tuple[int, int, int, int]]], out_path: Path) -> None:
    crops = []
    for image_path, box in parts:
        img = Image.open(image_path)
        crops.append(img.crop(box))
    total_height = sum(img.height for img in crops) + (12 * (len(crops) - 1))
    canvas = Image.new("RGB", (max(img.width for img in crops), total_height), "white")
    y = 0
    for idx, crop in enumerate(crops):
        canvas.paste(crop, (0, y))
        y += crop.height
        if idx < len(crops) - 1:
            y += 12
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "WEBP", quality=82, method=6)


def build_exam(exam_key: str, config: dict) -> list[dict]:
    pdf = ROOT / config["pdf"]
    cache_dir = ROOT / "tmp113" / "ocr-cache" / exam_key
    cache_dir.mkdir(parents=True, exist_ok=True)
    page_lines = {}
    page_anchors = {}

    for page_num in range(1, config["pages"] + 1):
        png = cache_dir / f"page-{page_num:02d}.png"
        render_page(pdf, page_num, png)
        lines = hocr_lines(png)
        page_lines[page_num] = lines
        page_anchors[page_num] = auto_anchors(lines)

    for item in MANUAL_ANCHORS.get(exam_key, []):
        page_anchors[item["page"]].append({"n": item["n"], "y": item["y"], "title": item["title"]})

    flat = []
    for page_num in range(1, config["pages"] + 1):
        anchors = sorted(page_anchors[page_num], key=lambda x: x["y"])
        for anchor in anchors:
            flat.append({"page": page_num, **anchor})

    crops = []
    x1, x2 = 40, 1160
    page_bottom = 1620
    carry_threshold = 120

    for idx, anchor in enumerate(flat):
        page_num = anchor["page"]
        same_page = [a for a in flat if a["page"] == page_num]
        pos = same_page.index(next(a for a in same_page if a["n"] == anchor["n"]))
        start_y = max(anchor["y"] - 12, 0)
        image_parts = []

        if pos + 1 < len(same_page):
            end_y = max(same_page[pos + 1]["y"] - 16, start_y + 40)
            image_parts.append((cache_dir / f"page-{page_num:02d}.png", (x1, start_y, x2, end_y)))
        else:
            image_parts.append((cache_dir / f"page-{page_num:02d}.png", (x1, start_y, x2, page_bottom)))
            if page_num < config["pages"]:
                next_anchors = sorted(page_anchors[page_num + 1], key=lambda x: x["y"])
                if next_anchors and next_anchors[0]["y"] > carry_threshold:
                    image_parts.append((cache_dir / f"page-{page_num + 1:02d}.png", (x1, 0, x2, next_anchors[0]["y"] - 16)))

        out_path = OUT_DIR / exam_key / f"q{anchor['n']:03d}.webp"
        stitch_images(image_parts, out_path)
        crops.append(
            {
                "n": anchor["n"],
                "text": anchor["title"],
                "img": str(out_path.relative_to(ROOT)),
                "ans": ANSWERS[exam_key][anchor["n"] - 1],
            }
        )

    crops.sort(key=lambda x: x["n"])
    expected = list(range(1, 81))
    found = [item["n"] for item in crops]
    missing = [n for n in expected if n not in found]
    if missing:
        raise RuntimeError(f"{exam_key} missing question crops: {missing}")
    return crops


def main() -> None:
    data = {exam_key: build_exam(exam_key, config) for exam_key, config in EXAMS.items()}
    out_file = ROOT / "data113.js"
    with out_file.open("w", encoding="utf-8") as f:
        f.write("const DATA_113 = ")
        json.dump(data, f, ensure_ascii=False)
        f.write(";\n")
    print("wrote", out_file)


if __name__ == "__main__":
    main()
