#!/usr/bin/env python3
"""Append heading #fragment anchors to a split epub's navigation targets.

Kobo eReader TOC landing bug + the fix
--------------------------------------
Kobo's epub/kepub renderer only inserts a page break at spine-FILE boundaries;
it ignores in-file CSS page breaks (``page-break-before`` / ``break-before``).
So to get a visual page break before every recipe/category we must split each
one into its own file (Calibre ``--chapter``).

But when a chapter IS a whole file, Calibre writes the nav target as a BARE file
reference (``src="...split_432.html"`` with no ``#fragment``). Kobo lands a
bare-file target on the *previous* file's last page -- the off-by-one where a
recipe's TOC entry opens the end of the recipe before it.

Fix: rewrite every bare nav target so it points at the ``#id`` of the first
heading inside that file (``...split_432.html#hearty-beef-lasagna``). Kobo
scrolls to that in-file anchor correctly, so the page break (from the file
split) and the landing (from the fragment) both work.

This operates on an UNZIPPED epub directory, rewriting ``toc.ncx`` and any
``nav*.xhtml`` in place. Run it after ``ebook-convert`` (which produces the split
epub) and before re-zipping / kepubify.

Usage:
  fix_epub_nav.py <unzipped_epub_dir>
"""
import os
import re
import sys
import glob


def first_heading_id(html_path):
    """Return the id to anchor to for a content file: the id on the <section>
    that wraps the first h2/h3, else the id on the heading itself, else None."""
    try:
        html = open(html_path, encoding="utf-8").read()
    except OSError:
        return None
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S)
    section = body.group(1) if body else html
    m = re.search(r'<section id="([^"]+)"[^>]*>\s*<h[23]\b', section)
    if m:
        return m.group(1)
    m = re.search(r"<h[23][^>]*id=\"([^\"]+)\"", section)
    if m:
        return m.group(1)
    return None


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: fix_epub_nav.py <unzipped_epub_dir>\n")
        return 2
    root = argv[0]

    id_by_file = {}
    for pattern in ("**/*.html", "**/*.xhtml"):
        for f in glob.glob(os.path.join(root, pattern), recursive=True):
            hid = first_heading_id(f)
            if hid:
                id_by_file[os.path.basename(f)] = hid

    def fix_src(src):
        if "#" in src:
            return src
        hid = id_by_file.get(os.path.basename(src))
        return src + "#" + hid if hid else src

    rewritten = 0
    nav_files = (
        glob.glob(os.path.join(root, "**", "*.ncx"), recursive=True)
        + glob.glob(os.path.join(root, "**", "nav*.xhtml"), recursive=True)
    )
    for navfile in nav_files:
        txt = open(navfile, encoding="utf-8").read()
        new = re.sub(
            r'src="([^"]+\.x?html)"',
            lambda m: 'src="%s"' % fix_src(m.group(1)),
            txt,
        )
        new = re.sub(
            r'href="([^"]+\.x?html)"',
            lambda m: 'href="%s"' % fix_src(m.group(1)),
            new,
        )
        if new != txt:
            open(navfile, "w", encoding="utf-8").write(new)
            rewritten += 1

    sys.stderr.write(
        "fix_epub_nav: mapped %d heading id(s); rewrote %d nav file(s)\n"
        % (len(id_by_file), rewritten)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
