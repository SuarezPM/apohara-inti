#!/usr/bin/env bash
# Apohara PROBANT Fusion Sprint — Honesty CI Gate
# Per CRITIC review of fusion plan, mandatory before any commit.
set -u
EXIT=0
APOHARA_AEGIS=/home/linconx/Documentos/apohara-aegis
APOHARA_INTI=/home/linconx/Documentos/apohara-inti

# Rule 1: No "Mythos access" claims outside boundary contexts
echo "=== Rule 1: Mythos boundary language ==="
HITS=$(grep -rnE "(Powered by Mythos|Mythos-approved|Anthropic-approved|Mythos access granted)" \
  "$APOHARA_AEGIS" "$APOHARA_INTI" \
  --include="*.md" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.html" \
  2>/dev/null \
  | grep -v MYTHOS_READY.md \
  | grep -v '\.omc/' \
  | grep -v "\"not" \
  | grep -v "not \"" \
  || true)
if [ -n "$HITS" ]; then
  echo "VIOLATION: Forbidden Mythos access claim found:"
  echo "$HITS"
  EXIT=1
else
  echo "  ✓ No forbidden Mythos access claims"
fi

# Rule 2: "first implementation" claims require prior-art.md
echo "=== Rule 2: 'first implementation' requires prior-art evidence ==="
HITS=$(grep -rnE "first[- ]implementation" "$APOHARA_INTI"/docs "$APOHARA_AEGIS" --include="*.md" 2>/dev/null || true)
if [ -n "$HITS" ]; then
  if [ ! -f "$APOHARA_INTI/docs/research/prior-art-nist-agentic-profile.md" ]; then
    echo "VIOLATION: 'first implementation' claimed without prior-art evidence"
    echo "$HITS"
    EXIT=1
  else
    echo "  ✓ 'first implementation' claims backed by prior-art.md"
  fi
else
  echo "  ✓ No 'first implementation' claims found"
fi

# Rule 3: No PLAYBOOK-style overclaim of test counts
# (Future: check pytest --collect-only against documented counts)
echo "=== Rule 3: Test count consistency (placeholder for fusion build-out) ==="
echo "  ✓ Placeholder — full check ships in US-86"

# Rule 4: No "v2" labels in user-facing content (Pablo's directive)
echo "=== Rule 4: Single-product naming (no 'v2' labels) ==="
HITS=$(grep -rnE "(PROBANT v2|PROBANT 2\.0|version 2\.0|apohara_probant/v2|apohara_app)" \
  "$APOHARA_INTI"/{docs,README.md,MYTHOS_READY.md,CHANGELOG.md} \
  "$APOHARA_AEGIS"/README.md "$APOHARA_AEGIS"/CHANGELOG.md \
  2>/dev/null | grep -v "FUSION-PLAN" | grep -v "SESSION-MEMORY" || true)
if [ -n "$HITS" ]; then
  echo "VIOLATION: 'v2' labeling found (Pablo directive: single product 'Apohara PROBANT'):"
  echo "$HITS"
  EXIT=1
else
  echo "  ✓ No 'v2' labeling in user-facing docs"
fi

echo ""
[ $EXIT -eq 0 ] && echo "✅ honesty fusion gate PASS" || echo "❌ honesty fusion gate FAIL"
exit $EXIT
