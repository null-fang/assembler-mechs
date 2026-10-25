#!/usr/bin/env python3
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
man = json.loads((root / "tools" / "part_models_manifest.json").read_text(encoding="utf-8"))
cat = (root / "src" / "Shared" / "Parts" / "Catalog.luau").read_text(encoding="utf-8")
bay = (root / "src" / "Shared" / "Parts" / "CatalogBay.luau").read_text(encoding="utf-8")
pat = r'id\s*=\s*"([a-z0-9_]+)"'
ids = set(re.findall(pat, cat)) | set(re.findall(pat, bay))
missing = [i for i in man["ids"] if i not in ids]
print("models", man["count"], "catalog_ids", len(ids), "missing", len(missing))
if missing:
    print("missing:", ", ".join(missing[:20]))
raise SystemExit(1 if missing else 0)
