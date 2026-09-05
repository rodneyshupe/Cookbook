#!/usr/bin/env python3
"""Manifest-based version bookkeeping for the cookbook books.

Replaces the old per-book git-tag scheme (``<Book>-vMAJOR.MINOR``). Versions
and last-updated dates are tracked in a single ``manifest.json`` that lives as
an asset on the rolling ``latest`` GitHub release, e.g.::

    {
      "TheMessyChef":          {"version": "4.6", "updated": "2026-09-05"},
      "AirFryerRecipes":       {"version": "1.7", "updated": "2026-08-20"},
      "PressureCookerRecipes": {"version": "1.6", "updated": "2026-07-11"},
      "SousVideRecipes":       {"version": "1.6", "updated": "2026-06-01"},
      "MealPlannerBook":       {"version": "1.10", "updated": "2026-09-05"}
    }

Bump rule (unchanged from the old scheme): increment MINOR by 1. A book with no
manifest entry is seeded:
  - TheMessyChef  -> 4.0   (legacy series, renamed from RodneyFavoriteRecipes)
  - every other   -> 1.0

Usage:
  book_versions.py current <manifest.json> <Book>
      Print the book's CURRENT version (seed value if the book is absent).

  book_versions.py next <manifest.json> <Book>
      Print the book's NEXT version (current bumped by one MINOR; seed value if
      the book is absent -- seeds are treated as the first published version and
      are NOT bumped).

  book_versions.py updated <manifest.json> <Book>
      Print the book's last-updated date (YYYY-MM-DD), or empty if unknown.

  book_versions.py set <manifest.json> <Book> <version> <date>
      Write/replace the book's entry and print the resulting manifest JSON to
      stdout (the file is updated in place too). Creates the file if missing.

A missing or unreadable manifest file is treated as ``{}`` (first run).
"""
import json
import os
import sys


def seed_version(book):
    return "4.0" if book == "TheMessyChef" else "1.0"


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def current_version(manifest, book):
    entry = manifest.get(book)
    if isinstance(entry, dict) and entry.get("version"):
        return str(entry["version"])
    return seed_version(book)


def next_version(manifest, book):
    entry = manifest.get(book)
    if not (isinstance(entry, dict) and entry.get("version")):
        # First time this book is published: use the seed as-is.
        return seed_version(book)
    ver = str(entry["version"])
    try:
        major, minor = ver.split(".", 1)
        return "%s.%d" % (major, int(minor) + 1)
    except (ValueError, TypeError):
        # Malformed stored version: fall back to seed.
        return seed_version(book)


def updated_date(manifest, book):
    entry = manifest.get(book)
    if isinstance(entry, dict) and entry.get("updated"):
        return str(entry["updated"])
    return ""


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    cmd, path, book = argv[0], argv[1], argv[2]
    manifest = load(path)

    if cmd == "current":
        print(current_version(manifest, book))
        return 0
    if cmd == "next":
        print(next_version(manifest, book))
        return 0
    if cmd == "updated":
        print(updated_date(manifest, book))
        return 0
    if cmd == "set":
        if len(argv) < 5:
            sys.stderr.write("set requires <version> <date>\n")
            return 2
        version, date = argv[3], argv[4]
        manifest[book] = {"version": version, "updated": date}
        # Deterministic key order for stable diffs.
        ordered = {k: manifest[k] for k in sorted(manifest)}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ordered, f, indent=2, sort_keys=True)
            f.write("\n")
        json.dump(ordered, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    sys.stderr.write("unknown command: %s\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
