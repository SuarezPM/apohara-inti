#!/usr/bin/env bash
# US-T-07: Submission char-count gate.
# Asserts: tagline ≤80, short pitch ≤200, long description ≤2000.
# Per file: 4 paste-ready variants (techex/milan × 9vendor/12vendor).

set -u

REPO=$(dirname $(dirname $(realpath "$0")))
SUBS_DIR="$REPO/docs/submissions"
EXIT=0

extract_section() {
  local file="$1" header="$2"
  awk -v hdr="$header" '
    /^## Field:/ { current = $0; next }
    /^## / && !/^## Field:/ { current = ""; next }
    /^```/ { in_code = !in_code; if (in_code && current ~ hdr) { capture=1; next } else { capture=0; next } }
    capture { print }
  ' "$file"
}

check_file() {
  local file="$1" label="$2"
  [ -f "$file" ] || { echo "MISSING $file"; EXIT=1; return; }
  local tagline_n=$(extract_section "$file" "Tagline" | wc -c)
  local pitch_n=$(extract_section "$file" "Short pitch" | wc -c)
  local longdesc_n=$(extract_section "$file" "Long description" | wc -c)

  printf "%-30s tagline=%d/80 pitch=%d/200 longdesc=%d/2000 " "$label" "$tagline_n" "$pitch_n" "$longdesc_n"
  local fail=0
  [ "$tagline_n" -gt 81 ] && { printf " ✗ TAGLINE_OVER"; fail=1; EXIT=1; }
  [ "$pitch_n" -gt 201 ] && { printf " ✗ PITCH_OVER"; fail=1; EXIT=1; }
  [ "$longdesc_n" -gt 2001 ] && { printf " ✗ LONGDESC_OVER"; fail=1; EXIT=1; }
  [ "$fail" -eq 0 ] && printf " ✓ OK"
  printf "\n"
}

echo "=== US-T-07 Submission char-count gate ==="
check_file "$SUBS_DIR/techex-2026-submission.9vendor.md"   "techex 9-vendor"
check_file "$SUBS_DIR/techex-2026-submission.12vendor.md"  "techex 12-vendor"
check_file "$SUBS_DIR/milan-aiweek-2026-submission.9vendor.md" "milan 9-vendor"
check_file "$SUBS_DIR/milan-aiweek-2026-submission.12vendor.md" "milan 12-vendor"

exit $EXIT
