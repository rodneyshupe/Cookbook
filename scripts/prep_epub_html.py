#!/usr/bin/env python3
"""Prepare the generated single-file HTML for a clean Calibre -> epub conversion.

Problem this solves (Kobo TOC mis-landing):
  Recipes are separated by a standalone ``<p style="page-break-before: always"/>``
  paragraph (from ``includes/recipePageBreak.rst``). In the docutils HTML this
  paragraph is emitted as the LAST child of the PREVIOUS recipe's ``<section>``,
  immediately before its ``</section>``. When Calibre splits the epub, that
  trailing break makes Calibre migrate the previous section's ``id`` anchors into
  zero-height ghost ``<div>`` elements at the TOP of the next recipe's file. On
  Kobo, a TOC tap then lands on the tail of the previous recipe instead of the
  selected one.

Fix:
  Remove those standalone page-break paragraphs from the HTML *before* it is fed
  to ``ebook-convert``. With them gone, Calibre splits cleanly at each section
  boundary (verified: no ghost anchors, each recipe file starts with its own
  heading). Every recipe/category still becomes its own epub spine item, so each
  starts on a fresh page -- the visual break is preserved by the file split.

Scope:
  This only rewrites the HTML copy used for the epub build. The PDF build breaks
  via its own ``.. raw:: pdf`` directive, and the website build consumes the HTML
  separately, so neither is affected.

Usage:
  prep_epub_html.py <input.html> <output.html>
"""
import re
import sys

# Matches the standalone docutils page-break paragraph in both self-closing and
# paired forms, tolerant of whitespace after the colon.
PAGE_BREAK_P = re.compile(
    r'<p\s+style="page-break-before:\s*always"\s*/?>(?:\s*</p>)?',
    re.IGNORECASE,
)


def prepare(html: str) -> str:
    return PAGE_BREAK_P.sub("", html)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: prep_epub_html.py <input.html> <output.html>\n")
        return 2
    inp, outp = argv
    with open(inp, encoding="utf-8") as f:
        html = f.read()
    before = html.count("page-break-before")
    html = prepare(html)
    after = html.count("page-break-before")
    with open(outp, "w", encoding="utf-8") as f:
        f.write(html)
    sys.stderr.write(
        "prep_epub_html: removed %d standalone page-break paragraph(s) "
        "(%d -> %d page-break-before occurrences)\n" % (before - after, before, after)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
