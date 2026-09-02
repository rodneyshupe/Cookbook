===========================
Recipe Style & Format Guide
===========================

.. note::

   This is a context/reference document for humans and AI assistants
   (Claude, Gemini/Antigravity, Copilot, etc.). Its purpose is to define the
   **canonical, consistent format, tone, and voice** for recipe files so that
   existing recipes can be rewritten to match and new ones authored to fit.
   It is not part of any published book.

   When rewriting a recipe, preserve the actual cooking content (ingredients,
   quantities, steps, times, sources). Only normalize *format, structure,
   tone, and wording*. Do not invent quantities, times, or steps that are not
   in the source recipe.

Scope
=====

Recipes live at ``Recipes/<Category>/<RecipeName>.rst`` in reStructuredText.
They are shared across multiple books, so formatting must be self-contained
and consistent. See ``repo-structure.rst`` for how recipes are assembled.

The canonical recipe skeleton
=============================

Every recipe SHOULD follow this structure, in this order. Sections marked
*(optional)* are included only when they apply.

.. code-block:: rst

   Recipe Title
   ============

   +-----------------------+-----------------------+------------------------+-------------------+
   | Prep Time: 15 minutes | Cook Time: 25 minutes | Total Time: 40 minutes | Yield: 4 servings |
   +-----------------------+-----------------------+------------------------+-------------------+

   Source: `Display Name <https://example.com/recipe>`__

   Optional one- or two-sentence intro paragraph in a warm, plain voice.

   Equipment
   ---------
   Air Fryer

   Ingredients
   -----------

   - 1 pound boneless skinless chicken thighs, cut into bite-size pieces
   - 2 tablespoons olive oil
   - 1 teaspoon salt

   Directions
   ----------

   1. Combine the chicken, oil, and salt in a bowl and toss to coat.
   2. Cook until the chicken is browned and cooked through, about 8 minutes.

   Notes
   -----

   Optional tips, storage, or substitutions.

Element-by-element rules
========================

Title
-----

- First line of the file, in **Title Case**, followed by a ``=`` underline
  that is **at least as long as the title** (matching length preferred).
- Lowercase small connecting words (``with``, ``and``, ``of``, ``the``, ``a``,
  ``in``) unless they start the title.
- The title is the human recipe name and may differ from the PascalCase
  filename; parentheticals are fine (``Cubanos (Cuban Sandwiches)``).

Metadata table
--------------

- An RST grid table with one data row, placed directly under the title.
- Each cell is ``Label: value``. Use these labels, in this order, including
  only the ones that apply:
  ``Prep Time:`` → ``Cook Time:`` → ``Total Time:`` → ``Yield:``
- Additional time labels, when relevant, go **before** ``Yield:`` using the
  same ``X Time:`` pattern: ``Marinate Time:``, ``Cure Time:``, ``Rest Time:``.
- Times read as human durations: ``15 minutes``, ``1 hour``, ``1 1/2 hours``,
  ``overnight``, ``7 days``. Never leave a ``TBD`` placeholder — omit the
  column if unknown.
- ``Yield:`` describes what the recipe makes. Prefer a count + noun:
  ``4 servings``, ``1 loaf``, ``24 poppers``, ``about 3/4 cup``. Use lowercase
  ``serves`` only inside prose-style yields (``enough for 2 lbs of wings``).
  Do **not** add a separate "Servings" or "Makes" column — fold that into
  ``Yield:``.

Source *(optional)*
-------------------

- A single line placed **after** the metadata table (and before any intro).
- Web source: ``Source: `Display Name <URL>`__`` — use the site/author name as
  display text, not a bare URL.
- Book/print source: ``Source: <Title> by <Author>`` in plain text.
- Spell publisher names consistently (e.g. ``Cook's Country``,
  ``Cook's Illustrated`` — with the apostrophe).
- Omit entirely for original/family recipes.

Intro paragraph *(optional)*
----------------------------

- One or two sentences, only when it adds real value (backstory, a key
  technique note, or serving context).
- Placed after the Source line (or after the table if no Source).
- Warm and personal but concise. First person is fine for family notes
  (``I got this from my friend Scott``). Avoid marketing fluff.

Equipment *(optional)*
----------------------

- Use only for a defining piece of gear (Air Fryer, Smoker, Waffle Iron,
  Electric Pressure Cooker). Heading ``Equipment`` with ``-`` underline; body
  is a plain line (or short bullet list), placed **before** Ingredients.

Ingredients
-----------

- Heading ``Ingredients`` with a ``-`` underline of matching length.
- **One space** after the hyphen bullet: ``- 1 cup milk`` (never ``-  1``).
- Quantities use ASCII fractions with a space after a whole number:
  ``1 1/2 cups``, ``1/4 cup``, ``2 1/2 pounds``. Ranges use a hyphen with
  spaces: ``1/2 - 3/4 teaspoon``.
- **Spell out units**: ``tablespoon``/``tablespoons``, ``teaspoon``, ``cup``,
  ``pound``, ``ounce`` (not ``Tbsp``, ``tsp``, ``lb``, ``oz``). Keep any
  metric equivalents the source gives in parentheses: ``1 1/2 pounds (750 g)``.
- Preparation notes follow the item, comma-separated:
  ``2 cloves garlic, minced``.
- Sub-group multi-part recipes with a caret (``^``) sub-heading whose
  underline matches the heading length:

  .. code-block:: rst

     Ingredients
     -----------

     Marinade
     ^^^^^^^^

     - 1/2 cup plain yogurt

     Curry
     ^^^^^

     - 1 cup heavy cream

Directions
----------

- Heading ``Directions`` with a ``-`` underline of matching length.
- An **ordered list** (``1.``, ``2.``, ...), numbered even when there is only
  one step (do not use a bare paragraph).
- **Imperative voice**: ``Combine...``, ``Heat...``, ``Stir in...``.
- Wrap long steps at ~78–80 characters, indenting continuation lines **3
  spaces** so they align under the text of the first line (past the number,
  period, and space):

  .. code-block:: rst

     1. Heat a large skillet over medium heat. Cook the beef until it starts
        to brown, 3 to 4 minutes.

- **Temperature format**: ``425F`` (number immediately followed by a capital
  ``F``, no space, no degree symbol). Normalize other forms
  (``375 degrees F``, ``350 F degrees``, ``325 degrees``) to this.
- For multi-phase recipes, prefix steps with a short label:
  ``1. For the soup:`` … ``5. To serve:``.
- A short trailing serving line after the list is allowed, for example:

  .. code-block:: rst

     Serve with `Garlic Bread <#garlic-bread>`__.

Notes / Variations *(optional)*
-------------------------------

- ``Notes`` (plural) for tips, storage, make-ahead, substitutions — placed
  after Directions.
- ``Variations`` (plural, not ``Variation``) for alternate versions. Each
  variant uses a caret (``^``) sub-heading. When a variant needs its own
  steps, a short numbered list under it is fine.

Cross-references
----------------

- Link to another recipe with an anonymous hyperlink to its slug anchor. The
  slug is the target recipe title, lowercased with spaces replaced by hyphens:

  .. code-block:: rst

     3 tablespoons `Buffalo Sauce <#buffalo-sauce>`__
- These may appear in ingredient bullets or in directions.

Tone & voice
============

- **Warm, practical, and unfussy** — like a knowledgeable friend sharing a
  family recipe, not a glossy magazine.
- **Direct and confident** in directions (imperative, active).
- **Concise**: trim filler. Keep useful sensory/technique cues
  (``until golden``, ``until fragrant``) and doneness signals with times
  (``about 8 minutes``).
- **Consistent terminology (cookbook-wide)**: use the same name for a given
  ingredient or tool across **every** recipe, not just within one file. Pick
  one term (e.g. ``cilantro``, not ``coriander``; ``skillet``, not ``frying
  pan``) and use it everywhere; optionally note an alternate name once, in
  parentheses, at first use in a recipe. When adding or rewriting a recipe,
  match the term already used by the rest of the cookbook rather than
  introducing a synonym.
- **Consistent spelling (cookbook-wide)**: standardize on Canadian English
  across all recipes (``flavour``, ``colour``, ``caramelise`` →
  keep ``-our``/``-ise`` forms). Apply this everywhere, not per file — when you
  touch a recipe that uses a different spelling, normalize it to the cookbook
  standard.

.. note::

   Terminology and spelling are **global** conventions. A change is only
   "consistent" if it agrees with the rest of the cookbook, so when in doubt
   grep the ``Recipes/`` tree for how a term is already spelled/used and follow
   the majority (or fix the outliers to match the chosen standard).

Known inconsistencies to normalize
===================================

When reformatting existing recipes, watch for and fix these (all observed in
the current corpus):

1. **Bullet spacing** — many files put two spaces after the hyphen bullet.
   Normalize to exactly one space after the hyphen.
2. **Temperature format** — ``375 degrees F``, ``350 F degrees``,
   ``325 degrees`` → ``375F`` / ``350F`` / ``325F``.
3. **Unit abbreviations** — ``Tbsp``, ``Tbsp.``, ``tsp``, ``lb``, ``lbs``,
   ``oz`` → spelled out.
4. **Yield phrasing** — mixed ``serves 12`` / ``Serves 4`` / ``4 servings``.
   Prefer count + noun; reserve prose yields for sauces/marinades.
5. **Underline lengths** — title (``=``), section (``-``), and sub-section
   (``^``) underlines are often too short or too long. Match the heading text
   length.
6. **Missing section headings** — a few files (e.g. some jerky marinades) drop
   the ``Ingredients``/``Directions`` headings or trail off with a dangling
   line. Restore the full skeleton.
7. **Source placement / naming** — move ``Source:`` to just after the table;
   use display-name links (not bare URLs); spell publishers consistently.
8. **Sub-grouping** — standardize ingredient/variation sub-groups on caret
   (``^``) sub-headings (not bold ``**For the sauce:**`` labels).
9. **Stray whitespace** — remove trailing spaces and collapse extra blank
   lines; keep exactly one blank line between blocks (and the RST-required
   blank line between a bold label or heading and a following list).
10. **Typos from imports** — e.g. ``%cup`` (should be a fraction), ``Day2``
    (should be ``Day 2``). Fix on sight.

RST reminders (so rewrites still build)
=======================================

- A bullet or numbered list MUST be preceded by a blank line.
- Headings need an underline (matching character per level: ``=`` title,
  ``-`` section, ``^`` sub-section) at least as long as the text.
- ``.rstcheck.cfg`` ignores the ``oddeven`` directive and the duplicate
  ``ingredients``/``directions`` implicit-target warnings (expected because
  every recipe repeats those headings).
- Keep the file self-contained; do not rely on another recipe's definitions.
