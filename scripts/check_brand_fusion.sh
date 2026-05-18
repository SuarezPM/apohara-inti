#!/usr/bin/env bash
# Apohara PROBANT Fusion Sprint — Brand CI Gate
# Per Architect+Critic review, mandatory before any frontend commit.
set -u
EXIT=0
FRONTEND=/home/linconx/Documentos/apohara-inti/packages/frontend/src
NEXTJS=/home/linconx/Documentos/apohara-inti/packages/frontend-nextjs/app

# Forbidden teal-range hex codes (PLAYBOOK SOAR uses teal)
TEAL_PATTERNS=(
  "#0EA5A0" "#14B8A6" "#0D9488" "#5EEAD4" "#06B6D4"
  "#0891B2" "#0E7490" "#155E75" "#164E63" "#22D3EE"
  "#67E8F9" "#A5F3FC" "#CFFAFE" "#ECFEFF"
)

echo "=== Forbidden teal-range hex scan (PLAYBOOK SOAR palette) ==="
for hex in "${TEAL_PATTERNS[@]}"; do
  HITS=$(grep -rni "$hex" "$FRONTEND" "$NEXTJS" --include="*.ts" --include="*.tsx" --include="*.css" --include="*.html" 2>/dev/null || true)
  if [ -n "$HITS" ]; then
    echo "VIOLATION: teal hex $hex found:"
    echo "$HITS"
    EXIT=1
  fi
done
[ $EXIT -eq 0 ] && echo "  ✓ No teal contamination"

echo ""
[ $EXIT -eq 0 ] && echo "✅ brand fusion gate PASS" || echo "❌ brand fusion gate FAIL"
exit $EXIT
