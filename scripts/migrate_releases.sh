#!/usr/bin/env bash
# ONE-TIME migration from the old per-book release/tag scheme to the new rolling
# `latest` release + manifest.json scheme.
#
# What it does, in order:
#   1. Seeds manifest.json from the current highest per-book version tags
#      (<Book>-vMAJOR.MINOR), preserving your existing version numbers. The
#      "updated" date is set to each tag's commit date (best-effort), else today.
#   2. Creates/updates the rolling `latest` release and uploads manifest.json
#      (plus any book assets you pass in, though normally the next CI run fills
#      those in).
#   3. (Optional, destructive) Deletes the old per-book releases + tags.
#   4. (Optional, destructive) Deletes the legacy global vMAJOR.MINOR tags.
#
# Requirements: run from a clone with `gh` authenticated (gh auth login) and
# the remote fetched (git fetch --tags). Nothing here runs in CI automatically.
#
# Usage:
#   scripts/migrate_releases.sh seed         # write manifest.json locally (safe)
#   scripts/migrate_releases.sh publish      # seed + create `latest` release
#   scripts/migrate_releases.sh cleanup-books  # DELETE old per-book releases+tags
#   scripts/migrate_releases.sh cleanup-legacy # DELETE legacy vX.Y tags (no releases)
#
# Review the manifest after `seed` before running `publish` or any `cleanup`.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
MANIFEST="manifest.json"
TODAY="$(date +%F)"

books() { python3 scripts/book_deps.py list; }

seed() {
  echo "{}" > "$MANIFEST"
  git fetch --tags --quiet || true
  for BOOK in $(books); do
    # Highest MAJOR.MINOR tag for this book.
    latest="$(git tag --list "${BOOK}-v*" \
      | sed -E "s/^${BOOK}-v//" \
      | grep -E '^[0-9]+\.[0-9]+$' \
      | sort -t. -k1,1n -k2,2n \
      | tail -n 1 || true)"
    if [ -z "$latest" ]; then
      echo "  ${BOOK}: no existing tag; leaving unseeded (CI will seed on first build)."
      continue
    fi
    # Commit date of that tag, if resolvable; else today.
    tagref="${BOOK}-v${latest}"
    date="$(git log -1 --format=%cs "$tagref" 2>/dev/null || echo "$TODAY")"
    [ -n "$date" ] || date="$TODAY"
    python3 scripts/book_versions.py set "$MANIFEST" "$BOOK" "$latest" "$date" >/dev/null
    echo "  ${BOOK}: v${latest} (updated ${date})"
  done
  echo "Wrote $MANIFEST:"
  cat "$MANIFEST"
}

publish() {
  [ -f "$MANIFEST" ] || seed
  echo "Creating/updating the 'latest' release with manifest.json ..."
  {
    echo "Cookbook release — ${TODAY}"
    echo ""
    echo "Rolling release; see manifest.json for per-book versions."
  } > release_notes.md
  if gh release view latest >/dev/null 2>&1; then
    gh release upload latest "$MANIFEST" --clobber
    gh release edit latest --notes-file release_notes.md --title "Cookbook (latest)"
  else
    gh release create latest "$MANIFEST" \
      --title "Cookbook (latest)" \
      --notes-file release_notes.md \
      --latest
  fi
  echo "Done. The next CI run will attach the book assets."
}

cleanup_books() {
  echo "Deleting old per-book releases and tags ..."
  for BOOK in $(books); do
    for tag in $(git tag --list "${BOOK}-v*"); do
      echo "  removing $tag"
      gh release delete "$tag" --yes --cleanup-tag 2>/dev/null \
        || git push origin ":refs/tags/$tag" 2>/dev/null || true
    done
  done
  echo "Per-book cleanup complete."
}

cleanup_legacy() {
  echo "Deleting legacy global vMAJOR.MINOR tags ..."
  for tag in $(git tag --list 'v[0-9]*.[0-9]*'); do
    echo "  removing $tag"
    gh release delete "$tag" --yes --cleanup-tag 2>/dev/null \
      || git push origin ":refs/tags/$tag" 2>/dev/null || true
  done
  echo "Legacy cleanup complete."
}

case "${1:-}" in
  seed)           seed ;;
  publish)        publish ;;
  cleanup-books)  cleanup_books ;;
  cleanup-legacy) cleanup_legacy ;;
  *)
    echo "usage: $0 {seed|publish|cleanup-books|cleanup-legacy}" >&2
    exit 2 ;;
esac
