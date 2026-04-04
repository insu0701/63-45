from datetime import datetime, UTC


def build_response(data, snapshot_time=None, errors=None):
    return {
        "data": data,
        "meta": {
            "generated_at": datetime.now(UTC).isoformat(),
            "snapshot_time": snapshot_time.isoformat() if snapshot_time else None,
        },
        "errors": errors or [],
    }