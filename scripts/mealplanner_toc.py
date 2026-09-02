# rst2pdf extension: nest each meal-plan recipe under its week in the ToC.
#
# The Meal Planner book includes shared recipe files whose titles use the
# top-level "=" underline. In the assembled document that makes every recipe
# title a sibling of the "Week N" headings, so a plain ``.. contents::`` lists
# weeks and recipes flat, and any depth that reveals recipe names also reveals
# each recipe's own "Ingredients"/"Directions" sub-headings.
#
# This extension registers a docutils transform that runs before the built-in
# Contents transform (priority 720) and re-parents each top-level recipe
# section so it becomes a child of the preceding "Week N" section. Recipe
# titles then sit one level below the week (and their Ingredients/Directions a
# further level down), so ``.. contents:: :depth: 2`` renders:
#
#     Week 1: ...
#         Weekly Shopping List
#         Creamy Sausage Penne
#         Fish Tacos
#     Week 2: ...
#         ...
#
# with automatically generated page numbers and no Ingredients/Directions
# clutter. Only the ToC structure changes; the rendered body is untouched.
#
# Load it in the PDF build with: ``-e scripts/mealplanner_toc.py``.

from docutils import nodes
from docutils.transforms import Transform
from docutils.parsers.rst import Parser as _RstParser


class NestRecipesUnderWeek(Transform):
    # Must run before docutils' Contents transform (default_priority 720) so
    # the ToC is built from the re-parented tree.
    default_priority = 700

    def apply(self):
        document = self.document
        top_sections = [
            child for child in document.children if isinstance(child, nodes.section)
        ]
        # Sections whose recipes should be nested beneath them: each "Week N"
        # and the trailing "Related Recipes" reference list. Recipes following
        # such a parent become its children so their titles sit one ToC level
        # down and their Ingredients/Directions a further level down.
        current_parent = None
        for section in top_sections:
            title = section.next_node(nodes.title)
            text = title.astext() if title is not None else ""
            if text.startswith("Week ") or text.startswith("Related Recipes"):
                current_parent = section
                continue
            if current_parent is not None:
                # A recipe section following a parent: nest it under the parent.
                document.remove(section)
                current_parent += section


_orig_get_transforms = _RstParser.get_transforms


def _patched_get_transforms(self):
    return _orig_get_transforms(self) + [NestRecipesUnderWeek]


# Registering here (at import time) means the transform is active as soon as
# rst2pdf imports this extension module.
_RstParser.get_transforms = _patched_get_transforms


def install(createpdf, options):
    # The extension API calls install() after parsing the command line. All
    # wiring happens at import time above, so there is nothing to do here.
    pass
