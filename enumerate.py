import os
import json
from collections import defaultdict

BASE_DIR = os.getcwd()   # <-- IMPORTANT FIX

def extract_fields(obj, prefix=""):
    fields = set()

    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            fields.add(path)
            fields |= extract_fields(v, path)

    elif isinstance(obj, list):
        path = f"{prefix}[]" if prefix else "[]"
        fields.add(path)
        for item in obj:
            fields |= extract_fields(item, path)

    return fields


def discover():
    sensor_fields = defaultdict(set)
    sensor_counts = defaultdict(int)

    for root, _, files in os.walk(BASE_DIR):
        json_files = [f for f in files if f.endswith(".json")]
        if not json_files:
            continue

        # Expect structure: dataset/<sensor>/<devEUI>/*.json
        rel = os.path.relpath(root, BASE_DIR)
        parts = rel.split(os.sep)

        if len(parts) < 2:
            continue

        sensor_name = parts[0]

        print(f"[+] Found {len(json_files)} JSON files in {root}")

        for jf in json_files:
            path = os.path.join(root, jf)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[!] Failed to parse {path}: {e}")
                continue

            sensor_counts[sensor_name] += 1
            sensor_fields[sensor_name] |= extract_fields(data)

    return sensor_fields, sensor_counts


if __name__ == "__main__":
    fields, counts = discover()

    print("\n\n=== SUMMARY ===")
    for sensor in sorted(fields):
        print("=" * 80)
        print(f"SENSOR: {sensor}")
        print(f"Total JSON files: {counts[sensor]}")
        print("Fields:")
        for field in sorted(fields[sensor]):
            print(f"  - {field}")
