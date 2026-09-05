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
  ``Books/<Book>.rst`` filename.
- ``next_version.sh`` — prints the next ``<Book>-vMAJOR.MINOR`` version from
  existing git tags (bumps MINOR; seeds new books at ``1.0``; TheMessyChef is
  seeded to continue its legacy series).
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
4. **build_epub** — ``calibre`` (``ebook-convert``) from the HTML output, with
   per-book title/comments metadata and the per-book (or shared) cover.
5. **build_website** — splits the HTML into a multi-page site.
6. **release** — one GitHub release per book, tagged ``<Book>-v<version>``,
   with the PDF/EPUB/website assets attached.
7. **publish_to_google / publish_to_dropbox / upload_website** — push
   artifacts to external storage.

Versioning
==========

Releases are tagged ``<Book>-vMAJOR.MINOR``. ``next_version.sh`` takes the
highest existing tag for a book and increments MINOR; a book with no tag is
seeded (TheMessyChef continues its legacy series; others start at ``1.0``).
The first release after a bump therefore comes from the seed logic, and normal
MINOR bumps follow.

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
