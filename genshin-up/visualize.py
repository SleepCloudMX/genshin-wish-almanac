import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

TEMPLATE = Path(__file__).resolve().parent / "templates" / "up-visual.html"


def main():
    data = common.load()
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__UP_DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("__GENERATED_AT__", date.today().strftime("%Y/%m/%d"))
    out = common.ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"written: {out.relative_to(common.ROOT)}（{len(data)} 期）")


if __name__ == "__main__":
    main()
