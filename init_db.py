from __future__ import annotations

import sqlite3
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    schema_path = base_dir / 'schema.sql'
    insert_path = base_dir / 'insert_data.sql'

    db_path = base_dir / 'return_tracker.db'

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(read_text(schema_path))
        conn.executescript(read_text(insert_path))

        # Count all orders as requested
        cur = conn.execute('SELECT COUNT(*) FROM Orders')
        x = cur.fetchone()[0]
        print(f'Database initialized with {x} rows')
    finally:
        conn.commit()
        conn.close()


if __name__ == '__main__':
    main()

