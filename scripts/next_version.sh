#!/usr/bin/env bash
# Print the NEXT version for a book based on existing git tags.
#
# Tag scheme: <Book>-vMAJOR.MINOR   (e.g. AirFryerRecipes-v1.3)
#
# Bump rule: take the highest existing MAJOR.MINOR for the book and increment
# MINOR. If the book has no tag yet, seed it:
#   - TheMessyChef (formerly RodneyFavoriteRecipes) was on the legacy global
#     series at v3.65; the rename bumps the major to 4, so its first new
#     version becomes 4.0.
#   - Every other book starts at 1.0.
#
# The computation is deterministic for a given tag state, so every job in a
# run that calls this gets the same answer until the release job creates the
# new tag.
#
# Usage: next_version.sh <BookName>
set -euo pipefail

BOOK="${1:?usage: next_version.sh <BookName>}"

# Ensure tags are available (the caller should have fetched them).
# Collect existing MAJOR.MINOR values for this book.
latest="$(git tag --list "${BOOK}-v*" \
  | sed -E "s/^${BOOK}-v//" \
  | grep -E '^[0-9]+\.[0-9]+$' \
  | sort -t. -k1,1n -k2,2n \
  | tail -n 1 || true)"

if [ -z "${latest}" ]; then
  # No tag yet: seed.
  if [ "${BOOK}" = "TheMessyChef" ]; then
    # Legacy series (formerly RodneyFavoriteRecipes) was at v3.65; the rename
    # bumps the major version to 4.
    echo "4.0"
  else
    echo "1.0"
  fi
  exit 0
fi

MAJOR="${latest%%.*}"
MINOR="${latest##*.}"
echo "${MAJOR}.$((MINOR + 1))"
