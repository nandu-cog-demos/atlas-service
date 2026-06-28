#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# reset-demo.sh — one-command reset for Devin Review demo environment
#
# Usage:
#   ./scripts/reset-demo.sh            # full reset (close PRs, reset branches, recreate PRs)
#   ./scripts/reset-demo.sh --light    # lightweight reset (close + reopen PRs only)
#
# Prerequisites:
#   - gh CLI authenticated with repo access
#   - Push access to nandu-cog-demos/atlas-service
#
# The script is idempotent — safe to run repeatedly.
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="nandu-cog-demos/atlas-service"
LIGHT=false

if [[ "${1:-}" == "--light" ]]; then
  LIGHT=true
fi

echo "══════════════════════════════════════════════"
echo "  Atlas Service — Demo Reset"
echo "  Mode: $(if $LIGHT; then echo 'light (close/reopen PRs)'; else echo 'full (branches + PRs)'; fi)"
echo "══════════════════════════════════════════════"
echo ""

# ── Phase 1: Close all existing demo PRs ────────────────────────────
echo "▸ Phase 1: Closing existing demo PRs..."

for branch in pr1-operator-settings pr2-refactor-inference pr3-batch-scoring pr4-status-badge; do
  pr_number=$(gh pr list --repo "$REPO" --head "$branch" --state open --json number --jq '.[0].number' 2>/dev/null || true)
  if [[ -n "$pr_number" ]]; then
    echo "  Closing PR #${pr_number} (${branch})..."
    gh pr close "$pr_number" --repo "$REPO" 2>/dev/null || true
  else
    echo "  No open PR for ${branch} — skipping."
  fi
done

echo ""

# ── Phase 2: Reset branches ────────────────────────────────────────
if ! $LIGHT; then
  echo "▸ Phase 2: Resetting working branches to seed state..."

  git push -f origin seed/pr1-operator-settings:pr1-operator-settings
  git push -f origin seed/pr2-refactor-inference:pr2-refactor-inference
  git push -f origin seed/pr3-batch-scoring:pr3-batch-scoring
  git push -f origin seed/pr4-status-badge:pr4-status-badge

  echo ""
  echo "▸ Resetting merge-target to main..."
  git push -f origin main:merge-target

  echo ""
else
  echo "▸ Phase 2: Skipped (light mode — branches unchanged)."

  # In light mode, push a trivial empty commit to each working branch
  # so PRs get new head SHAs and Devin auto-review triggers afresh.
  echo "  Pushing trigger commits to working branches..."
  for branch in pr1-operator-settings pr2-refactor-inference pr3-batch-scoring pr4-status-badge; do
    git checkout "$branch" 2>/dev/null
    git commit --allow-empty -m "chore: trigger re-review"
    git push origin "$branch"
    echo "  ✓ ${branch}"
  done
  git checkout main 2>/dev/null
  echo ""
fi

# ── Phase 3: Recreate PRs ──────────────────────────────────────────
echo "▸ Phase 3: Opening fresh demo PRs..."

echo ""
echo "  Creating PR #1: Add operator settings endpoint..."
gh pr create \
  --repo "$REPO" \
  --head pr1-operator-settings \
  --base main \
  --title "Add operator settings endpoint" \
  --body "$(cat <<'EOF'
## Summary

Add a PATCH endpoint for operators to update their dashboard preferences
(display name, theme, notifications, default map zoom) and wire up the
corresponding React component.

### Changes
- **Backend**: new PATCH handler in `src/api/routes/settings.py`
- **Frontend**: updated `OperatorSettings.tsx` with theme selector and
  preferences display
EOF
)"

echo ""
echo "  Creating PR #2: Refactor: extract inference utilities..."
gh pr create \
  --repo "$REPO" \
  --head pr2-refactor-inference \
  --base main \
  --title "Refactor: extract inference utilities" \
  --body "$(cat <<'EOF'
## Summary

Extract scoring computation and ETA calculation logic from
`src/ml/inference.py` into dedicated helpers in `src/ml/features.py`.

This keeps the inference module focused on the public batch/per-item API
while the feature-engineering and scoring math lives in a single,
independently testable module.

### Changes
- **`src/ml/features.py`**: added `compute_route_score()`,
  `compute_eta_minutes()`, and `_sum_segment_distances()` helpers
- **`src/ml/inference.py`**: simplified to delegate to `features` module
EOF
)"

echo ""
echo "  Creating PR #3: Performance: batch route scoring..."
gh pr create \
  --repo "$REPO" \
  --head pr3-batch-scoring \
  --base main \
  --title "Performance: batch route scoring" \
  --body "$(cat <<'EOF'
## Summary

Improve memory efficiency of `score_routes_batch()` by processing
candidates in configurable chunks rather than all at once.

### Changes
- **`src/ml/inference.py`**: added `_score_chunk()` helper, refactored
  `score_routes_batch()` to iterate in fixed-size windows
- Added `batch_size` parameter (default 10) to control chunk granularity
EOF
)"

echo ""
echo "  Creating PR #4: Add vehicle status badge..."
gh pr create \
  --repo "$REPO" \
  --head pr4-status-badge \
  --base merge-target \
  --title "Add vehicle status badge" \
  --body "$(cat <<'EOF'
## Summary

Introduce a reusable `StatusBadge` component that renders color-coded
status indicators for vehicles. Replace inline status text in the
dashboard and detail views.

### Changes
- **`web/src/components/StatusBadge.tsx`**: new component with
  color-coded pill badges for active/idle/maintenance/offline states
- **`FleetDashboard.tsx`** and **`VehicleDetail.tsx`**: updated to use
  `StatusBadge`
- **`StatusBadge.test.tsx`**: unit tests for all status variants
EOF
)"

echo ""
echo "══════════════════════════════════════════════"
echo "  Reset complete!"
echo ""
echo "  PRs created:"
gh pr list --repo "$REPO" --state open --json number,title,headRefName --template '{{range .}}  #{{.number}} {{.title}} ({{.headRefName}}){{"\n"}}{{end}}'
echo "══════════════════════════════════════════════"
