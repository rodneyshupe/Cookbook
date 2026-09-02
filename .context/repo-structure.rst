==========================================
Cookbook Repository Structure & Publishing
==========================================

.. note::

   This is a context/reference document for humans and AI assistants
   (Claude, Gemini/Antigravity, Copilot, etc.). It is **not** part of any
   published book and is not included by any book's ``.. include::`` graph.
   Keep it up to date when the structure or build process changes.

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
