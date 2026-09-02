#!/usr/bin/env python3
"""Compute per-book build dependencies from the RST include graph, and decide
which books need rebuilding given a set of changed files.

A "book" is a source root under Books/ named <Book>.rst (the PDF root). Its
HTML sibling <Book>.html.rst is treated as part of the same book. A book's
dependency set is the transitive closure of its `.. include::` directives
(both roots), plus:
  - shared build assets that affect every book:
      assets/Cookbook.yaml, assets/Cookbook.css, assets/Cover.png,
      the publish workflow, and this script
  - the book's own optional style overrides:
      assets/<Book>.yaml, assets/<Book>.css

Usage:
  book_deps.py list                      -> list all book names
  book_deps.py deps <Book>               -> print dependency files for a book
  book_deps.py changed <file1> <file2>.. -> print JSON matrix of books to build
  book_deps.py changed --stdin           -> read newline-separated changed files
                                            from stdin, print JSON matrix

The "changed" command prints a JSON object:
  {"book": ["AirFryerRecipes", ...]}
suitable for use as a GitHub Actions matrix include list is produced by the
--matrix flag; by default it prints {"books": [...]}.
"""
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_DIR = os.path.join(REPO_ROOT, "Books")

INCLUDE_RE = re.compile(r"^\s*\.\.\s+include::\s+(.+?)\s*$")

# Assets whose change forces every book to rebuild. Paths are repo-relative.
SHARED_ASSETS = [
    "assets/Cookbook.yaml",
    "assets/Cookbook.css",
    "assets/Cover.png",
    ".github/workflows/publish_book.yml",
    "scripts/book_deps.py",
]


def rel(path):
    """Return a repo-root-relative, normalized POSIX path."""
    return os.path.relpath(os.path.normpath(path), REPO_ROOT).replace(os.sep, "/")


def list_books():
    books = []
    if not os.path.isdir(BOOKS_DIR):
        return books
    for name in sorted(os.listdir(BOOKS_DIR)):
        if name.endswith(".html.rst"):
            continue
        if name.endswith(".rst"):
            books.append(name[: -len(".rst")])
    return books


def include_closure(root_abs):
    """Transitive set of files reachable via `.. include::` from root_abs.
    Returns repo-relative paths, including the root itself. Missing includes
    are skipped (they are surfaced by the separate resolution check)."""
    seen = set()
    stack = [root_abs]
    while stack:
        p = os.path.abspath(stack.pop())
        if p in seen:
            continue
        seen.add(p)
        if not os.path.isfile(p):
            continue
        d = os.path.dirname(p)
        try:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    m = INCLUDE_RE.match(line)
                    if not m:
                        continue
                    target = m.group(1)
                    # temp_substitutions.rst is generated at build time; not a
                    # source dependency.
                    if os.path.basename(target) == "temp_substitutions.rst":
                        continue
                    stack.append(os.path.normpath(os.path.join(d, target)))
        except OSError:
            pass
    return {rel(p) for p in seen}


def book_deps(book):
    """Full repo-relative dependency set for a book."""
    deps = set()
    for suffix in (".rst", ".html.rst"):
        root = os.path.join(BOOKS_DIR, book + suffix)
        if os.path.isfile(root):
            deps |= include_closure(root)
    # shared assets
    deps.update(SHARED_ASSETS)
    # optional per-book style overrides
    deps.add("assets/%s.yaml" % book)
    deps.add("assets/%s.css" % book)
    # optional per-book epub cover override
    deps.add("assets/%s.Cover.png" % book)
    return deps


def changed_books(changed_files):
    changed = {c.strip().replace(os.sep, "/") for c in changed_files if c.strip()}
    result = []
    for book in list_books():
        deps = book_deps(book)
        if deps & changed:
            result.append(book)
    return result


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "list":
        if "--matrix" in argv[1:]:
            print(json.dumps({"include": [{"book": b} for b in list_books()]}))
        else:
            for b in list_books():
                print(b)
        return 0
    if cmd == "deps":
        if len(argv) < 2:
            sys.stderr.write("deps requires a book name\n")
            return 2
        for f in sorted(book_deps(argv[1])):
            print(f)
        return 0
    if cmd == "changed":
        rest = argv[1:]
        matrix = "--matrix" in rest
        rest = [a for a in rest if a != "--matrix"]
        if rest == ["--stdin"] or (not rest):
            files = sys.stdin.read().splitlines()
        else:
            files = rest
        books = changed_books(files)
        if matrix:
            print(json.dumps({"include": [{"book": b} for b in books]}))
        else:
            print(json.dumps({"books": books}))
        return 0
    sys.stderr.write("unknown command: %s\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
