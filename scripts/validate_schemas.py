#!/usr/bin/env python3
"""Validate profile JSON files against the checked-in JSON Schemas."""
from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "portfolio/profile.json", ROOT / "schemas/profile.schema.json"),
    (ROOT / "portfolio/projects.json", ROOT / "schemas/projects.schema.json"),
    (ROOT / "portfolio/proof-assets.json", ROOT / "schemas/proof-assets.schema.json"),
    (ROOT / "portfolio/activity-sources.json", ROOT / "schemas/activity-sources.schema.json"),
    (ROOT / "portfolio/repository-activity.json", ROOT / "schemas/repository-activity.schema.json"),
    (ROOT / "portfolio/engineering-activity.json", ROOT / "schemas/engineering-activity.schema.json"),
    (ROOT / "portfolio/private-project-registry.json", ROOT / "schemas/private-project-registry.schema.json"),
    (ROOT / "portfolio/discovered-projects.json", ROOT / "schemas/discovered-projects.schema.json"),
]


def main() -> int:
    errors: list[str] = []
    for data_path, schema_path in PAIRS:
        data = json.loads(data_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{data_path.relative_to(ROOT)}:{location}: {error.message}")
    if errors:
        print("Schema validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("JSON Schema validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
