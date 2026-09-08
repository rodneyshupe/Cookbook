==========================================
Cookbook Repository Structure & Publishing
==========================================

.. note::

   This is a context/reference document for humans and AI coding assistants
   (whichever editor or agent is in use). It is **not** part of any published
   book and is not included by any book's ``.. include::`` graph. Keep it up to
   date when the structure or build process changes.

Purpose
=======

This repository is a personal cookbook. Recipes are authored once as
reStructuredText (RST) files and assembled into several distinct "books"
(PDF, HTML, EPUB, and a split website) by a GitHub Actions workflow. There
is no local build step required for authoring; pushing RST changes triggers
the build.

Top-level layout
================

::

   cookbook/
   ├── .github/workflows/publish_book.yml   CI: builds/publishes every book
   ├── .context/                            Reference docs (this folder)
   ├── Books/                               One source file per book (+ HTML variant)
   │   └── MealPlans/                       Week1..Week5 planner sections (MealPlanner only)
   ├── Recipes/                             All recipes, grouped by category
   ├── Appendix/                            Shared reference sections (A–H)
   ├── includes/                            Small shared RST snippets
   ├── assets/                              Stylesheets, covers, brand art
   │   └── brand/                           Logo / avatar source art
   ├── scripts/                             Build-support Python/bash
   ├── README.md                            Repo intro (uses assets/CollectionCover.jpg)
   └── .rstcheck.cfg                        rstcheck linting config

Key concept: books are assembled from includes
===============================================

A **book** is a source root ``Books/<Book>.rst`` (the PDF root) plus its
HTML sibling ``Books/<Book>.html.rst``. A book file is mostly front matter
(cover, title block, header/footer, table of contents) followed by a long
list of ``.. include::`` directives that pull in content.

Two include patterns exist:

- **Category aggregators** — ``Recipes/<Category>/Recipes.rst`` is an index
  that ``.. include::`` s every individual recipe in that category (with page
  breaks between them). ``TheMessyChef`` includes these aggregators.
- **Individual recipe includes** — some books (AirFryer, MealPlanner) include
  specific ``Recipes/<Category>/<Recipe>.rst`` files directly.

Because the same recipe files are shared across books, **editing a recipe
file changes every book that includes it.** Only ``Books/`` files and the
per-book planner files under ``Books/MealPlans/`` are book-specific.

The books
=========

TheMessyChef
   The full cookbook — the complete collection. Includes every category via
   the ``Recipes/<Category>/Recipes.rst`` aggregators, plus all Appendix
   sections (A–H). Source: ``Books/TheMessyChef.rst``. Its version series
   continues a legacy line (see Versioning) and was recently bumped to major
   v4 (first build ``TheMessyChef-v4.0``). Formerly named
   ``RodneyFavoriteRecipes``.

AirFryerRecipes
   Air-fryer subset. Opens with a short "Air Fryer" explainer section, then
   includes a hand-picked set of individual recipes, followed by a
   "Related Recipes" section (sauces/rubs referenced by the mains).

PressureCookerRecipes
   Electric-pressure-cooker (Instant Pot) subset. Same shape as AirFryer:
   an intro explainer, curated individual recipes, then Related Recipes.

SousVideRecipes
   Sous-vide subset. Same shape: intro explainer, curated recipes, Related
   Recipes.

MealPlannerBook
   A 5-week meal planner. Includes ``Books/MealPlans/Week1..5_Planner.rst``,
   each of which has a week overview, a **Weekly Shopping List**, and the
   week's recipes, followed by a flat "Related Recipes" reference section.
   Its PDF build uses a custom ToC transform (see below).

.. note::

   ``AirFryerRecipes``, ``PressureCookerRecipes``, and ``SousVideRecipes``
   share the front-matter shape: two ``PageBreak cutePage`` breaks before the
   title (so the title never lands on the cover page), a ``coverPage``
   background cover, and a ``:depth: 1`` table of contents. Keep new books
   consistent with this pattern.

Recipe categories
=================

Individual recipes live at ``Recipes/<Category>/<RecipeName>.rst`` in
PascalCase filenames. Each category folder also has a ``Recipes.rst``
aggregator. Categories (with nesting):

- ``Appetizers``
- ``Baking/Breads``, ``Baking/Cookies``
- ``Barbecue/Sauces``, ``Barbecue/SpiceRubs``
- ``Breakfast``
- ``Canapes-Tapas``
- ``Desserts``
- ``Dips-Salsa-Chutneys``
- ``Entrees/Beef``, ``Entrees/Lamb``, ``Entrees/Misc``, ``Entrees/Pasta``,
  ``Entrees/Pork``, ``Entrees/Poultry``, ``Entrees/Seafood``, ``Entrees/Veg``
- ``Jerky``
- ``PicklesAndPreserves``
- ``Salads``
- ``Sandwiches``
- ``Sauces``
- ``Sides``
- ``SmokedAndCured``
- ``SoupsAndStews``

Appendix
========

``Appendix/`` holds shared reference sections included (mainly) by
TheMessyChef: A_MealPlans, B_Conversions-Substitutions, C_Maintenance,
D_MeatAndPoultryTemperatureGuide, E_MeatCuringSalts, F_PantryItems,
G_RecipesToTry, G_RecipesUnderDevelopment, and H_UrbanFareRecipes (currently
commented out of the build).

Shared includes & assets
=========================

- ``includes/recipePageBreak.rst`` — the standard page break inserted between
  recipes (and after a week's shopping list). It emits a ``PageBreak
  recipePage`` for PDF and a page-break ``<p>`` for HTML. Reference it with
  the correct relative depth (``../includes/...`` from ``Books/``,
  ``../../includes/...`` from ``Books/MealPlans/``, ``../../../includes/...``
  from a category folder).
- ``assets/Cookbook.yaml`` / ``assets/Cookbook.css`` — the shared PDF/HTML
  stylesheets. The PDF cover image comes from ``coverPage.background`` in the
  YAML.
- ``assets/Cover.png`` — the shared default cover (PDF/EPUB fallback).
- ``assets/<Book>.Cover.png`` — optional per-book cover; used by the PDF (via
  a generated overlay stylesheet) and the EPUB when present.
- ``assets/brand/`` — logo/avatar source art (SVG + raster).

scripts/
========

- ``book_deps.py`` — computes each book's dependency set from the RST include
  graph plus shared assets, and decides which books to rebuild for a given set
  of changed files. Commands: ``list``, ``deps <Book>``, ``changed`` (with
  ``--matrix`` / ``--stdin``). A book name is derived purely from its
  ``Books/<Book>.rst`` filename. Its ``SHARED_ASSETS`` list names files whose
  change forces **every** book to rebuild — this includes the build-pipeline
  scripts (``book_deps.py``, ``prep_epub_html.py``, ``fix_epub_nav.py``,
  ``book_versions.py``) and the shared CSS/YAML/cover/workflow. If you add a
  script that changes output for all books, add it here, or a push that only
  touches it will rebuild nothing and the release will carry forward stale
  assets.
- ``book_versions.py`` — manifest-based version bookkeeping (replaces the old
  tag-based ``next_version.sh``). Reads/writes a ``manifest.json`` that records
  each book's ``version`` and last-updated ``date``. Commands: ``current``,
  ``next`` (bumps MINOR), ``updated``, ``set``. Seeds new books at ``1.0``
  (TheMessyChef at ``4.0`` to continue its legacy series).
- ``prep_epub_html.py`` — rewrites the epub's HTML copy for a Kobo-friendly
  build: strips stray in-body page-break paragraphs and inserts a
  ``<div class="pagebreak">`` before each recipe/category so Calibre splits one
  file per recipe (see "EPUB / Kobo pipeline"). Only used by ``build_epub``.
- ``fix_epub_nav.py`` — post-processes an unzipped split epub, appending each
  file's first-heading ``#id`` to the ``toc.ncx`` / nav targets so Kobo TOC
  jumps land on the heading instead of the previous file's tail.
- ``mealplanner_toc.py`` — a MealPlanner-only rst2pdf extension (docutils
  transform) that nests each recipe under its week in the PDF ToC. Loaded via
  ``--extension-module`` only for the MealPlanner PDF build.
- ``import_recipe.py`` — interactive helper that scrapes a recipe URL and
  writes a new ``Recipes/<Category>/<Recipe>.rst`` in the standard format,
  then inserts it into the category ``Recipes.rst``. Its output format is the
  canonical recipe skeleton (see ``recipe-style-guide.rst``).

How publishing works
=====================

The workflow ``.github/workflows/publish_book.yml`` runs on pushes that touch
``**.rst``, ``assets/**``, ``scripts/**``, or the workflow file (and on manual
dispatch).

Pipeline (per book, driven by a build matrix):

1. **detect_changes** — runs ``book_deps.py`` against the pushed diff to build
   a matrix of only the books that need rebuilding. Manual dispatch builds all
   books. (Changes under ``.context/`` match no book's deps, so they build
   nothing.)
2. **build_pdf** — ``rst2pdf`` on ``Books/<Book>.rst``. Selects a per-book
   stylesheet override if ``assets/<Book>.yaml`` exists (else
   ``assets/Cookbook.yaml``); generates a cover overlay stylesheet pointing at
   the per-book cover (else shared cover); for MealPlanner, adds the
   ``mealplanner_toc.py`` extension. Loads the ``preprocess`` extension.
3. **build_html** — ``rst2html5`` on ``Books/<Book>.html.rst``.
4. **build_epub** — produces both a plain ``.epub`` and a Kobo ``.kepub.epub``
   from the HTML output (see "EPUB / Kobo pipeline" below for the why). Steps:
   ``prep_epub_html.py`` → ``ebook-convert`` (split per recipe/category) →
   ``fix_epub_nav.py`` (repackaged) → ``kepubify``. Per-book title/comments
   metadata and the per-book (or shared) cover are applied here.
5. **build_website** — splits the HTML into a multi-page site.
6. **release** — a single rolling GitHub release tagged ``latest`` that always
   holds the complete set of book assets. Books built this run use their fresh
   artifacts; every other book's assets are carried forward from the previous
   ``latest`` release. Per-book versions and last-updated dates live in
   ``manifest.json`` (an asset on the release), and the release notes list the
   books updated this run (with new version) and the unchanged books (with the
   date they were last updated).
7. **publish_to_google / publish_to_dropbox / upload_website** — push the
   rebuilt books' artifacts to external storage. Google Drive and the GitHub
   ``release`` get the plain ``.epub``; **Dropbox (the Rakuten Kobo folder)
   gets the ``.kepub.epub``** because Kobo renders kepub with its native
   viewer.

Published output files are prefixed with ``TheMessyChef-`` (e.g.
``TheMessyChef-AirFryerRecipes.pdf``) except the main ``TheMessyChef`` book,
which keeps its bare name.

EPUB / Kobo pipeline (hard-won; read before touching build_epub)
================================================================

The epub build is more involved than a single ``ebook-convert`` call because
of how the **Kobo eReader** renders epubs. The behaviours below were verified
against real Calibre + kepubify output and on a physical Kobo; do not "simplify"
this pipeline without re-testing on a Kobo.

Facts about Kobo:

- Kobo only inserts a page break at **spine-file boundaries**. It ignores
  in-file CSS page breaks (``page-break-before`` / ``break-before``) and
  standalone break paragraphs. So to get a visual page break before every
  recipe/category, **each must be its own epub file** (Calibre ``--chapter``).
- When a chapter is a whole file, Calibre writes a **bare-file nav target**
  (no ``#fragment``). Kobo lands a bare-file target on the **previous** file's
  last page (an off-by-one). The nav must point at a ``#fragment`` on the
  first heading **inside** the file so Kobo scrolls to the heading.

The pipeline that satisfies both (in ``build_epub``):

1. ``scripts/prep_epub_html.py`` — on the epub's HTML copy only: strips the
   stray ``<p style="page-break-before">`` paragraphs **within the recipe body**
   (from the first ``<section>`` on; they corrupt anchors when Calibre splits),
   **preserves the front-matter breaks** (title / author-block / TOC page
   separators), and inserts a clean ``<div class="pagebreak">`` before each
   recipe (h3) and category (h2) section so Calibre splits one file per recipe.
2. ``ebook-convert`` — ``--chapter "//h:h2|//h:h3"`` (split per file),
   ``--chapter-mark none``, nested ``--level1-toc "//h:h2"`` /
   ``--level2-toc "//h:h3"``, and ``--extra-css`` for the ``.pagebreak`` class.
3. ``scripts/fix_epub_nav.py`` — on the **unzipped** epub: appends each file's
   first-heading ``#id`` to the ``toc.ncx`` / nav targets, then the workflow
   repackages (mimetype first and **stored**, per the epub spec).
4. ``kepubify`` (static Linux binary, downloaded in the step) — emits
   ``<name>.kepub.epub`` for Kobo.

Front-matter (Author / Revision / Date) gotcha
-----------------------------------------------

The HTML books are built with the **PyPI ``rst2html5`` (v2.x)**, which is a
different tool from the Docutils-bundled ``rst2html5``. v2.x treats a docutils
**bibliographic field list** (``:Author:`` / ``:Revision:`` / ``:Date:``) as
document metadata and emits it as ``<meta>`` tags in ``<head>`` — so it never
renders as a visible page. Therefore the ``*.html.rst`` front matter uses
**plain centered paragraphs**, not a field list and not an RST line block
(a line block becomes ``<pre class="line_block">``, which is monospace in Apple
Books). Keep front matter as::

   .. class:: center

   **Author:** Rodney Shupe <messychef@shupe.ca>

   .. class:: center

   **Revision:** |Revision|

   .. class:: center

   **Date:** |Date|

When validating an epub change locally you must use the **PyPI ``rst2html5``**
(``pip install rst2html5``), not the Docutils default, or the front-matter
behaviour will not reproduce.

Versioning
==========

There are no per-book git tags. Versions and last-updated dates are tracked in
``manifest.json``, stored as an asset on the rolling ``latest`` release and
maintained by ``book_versions.py``. On each run, books that were rebuilt get
their MINOR bumped and the date set to today; unchanged books carry their entry
forward. A book absent from the manifest is seeded (TheMessyChef at ``4.0`` to
continue its legacy series; every other book at ``1.0``). The version is also
injected into each book as the ``|Revision|`` substitution at build time.

Authoring workflow (quick reference)
====================================

- Add a recipe: create ``Recipes/<Category>/<Recipe>.rst`` (see
  ``recipe-style-guide.rst`` for format) and add an ``.. include::`` for it in
  that category's ``Recipes.rst`` (with a page break). ``import_recipe.py`` can
  do both from a URL.
- Add it to a specific book: reference the category aggregator (TheMessyChef)
  or the individual recipe (AirFryer/MealPlanner) from the book's source.
- Never hand-maintain page numbers; the ToC is generated.
- Do not edit shared recipe files to fix a single book — the change affects
  every book that includes them.

Testing & validation strategies
===============================

There is no unit-test suite; "testing" here means validating that RST changes
build cleanly and render as intended **before pushing**, since the real build
runs in CI on push. The strategies below are ordered from cheapest/fastest to
most thorough. Use the lightest one that covers your change.

1. Lint the RST (fast, always do this)
--------------------------------------

Run ``rstcheck`` with the repo config on the files you touched:

.. code-block:: bash

   python3 -m venv /tmp/venv && /tmp/venv/bin/pip install rstcheck
   /tmp/venv/bin/rstcheck --config .rstcheck.cfg <changed-file>.rst

- The config ignores the ``oddeven`` directive and the expected duplicate
  ``ingredients``/``directions`` target warnings.
- "Could not find line for literal block directive" is informational only, not
  an error; a clean run ends with ``Success! No issues detected``.
- Catches the common breakages: missing blank line before a list, heading
  underlines shorter than the title, and inline-literal / hyperlink syntax
  errors.

2. Check which books a change rebuilds (dependency sanity)
----------------------------------------------------------

Before/after editing, confirm your change maps to the books you expect (and
only those):

.. code-block:: bash

   # list all books
   python3 scripts/book_deps.py list
   # what a book depends on
   python3 scripts/book_deps.py deps MealPlannerBook
   # which books rebuild for a set of changed files
   echo "Recipes/Entrees/Pasta/CreamySausagePenne.rst" \
     | python3 scripts/book_deps.py changed --matrix --stdin

- A shared recipe or category ``Recipes.rst`` change should list every book
  that includes it. A ``Books/`` or ``Books/MealPlans/`` change should scope to
  the one book.
- Changes under ``.context/`` (or other non-dependency paths) resolve to zero
  books — expected, and confirms the docs don't trigger book rebuilds.

3. Build the affected book locally (rst2pdf)
--------------------------------------------

Reproduce the CI PDF build for one book. This is the highest-fidelity local
check for layout, ToC, covers, and page breaks.

.. code-block:: bash

   python3 -m venv /tmp/venv && /tmp/venv/bin/pip install rst2pdf pdfminer.six

   # CI generates these at build time; create stubs locally:
   printf '.. |Date| replace:: January 01, 2026\n\n.. |Revision| replace:: 0.0\n\n' \
     > temp_substitutions.rst
   printf 'pageTemplates:\n  coverPage:\n    background: assets/Cover.png\n' \
     > cover_overlay.yaml

   /tmp/venv/bin/rst2pdf Books/MealPlannerBook.rst \
     --break-level=1 --section-header-depth=1 --fit-background-mode=scale \
     --smart-quotes=0 --fit-literal-mode=shrink --repeat-table-rows \
     --stylesheets=assets/Cookbook.yaml,cover_overlay.yaml \
     --output=/tmp/out.pdf --strip-elements-with-class=handout \
     --extension-module=preprocess \
     --extension-module=scripts/mealplanner_toc.py   # MealPlanner only

   rm -f temp_substitutions.rst cover_overlay.yaml   # clean up (temp_substitutions.rst is gitignored)

- Mirror the exact flags the workflow uses (see ``publish_book.yml``). Drop the
  second ``--extension-module`` for books other than MealPlanner.
- ``temp_substitutions.rst`` is generated by CI (date + version) and is
  gitignored; the stub above is enough for a local render.
- A successful build exits 0 and produces the PDF. **Exit 0 alone is not proof
  the change is correct** — inspect the output (next step).

4. Inspect the rendered PDF programmatically (verify, don't assume)
-------------------------------------------------------------------

Use ``pdfminer.six`` to assert the specific outcome you changed, rather than
eyeballing. Examples proven useful in this repo:

- **ToC contents/indent** — extract text from the "Table of Contents" page and
  check entry labels and their x-offsets (nesting shows as larger x0).
- **Page breaks** — confirm content A ends on page N and content B starts on
  page N+1 (e.g. shopping list vs first recipe).
- **Cover selection** — compare the embedded image stream on the cover page
  between two builds to confirm the right cover is used.
- **Bullet rendering** — check that list items render as bullets (indented,
  ``•``) rather than a run-on paragraph.

.. code-block:: python

   from pdfminer.high_level import extract_pages
   from pdfminer.layout import LTTextContainer, LTTextLine
   for i, page in enumerate(extract_pages("/tmp/out.pdf"), 1):
       txt = "".join(e.get_text() for e in page if isinstance(e, LTTextContainer))
       if "Table of Contents" in txt:
           for el in page:
               if isinstance(el, LTTextContainer):
                   for line in el:
                       if isinstance(line, LTTextLine):
                           print(round(line.x0), line.get_text().strip())
           break

5. Build the HTML variant when it is affected
---------------------------------------------

For changes that touch the HTML root (``Books/<Book>.html.rst``) or HTML
rendering, mirror the ``build_html`` step:

.. code-block:: bash

   /tmp/venv/bin/pip install rst2html5
   /tmp/venv/bin/rst2html5 --stylesheet-inline=assets/Cookbook.css \
     --strip-elements-with-class=handout --strip-comments \
     Books/<Book>.html.rst /tmp/out.html

Guidelines
----------

- **Prefer editing/verifying over guessing.** When behavior depends on how
  rst2pdf/docutils assembles sections (heading levels, ToC depth, page
  templates), build and inspect rather than reasoning about it in the
  abstract — this repo has surprised us there before.
- **Isolate the variable.** To attribute an effect to your change, build once
  before and once after (or with/without the change) and diff the inspected
  output.
- **Keep the loop cheap.** For structural questions, a minimal standalone
  ``.rst`` that reproduces just the heading/list/table pattern builds far
  faster than the full book and isolates the behavior.
- **Clean up artifacts.** Remove ``temp_substitutions.rst``, ``cover_overlay.yaml``,
  ``*.build_temp``, generated PDFs/HTML, and any ``scripts/__pycache__`` before
  committing.
- **Match CI exactly.** The source of truth for flags, extensions, and
  stylesheet selection is ``.github/workflows/publish_book.yml``; when in
  doubt, copy the step you are validating.
