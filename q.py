"""
Query runner. Two ways to use it:

    python q.py                     -> interactive. Type SQL, blank line runs it.
    python q.py "SELECT 1"          -> one-shot
    python q.py -f 02_profile.sql   -> run a whole file

Prints results as an aligned table so you can actually read them.
"""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).parent / "ring.db"
con = sqlite3.connect(DB)


def run(sql: str) -> None:
    sql = sql.strip().rstrip(";")
    if not sql:
        return
    try:
        cur = con.execute(sql)
    except sqlite3.Error as e:
        print(f"  !! {type(e).__name__}: {e}\n")
        return
    if cur.description is None:
        con.commit()
        print(f"  ok ({cur.rowcount} rows affected)\n")
        return

    cols = [d[0] for d in cur.description]
    rows = cur.fetchmany(50)
    fmt = lambda v: "NULL" if v is None else (f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    table = [cols] + [[fmt(v) for v in r] for r in rows]
    w = [max(len(r[i]) for r in table) for i in range(len(cols))]

    print("  " + " | ".join(c.ljust(w[i]) for i, c in enumerate(cols)))
    print("  " + "-+-".join("-" * x for x in w))
    for r in table[1:]:
        print("  " + " | ".join(c.ljust(w[i]) for i, c in enumerate(r)))
    extra = cur.fetchone()
    print(f"  ({len(rows)} rows shown{', more truncated' if extra else ''})\n")


if len(sys.argv) > 2 and sys.argv[1] == "-f":
    for stmt in Path(sys.argv[2]).read_text(encoding="utf-8").split(";"):
        if stmt.strip() and not stmt.strip().startswith("--"):
            print(f"\n>>> {stmt.strip()[:80]}...")
            run(stmt)
elif len(sys.argv) > 1:
    run(" ".join(sys.argv[1:]))
else:
    print(f"connected: {DB.name}   (blank line runs, Ctrl+C quits)\n")
    buf = []
    while True:
        try:
            line = input("sql> " if not buf else "...> ")
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip() == "":
            run("\n".join(buf))
            buf = []
        else:
            buf.append(line)
