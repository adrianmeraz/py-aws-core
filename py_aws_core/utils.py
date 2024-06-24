from datetime import datetime, timezone


def to_iso_8601(dt: datetime = None) -> str:
    # 2020-07-10 15:00:00.000
    if not dt:
        dt = datetime.now(tz=timezone.utc).replace(microsecond=0)
    return dt.isoformat()
