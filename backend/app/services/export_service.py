import csv
import io


def rows_to_csv(rows: list[dict]) -> str:
    """Rows contain only numbers and ISO dates (no user text), so there is no CSV-injection vector."""
    buffer = io.StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return buffer.getvalue()
