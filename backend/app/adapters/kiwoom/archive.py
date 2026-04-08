from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.core.config import settings


def archive_kiwoom_payload(kind: str, payload: dict[str, Any]) -> Path:
    now = datetime.now(UTC)
    day_dir = Path(settings.kiwoom_raw_archive_dir) / now.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{kind}_{now.strftime('%H%M%S')}.json"
    path = day_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

    return path