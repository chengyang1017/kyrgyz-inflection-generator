import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

CSV_FILE_NAMES = {
    "名词": "kyrgyz_nouns.csv",
    "动词": "kyrgyz_verbs.csv",
}

SQLITE_TABLE_NAMES = {
    "名词": "nouns",
    "动词": "verbs",
}


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_nouns():
    json_path = DATA_DIR / "nouns.json"
    txt_path = DATA_DIR / "nouns.txt"

    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "nouns" in data:
            data = data["nouns"]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "中文" not in item:
                    item["中文"] = ""
            return data

    if txt_path.exists():
        words = []
        with txt_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("	")
                if len(parts) >= 2:
                    words.append({"单数": parts[0], "中文": parts[1]})
                else:
                    words.append({"单数": parts[0], "中文": ""})
        return words

    print("未找到 data/nouns.json 或 data/nouns.txt，已生成空名词表。")
    return []


def load_verbs():
    json_path = DATA_DIR / "verbs.json"
    txt_path = DATA_DIR / "verbs.txt"

    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "verbs" in data:
            data = data["verbs"]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item.setdefault("中文", "")
                    item.setdefault("原形", "")
                    item.setdefault("词干", "")
            return data

    if txt_path.exists():
        verbs = []
        with txt_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                verbs.append({
                    "原形": parts[0] if len(parts) > 0 else "",
                    "词干": parts[1] if len(parts) > 1 else "",
                    "中文": parts[2] if len(parts) > 2 else "",
                })
        return verbs

    print("未找到 data/verbs.json 或 data/verbs.txt，已生成空动词表。")
    return []


def export_multi_sheet_excel(sheets, output_path="output/kyrgyz.xlsx"):
    ensure_output_dir()
    path = ROOT_DIR / output_path if not Path(output_path).is_absolute() else Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return path


def export_csv_files(sheets, output_dir="output"):
    ensure_output_dir()
    output_path = ROOT_DIR / output_dir if not Path(output_dir).is_absolute() else Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    legacy_csv = output_path / "kyrgyz.csv"
    if legacy_csv.exists():
        legacy_csv.unlink()

    exported_paths = {}
    for sheet_name, df in sheets.items():
        file_name = CSV_FILE_NAMES.get(sheet_name, f"kyrgyz_{sheet_name}.csv")
        path = output_path / file_name
        df.to_csv(path, index=False, encoding="utf-8-sig")
        exported_paths[sheet_name] = path
    return exported_paths


def export_json_file(sheets, output_path="output/kyrgyz.json"):
    ensure_output_dir()
    path = ROOT_DIR / output_path if not Path(output_path).is_absolute() else Path(output_path)
    json_data = {
        sheet_name: df.to_dict(orient="records")
        for sheet_name, df in sheets.items()
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    return path


def export_sqlite_db(sheets, output_path="output/kyrgyz.db"):
    ensure_output_dir()
    path = ROOT_DIR / output_path if not Path(output_path).is_absolute() else Path(output_path)
    with sqlite3.connect(path) as conn:
        for sheet_name, df in sheets.items():
            table_name = SQLITE_TABLE_NAMES.get(sheet_name, sheet_name)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
    return path


def export_all_formats(sheets):
    exported = {
        "excel": export_multi_sheet_excel(sheets),
        "csv": export_csv_files(sheets),
        "json": export_json_file(sheets),
        "sqlite": export_sqlite_db(sheets),
    }
    return exported
