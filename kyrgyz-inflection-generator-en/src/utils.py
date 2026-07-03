import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

CSV_FILE_NAMES = {
    "Nouns": "kyrgyz_nouns.csv",
    "Verbs": "kyrgyz_verbs.csv",
}

JSON_KEYS = {
    "Nouns": "nouns",
    "Verbs": "verbs",
}

SQLITE_TABLE_NAMES = {
    "Nouns": "nouns",
    "Verbs": "verbs",
}


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_path(path):
    path = Path(path)
    return ROOT_DIR / path if not path.is_absolute() else path


def load_nouns():
    json_path = DATA_DIR / "nouns.json"
    txt_path = DATA_DIR / "nouns.txt"

    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "nouns" in data:
            data = data["nouns"]
        if isinstance(data, list):
            nouns = []
            for item in data:
                if isinstance(item, dict):
                    nouns.append({
                        "singular": item.get("singular", ""),
                        "meaning_zh": item.get("meaning_zh", ""),
                    })
            return nouns

    if txt_path.exists():
        nouns = []
        with txt_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                nouns.append({
                    "singular": parts[0] if len(parts) > 0 else "",
                    "meaning_zh": parts[1] if len(parts) > 1 else "",
                })
        return nouns

    print("No data/nouns.json or data/nouns.txt found. Using an empty noun list.")
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
            verbs = []
            for item in data:
                if isinstance(item, dict):
                    verbs.append({
                        "infinitive": item.get("infinitive", ""),
                        "stem": item.get("stem", ""),
                        "meaning_zh": item.get("meaning_zh", ""),
                    })
            return verbs

    if txt_path.exists():
        verbs = []
        with txt_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                verbs.append({
                    "infinitive": parts[0] if len(parts) > 0 else "",
                    "stem": parts[1] if len(parts) > 1 else "",
                    "meaning_zh": parts[2] if len(parts) > 2 else "",
                })
        return verbs

    print("No data/verbs.json or data/verbs.txt found. Using an empty verb list.")
    return []


def export_multi_sheet_excel(sheets, output_path="output/kyrgyz.xlsx"):
    ensure_output_dir()
    path = _resolve_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return path


def export_csv_files(sheets, output_dir="output"):
    ensure_output_dir()
    output_path = _resolve_path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    legacy_csv = output_path / "kyrgyz.csv"
    if legacy_csv.exists():
        legacy_csv.unlink()

    exported_paths = {}
    for sheet_name, df in sheets.items():
        file_name = CSV_FILE_NAMES.get(sheet_name, f"kyrgyz_{sheet_name.lower()}.csv")
        path = output_path / file_name
        df.to_csv(path, index=False, encoding="utf-8-sig")
        exported_paths[sheet_name] = path
    return exported_paths


def export_json_file(sheets, output_path="output/kyrgyz.json"):
    ensure_output_dir()
    path = _resolve_path(output_path)
    json_data = {
        JSON_KEYS.get(sheet_name, sheet_name.lower()): df.to_dict(orient="records")
        for sheet_name, df in sheets.items()
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    return path


def export_sqlite_db(sheets, output_path="output/kyrgyz.db"):
    ensure_output_dir()
    path = _resolve_path(output_path)
    with sqlite3.connect(path) as conn:
        for sheet_name, df in sheets.items():
            table_name = SQLITE_TABLE_NAMES.get(sheet_name, sheet_name.lower())
            df.to_sql(table_name, conn, if_exists="replace", index=False)
    return path


def export_all_formats(sheets):
    return {
        "excel": export_multi_sheet_excel(sheets),
        "csv": export_csv_files(sheets),
        "json": export_json_file(sheets),
        "sqlite": export_sqlite_db(sheets),
    }
