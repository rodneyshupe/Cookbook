#!/usr/bin/env python3
"""Prepare the generated single-file HTML for a Kobo-friendly epub conversion.

Kobo TOC / page-break behaviour (verified against real Calibre + kepubify output)
---------------------------------------------------------------------------------
Kobo's epub/kepub renderer only inserts a page break at spine-FILE boundaries;
it ignores in-file CSS page breaks (``page-break-before`` / ``break-before``) and
ignores standalone break paragraphs. So to get a visual page break before every
recipe and category, each one must end up as its OWN epub file. Calibre splits a
file wherever it detects a page break, so we need a real break element before
each recipe/category heading to make Calibre split per recipe.

The docutils output has two problems for this:
  1. Recipes are separated by a standalone ``<p style="page-break-before:
     always"/>`` that docutils emits as the LAST child of the PREVIOUS recipe's
     ``<section>``. When Calibre splits there, it migrates the previous section's
     id anchors into zero-height ghost ``<div>`` elements at the top of the next
     file, which corrupts navigation.
  2. That break is a trailing sibling of the wrong section, not a clean marker
     before the next heading.

What this script does
---------------------
  1. Remove the stray standalone page-break paragraphs that appear WITHIN the
     recipe/category content (i.e. from the first <section> onward), which fixes
     the ghost anchors. The front-matter page breaks BEFORE the first <section>
     (they separate the title page, the Author/Revision/Date block, and the main
     Table of Contents into their own pages) are PRESERVED.
  2. Insert a clean ``<div class="pagebreak"></div>`` immediately BEFORE each
     ``<section>`` that wraps a recipe (h3) or category (h2) heading. This gives
     Calibre a clean, correctly-placed break so it splits into one file per
     recipe/category -- which is what makes Kobo render a page break there.

Navigation targets still need a ``#fragment`` fix after conversion (see
``fix_epub_nav.py``), because Calibre writes bare-file nav targets for whole-file
chapters and Kobo lands those on the previous file's tail.

Scope:
  Only the epub's HTML copy is rewritten. The PDF build breaks via its own
  ``.. raw:: pdf`` directive and the website build consumes the HTML separately,
  so neither is affected.

Usage:
  prep_epub_html.py <input.html> <output.html>
"""
import re
import sys

# Standalone docutils page-break paragraph, self-closing or paired.
PAGE_BREAK_P = re.compile(
    r'<p\s+style="page-break-before:\s*always"\s*/?>(?:\s*</p>)?',
    re.IGNORECASE,
)

# A <section> that directly wraps a recipe (h3) or category (h2) heading.
SECTION_BEFORE_HEADING = re.compile(
    r'(<section id="[^"]*"[^>]*>\s*<h[23]\b)'
)

BREAK_DIV = '<div class="pagebreak"></div>'


def prepare(html: str):
    # Split the document at the first <section ...> so we only touch the recipe
    # body. Everything before it is front matter (title, Author/Revision/Date
    # field list, main TOC) whose page breaks must be preserved so each stays on
    # its own page.
    first = re.search(r'<section\b', html)
    if first:
        head, tail = html[: first.start()], html[first.start():]
    else:
        head, tail = "", html

    removed_before = tail.count("page-break-before")
    tail = PAGE_BREAK_P.sub("", tail)
    removed = removed_before - tail.count("page-break-before")

    inserted = 0

    def repl(m):
        nonlocal inserted
        inserted += 1
        return BREAK_DIV + m.group(1)

    tail = SECTION_BEFORE_HEADING.sub(repl, tail)
    return head + tail, removed, inserted


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: prep_epub_html.py <input.html> <output.html>\n")
        return 2
    inp, outp = argv
    with open(inp, encoding="utf-8") as f:
        html = f.read()
    html, removed, inserted = prepare(html)
    with open(outp, "w", encoding="utf-8") as f:
        f.write(html)
    sys.stderr.write(
        "prep_epub_html: removed %d stray page-break paragraph(s); "
        "inserted %d break div(s) before headings\n" % (removed, inserted)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
