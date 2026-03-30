#!/usr/bin/env python3
"""
Expense Tracker CLI — Python / CSV / Datetime
Zero data loss · Instant reports · 100% input integrity
"""

import csv
import os
import sys
from datetime import datetime, date
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────

DATA_FILE = "expenses.csv"
DATE_FMT  = "%Y-%m-%d"

CATEGORIES = [
    "Food", "Transport", "Housing", "Utilities",
    "Entertainment", "Healthcare", "Shopping", "Education", "Other"
]

FIELDNAMES = ["id", "date", "category", "description", "amount"]

# ── ANSI colours ──────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"

def bold(s):    return f"{C.BOLD}{s}{C.RESET}"
def dim(s):     return f"{C.DIM}{s}{C.RESET}"
def red(s):     return f"{C.RED}{s}{C.RESET}"
def green(s):   return f"{C.GREEN}{s}{C.RESET}"
def yellow(s):  return f"{C.YELLOW}{s}{C.RESET}"
def cyan(s):    return f"{C.CYAN}{s}{C.RESET}"
def blue(s):    return f"{C.BLUE}{s}{C.RESET}"

# ── Storage ───────────────────────────────────────────────────────────────────

def _ensure_file():
    """Create CSV with headers if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()

def _load_all() -> list[dict]:
    _ensure_file()
    with open(DATA_FILE, newline="") as f:
        return list(csv.DictReader(f))

def _save_all(rows: list[dict]):
    with open(DATA_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

def _next_id(rows: list[dict]) -> int:
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1

def _append_row(row: dict):
    _ensure_file()
    with open(DATA_FILE, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDNAMES).writerow(row)

# ── Validators ────────────────────────────────────────────────────────────────

def _parse_date(s: str) -> date:
    s = s.strip()
    if not s:
        raise ValueError("Date cannot be empty.")
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        raise ValueError(f"Invalid date '{s}'. Use YYYY-MM-DD.")

def _parse_amount(s: str) -> float:
    s = s.strip()
    if not s:
        raise ValueError("Amount cannot be empty.")
    try:
        val = float(s)
    except ValueError:
        raise ValueError(f"'{s}' is not a valid number.")
    if val <= 0:
        raise ValueError("Amount must be greater than zero.")
    return round(val, 2)

def _parse_description(s: str) -> str:
    s = s.strip()
    if not s:
        raise ValueError("Description cannot be empty.")
    if len(s) > 120:
        raise ValueError("Description too long (max 120 chars).")
    return s

def _pick_category() -> str:
    print()
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {dim(str(i) + '.')} {cat}")
    print()
    while True:
        raw = input(f"  Category {dim('[1-' + str(len(CATEGORIES)) + ']')}: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(CATEGORIES):
            return CATEGORIES[int(raw) - 1]
        # Allow typing the name directly
        match = [c for c in CATEGORIES if c.lower().startswith(raw.lower())]
        if len(match) == 1:
            return match[0]
        print(red(f"  ✗ Enter a number 1–{len(CATEGORIES)} or a category name."))

def _prompt(label: str, validator, default=None) -> str:
    hint = f" {dim('[' + default + ']')}" if default else ""
    while True:
        try:
            raw = input(f"  {label}{hint}: ").strip()
            if not raw and default:
                raw = default
            return validator(raw)
        except ValueError as e:
            print(red(f"  ✗ {e}"))

# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_add():
    print(f"\n{bold('  ── Add Expense ──')}\n")
    today = date.today().strftime(DATE_FMT)
    exp_date    = _prompt("Date (YYYY-MM-DD)", _parse_date, default=today)
    category    = _pick_category()
    description = _prompt("Description", _parse_description)
    amount      = _prompt("Amount (₹)", _parse_amount)

    rows = _load_all()
    row = {
        "id":          _next_id(rows),
        "date":        str(exp_date),
        "category":    category,
        "description": description,
        "amount":      f"{amount:.2f}",
    }
    _append_row(row)
    print(green(f"\n  ✓ Expense #{row['id']} saved — ₹{amount:.2f} on {category}\n"))


def cmd_list(filter_date_from=None, filter_date_to=None, filter_cat=None):
    rows = _load_all()

    # Apply filters
    if filter_date_from:
        rows = [r for r in rows if r["date"] >= filter_date_from]
    if filter_date_to:
        rows = [r for r in rows if r["date"] <= filter_date_to]
    if filter_cat:
        rows = [r for r in rows if r["category"].lower() == filter_cat.lower()]

    if not rows:
        print(yellow("\n  No expenses found for the given filters.\n"))
        return

    # Table
    print()
    _hline()
    header = f"{'ID':>4}  {'Date':<12}  {'Category':<14}  {'Description':<35}  {'Amount':>10}"
    print(f"  {bold(header)}")
    _hline()
    total = 0.0
    for r in rows:
        amt = float(r["amount"])
        total += amt
        desc = r["description"][:34]
        line = f"{r['id']:>4}  {r['date']:<12}  {r['category']:<14}  {desc:<35}  {green('₹' + f'{amt:>9.2f}')}"
        print(f"  {line}")
    _hline()
    print(f"  {'TOTAL':>4}  {'':12}  {'':14}  {'':35}  {bold(cyan('₹' + f'{total:>9.2f}'))}")
    _hline()
    print(f"  {dim(str(len(rows)) + ' record(s)')}\n")


def cmd_delete():
    print(f"\n{bold('  ── Delete Expense ──')}\n")
    raw = input("  Enter Expense ID to delete: ").strip()
    if not raw.isdigit():
        print(red("  ✗ Invalid ID.\n"))
        return
    exp_id = int(raw)
    rows = _load_all()
    match = [r for r in rows if int(r["id"]) == exp_id]
    if not match:
        print(red(f"  ✗ No expense with ID {exp_id}.\n"))
        return
    r = match[0]
    print(f"\n  {yellow('!')} About to delete: [{r['date']}] {r['category']} — {r['description']} — ₹{r['amount']}")
    confirm = input("  Confirm? (y/N): ").strip().lower()
    if confirm != "y":
        print(dim("  Cancelled.\n"))
        return
    rows = [r for r in rows if int(r["id"]) != exp_id]
    _save_all(rows)
    print(green(f"  ✓ Expense #{exp_id} deleted.\n"))


def cmd_report():
    print(f"\n{bold('  ── Financial Report ──')}\n")
    print("  Filter by date range (leave blank for all time)")
    raw_from = input("  From (YYYY-MM-DD): ").strip()
    raw_to   = input("  To   (YYYY-MM-DD): ").strip()

    date_from = None
    date_to   = None
    try:
        if raw_from:
            date_from = str(_parse_date(raw_from))
        if raw_to:
            date_to   = str(_parse_date(raw_to))
    except ValueError as e:
        print(red(f"  ✗ {e}\n"))
        return

    rows = _load_all()
    if date_from:
        rows = [r for r in rows if r["date"] >= date_from]
    if date_to:
        rows = [r for r in rows if r["date"] <= date_to]

    if not rows:
        print(yellow("  No expenses in this range.\n"))
        return

    total = sum(float(r["amount"]) for r in rows)
    by_cat = defaultdict(float)
    by_month = defaultdict(float)
    for r in rows:
        by_cat[r["category"]]          += float(r["amount"])
        by_month[r["date"][:7]]        += float(r["amount"])

    period = f"{date_from or rows[0]['date']} → {date_to or rows[-1]['date']}"
    print(f"\n  {bold('Period:')} {period}")
    print(f"  {bold('Records:')} {len(rows)}")
    print(f"  {bold('Total Spend:')} {cyan('₹' + f'{total:.2f}')}\n")

    # Category breakdown
    _hline()
    print(f"  {bold('Category Breakdown')}")
    _hline()
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = amt / total * 100
        bar = "█" * int(pct / 3)
        print(f"  {cat:<14}  {green('₹' + f'{amt:>10.2f}')}  {dim(bar + f' {pct:.1f}%')}")
    _hline()

    # Monthly breakdown
    if len(by_month) > 1:
        print(f"\n  {bold('Monthly Breakdown')}")
        _hline()
        for month, amt in sorted(by_month.items()):
            print(f"  {month}      {cyan('₹' + f'{amt:>10.2f}')}")
        _hline()

    # Top 5 expenses
    top5 = sorted(rows, key=lambda r: -float(r["amount"]))[:5]
    print(f"\n  {bold('Top 5 Expenses')}")
    _hline()
    for r in top5:
        amt_str = yellow("₹" + f"{float(r['amount']):>9.2f}")
        print(f"  {r['date']}  {r['category']:<14}  {r['description'][:30]:<30}  {amt_str}")
    _hline()
    print()


def cmd_edit():
    print(f"\n{bold('  ── Edit Expense ──')}\n")
    raw = input("  Enter Expense ID to edit: ").strip()
    if not raw.isdigit():
        print(red("  ✗ Invalid ID.\n"))
        return
    exp_id = int(raw)
    rows = _load_all()
    idx  = next((i for i, r in enumerate(rows) if int(r["id"]) == exp_id), None)
    if idx is None:
        print(red(f"  ✗ No expense with ID {exp_id}.\n"))
        return

    r = rows[idx]
    print(f"\n  Editing #{exp_id}: [{r['date']}] {r['category']} — {r['description']} — ₹{r['amount']}")
    print(dim("  (Press Enter to keep current value)\n"))

    new_date = _prompt("Date (YYYY-MM-DD)", _parse_date, default=r["date"])
    print(f"  Current category: {bold(r['category'])}")
    change_cat = input("  Change category? (y/N): ").strip().lower()
    new_cat = _pick_category() if change_cat == "y" else r["category"]
    new_desc = _prompt("Description", _parse_description, default=r["description"])
    new_amt  = _prompt("Amount (₹)", _parse_amount, default=r["amount"])

    rows[idx] = {
        "id":          r["id"],
        "date":        str(new_date),
        "category":    new_cat,
        "description": new_desc,
        "amount":      f"{new_amt:.2f}",
    }
    _save_all(rows)
    print(green(f"\n  ✓ Expense #{exp_id} updated.\n"))


def cmd_stats():
    rows = _load_all()
    if not rows:
        print(yellow("\n  No data yet.\n"))
        return
    total   = sum(float(r["amount"]) for r in rows)
    avg     = total / len(rows)
    amounts = sorted(float(r["amount"]) for r in rows)
    median  = amounts[len(amounts)//2]
    max_exp = max(rows, key=lambda r: float(r["amount"]))
    min_exp = min(rows, key=lambda r: float(r["amount"]))

    print(f"\n  {bold('── Quick Stats ──')}\n")
    print(f"  Records      : {bold(str(len(rows)))}")
    print(f"  Total Spend  : {cyan(bold('₹' + f'{total:.2f}'))}")
    print(f"  Average      : ₹{avg:.2f}")
    print(f"  Median       : ₹{median:.2f}")
    print(f"  Largest      : ₹{float(max_exp['amount']):.2f} — {max_exp['description']} ({max_exp['date']})")
    print(f"  Smallest     : ₹{float(min_exp['amount']):.2f} — {min_exp['description']} ({min_exp['date']})")
    print(f"  Date range   : {rows[0]['date']} → {rows[-1]['date']}\n")

# ── UI helpers ────────────────────────────────────────────────────────────────

def _hline():
    print(dim("  " + "─" * 80))

def _banner():
    print(f"""
{cyan(bold('  ╔══════════════════════════════════════╗'))}
{cyan(bold('  ║       EXPENSE TRACKER  CLI  v1.0     ║'))}
{cyan(bold('  ╚══════════════════════════════════════╝'))}
  {dim('Python · CSV · Datetime  |  Data: ' + DATA_FILE)}
""")

def _menu():
    print(f"  {bold('Commands')}")
    cmds = [
        ("add",    "Add a new expense"),
        ("list",   "List all expenses"),
        ("filter", "Filter by date range / category"),
        ("report", "Full financial report"),
        ("edit",   "Edit an expense"),
        ("delete", "Delete an expense"),
        ("stats",  "Quick stats summary"),
        ("quit",   "Exit"),
    ]
    for cmd, desc in cmds:
        print(f"  {cyan(bold(cmd.ljust(8)))} {dim('—')} {desc}")
    print()

# ── Main REPL ─────────────────────────────────────────────────────────────────

def _handle_filter():
    print(f"\n{bold('  ── Filter Expenses ──')}\n")
    print("  Leave blank to skip a filter.")
    raw_from = input("  From date (YYYY-MM-DD): ").strip()
    raw_to   = input("  To   date (YYYY-MM-DD): ").strip()
    print(f"\n  Categories: {', '.join(CATEGORIES)}")
    raw_cat  = input("  Category (or blank for all): ").strip()

    date_from = date_to = cat = None
    try:
        if raw_from: date_from = str(_parse_date(raw_from))
        if raw_to:   date_to   = str(_parse_date(raw_to))
    except ValueError as e:
        print(red(f"  ✗ {e}\n"))
        return
    if raw_cat:
        match = [c for c in CATEGORIES if c.lower().startswith(raw_cat.lower())]
        cat = match[0] if match else raw_cat

    cmd_list(filter_date_from=date_from, filter_date_to=date_to, filter_cat=cat)


def main():
    _ensure_file()
    _banner()
    _menu()

    while True:
        try:
            cmd = input(f"{cyan('▶')} Command: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{dim('  Goodbye.')}\n")
            sys.exit(0)

        if cmd in ("quit", "exit", "q"):
            print(f"\n{dim('  Goodbye.')}\n")
            break
        elif cmd == "add":
            cmd_add()
        elif cmd in ("list", "ls"):
            cmd_list()
        elif cmd in ("filter", "f"):
            _handle_filter()
        elif cmd in ("report", "r"):
            cmd_report()
        elif cmd in ("edit", "e"):
            cmd_edit()
        elif cmd in ("delete", "del", "d"):
            cmd_delete()
        elif cmd in ("stats", "s"):
            cmd_stats()
        elif cmd in ("help", "h", "?"):
            _menu()
        elif cmd == "":
            pass
        else:
            print(yellow(f"  Unknown command '{cmd}'. Type 'help' for options.\n"))


if __name__ == "__main__":
    main()
