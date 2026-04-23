#!/usr/bin/env python3
import json
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "tmp113" / "ocr-cache"
CACHE.mkdir(parents=True, exist_ok=True)
TESSDATA = ROOT / "tessdata"
THUMB = "/tmp/thumbnail"


PDFS = {
    "113-E1-1A": "113-1st-外匯1A-ADJ.pdf",
    "113-E1-2A": "113-1st-外匯2A-ADJ.pdf",
    "113-E2-1A": "113-2nd-外匯1A-ADJ.pdf",
    "113-E2-2A": "113-2nd-外匯2A-ADJ.pdf",
}


def render_page(pdf: Path, page_num: int, out_png: Path) -> None:
    if out_png.exists():
        return
    out_png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [THUMB, str(pdf), str(page_num), str(out_png), "1200", "1700"],
        check=True,
    )


def ocr_page(png: Path, txt_path: Path) -> str:
    if txt_path.exists():
        return txt_path.read_text()
    cmd = [
        "tesseract",
        str(png),
        "stdout",
        "-l",
        "chi_tra",
        "--psm",
        "6",
    ]
    env = os.environ.copy()
    env["TESSDATA_PREFIX"] = str(TESSDATA)
    text = subprocess.check_output(cmd, text=True, errors="ignore", env=env)
    txt_path.write_text(text)
    return text


def normalize(line: str, exam_suffix: str) -> str:
    suffix = exam_suffix.replace("-", "")
    line = (
        line.replace("【 】", "【】")
        .replace("【】】", "【】")
        .replace("0BU", "OBU")
        .replace("0/A", "O/A")
        .replace("T0KY0", "TOKYO")
        .replace("0MNER", "OWNER")
    )
    line = re.sub(rf"第\s*\d+\s*頁\s*,\s*共\s*\d+\s*頁\s*{suffix}", "", line)
    line = re.sub(r"1138?\s*年度外匯內部證照第.*?檢定試題", "", line)
    line = re.sub(r"準\s*考證號\s*:?.*", "", line)
    line = re.sub(r"姓名\s*:?.*", "", line)
    line = re.sub(r"卷\s*[。.]?\s*別\s*:?.*", "", line)
    line = re.sub(r"※\s*單選題.*", "", line)
    line = re.sub(r"[ \t]+", " ", line)
    for _ in range(5):
        line = re.sub(r"(?<=[\u4e00-\u9fff]) (?=[\u4e00-\u9fff])", "", line)
        line = re.sub(r"(?<=[\u4e00-\u9fff]) (?=[，。；：、（）])", "", line)
        line = re.sub(r"(?<=[，。；：、（）]) (?=[\u4e00-\u9fff])", "", line)
    return line.strip(" .")


def is_question(line: str) -> bool:
    return bool(re.match(r"^【.?】\s*\d+[、,，.]", line))


def question_number(line: str) -> int | None:
    match = re.match(r"^【.?】\s*(\d+)", line)
    return int(match.group(1)) if match else None


def strip_question_prefix(line: str) -> str:
    return re.sub(r"^【.?】\s*\d+[、,，.]\s*", "", line)


def is_option_start(line: str) -> bool:
    return bool(re.match(r"^[0-9@QGODCS心人全(（]", line))


def strip_option_prefix(line: str) -> str:
    return re.sub(r"^[0-9@QGODCS心人全(（)\s]+", "", line).strip()


def parse_exam(exam_key: str, pdf_name: str) -> dict:
    pdf = ROOT / pdf_name
    exam_suffix = exam_key.split("-")[-1]
    render_dir = CACHE / exam_key
    lines: list[str] = []

    for page_num in range(1, 12):
        png = render_dir / f"page-{page_num:02d}.png"
        txt = render_dir / f"page-{page_num:02d}.txt"
        render_page(pdf, page_num, png)
        raw = ocr_page(png, txt)
        for line in raw.splitlines():
            norm = normalize(line.strip(), exam_suffix)
            if norm:
                lines.append(norm)

    questions = []
    current = None
    for line in lines:
        if is_question(line):
            if current:
                questions.append(current)
            current = {
                "n": question_number(line),
                "text": strip_question_prefix(line),
                "opts": [],
            }
            continue
        if current is None:
            continue
        if len(current["opts"]) < 4 and (is_option_start(line) or current["opts"]):
            if is_option_start(line):
                current["opts"].append(strip_option_prefix(line) or "")
            elif current["opts"]:
                current["opts"][-1] += line
            else:
                current["text"] += line
        else:
            current["text"] += line
    if current:
        questions.append(current)

    return {
        "exam": exam_key,
        "count": len(questions),
        "numbers": [q["n"] for q in questions],
        "missing_options": [q["n"] for q in questions if len(q["opts"]) != 4],
        "questions": questions,
    }


def main() -> None:
    data = {key: parse_exam(key, pdf) for key, pdf in PDFS.items()}
    out = ROOT / "tmp113" / "parsed-113.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    summary = {
        key: {
            "count": value["count"],
            "missing_numbers": [n for n in range(1, 81) if n not in value["numbers"]],
            "missing_options": value["missing_options"],
        }
        for key, value in data.items()
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
