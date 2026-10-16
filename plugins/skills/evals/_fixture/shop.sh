#!/usr/bin/env bash
# Shared fixture: a small Python "shop" repo plus a delegator config in $HOME.
# Each case's fixture.sh sources this file; set NO_CONFIG=1 to skip the config.
set -euo pipefail

mkdir -p src tests
if [ -z "${NO_CONFIG:-}" ]; then
mkdir -p "$HOME/.claude"
cat > "$HOME/.claude/delegator.json" <<'JSON'
{
  "delegator": { "model": "opus", "effort": "high" },
  "research": { "model": "sonnet", "effort": "low" },
  "implementation": { "model": "sonnet", "effort": "low" },
  "review": { "model": "sonnet", "effort": "low" },
  "review_after_implementation": false
}
JSON
fi

cat > src/pricing.py <<'PY'
def parse_price(text):
    return float(text.strip().lstrip("$"))


def order_total(items, coupon=None):
    subtotal = sum(i["price"] * i["qty"] for i in items)
    if coupon == "SAVE10" and subtotal > 100:
        subtotal = subtotal * 0.9
    return round(subtotal, 2)
PY

cat > src/dates.py <<'PY'
from datetime import date


def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def days_between(a: date, b: date) -> int:
    return (a - b).days  # bug: negative when a < b, callers expect abs
PY

cat > src/inventory.py <<'PY'
STOCK = {}


def reserve(sku, qty):
    if STOCK.get(sku, 0) > qty:  # bug: should be >=
        STOCK[sku] -= qty
        return True
    return False
PY

cat > src/users.py <<'PY'
def display_name(user):
    return user["first"] + " " + user["last"]  # bug: KeyError when "last" missing


def is_admin(user):
    return user.get("role") == "admin"
PY

cat > tests/test_dates.py <<'PY'
from datetime import date
from src.dates import format_date


def test_format_date():
    assert format_date(date(2026, 1, 2)) == "2026-01-02"
PY

cat > tests/test_pricing.py <<'PY'
from src.pricing import order_total


def test_order_total_discount():
    assert order_total([{"price": 60, "qty": 2}], "SAVE10") == 108.0
PY

git init -q && git add -A && git -c user.name=eval -c user.email=eval@example.com commit -qm init
