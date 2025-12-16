#!/bin/bash
# Test script for agentready-dev workflow comment posting
#
# This script simulates the GitHub Actions workflow step that posts comments
# to issues/PRs after Claude Code Action completes.
#
# Usage:
#   ./scripts/test-agentready-dev-workflow.sh <issue-number>
#   Or with explicit token:
#   GITHUB_TOKEN=<token> ./scripts/test-agentready-dev-workflow.sh <issue-number>

set -euo pipefail

ISSUE_NUMBER="${1:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$ISSUE_NUMBER" ]; then
  echo "Usage: $0 <issue-number>"
  echo "   Or: GITHUB_TOKEN=<token> $0 <issue-number>"
  exit 1
fi

OWNER="ambient-code"
REPO="agentready"

echo "Testing comment posting for issue/PR #${ISSUE_NUMBER}..."
echo ""

# Check if gh CLI is available
if command -v gh &> /dev/null; then
  echo "✅ Using GitHub CLI (gh)"
  USE_GH=true
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "✅ Using GitHub API with token"
  USE_GH=false
else
  echo "❌ Error: Either 'gh' CLI must be installed or GITHUB_TOKEN must be set"
  exit 1
fi

# Test 1: Get issue/PR info
echo "1. Fetching issue/PR information..."
if [ "$USE_GH" = true ]; then
  ISSUE_INFO=$(gh api "repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}" 2>&1)
  if [ $? -ne 0 ]; then
    echo "   ❌ Error fetching issue: $ISSUE_INFO"
    exit 1
  fi
  TITLE=$(echo "$ISSUE_INFO" | jq -r '.title')
  IS_PR=$(echo "$ISSUE_INFO" | jq -r '.pull_request != null')
  echo "   ✅ Found: $TITLE"
  echo "   Type: $([ "$IS_PR" = "true" ] && echo "Pull Request" || echo "Issue")"
else
  ISSUE_INFO=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
    "https://api.github.com/repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}")
  TITLE=$(echo "$ISSUE_INFO" | jq -r '.title')
  IS_PR=$(echo "$ISSUE_INFO" | jq -r '.pull_request != null')
  echo "   ✅ Found: $TITLE"
  echo "   Type: $([ "$IS_PR" = "true" ] && echo "Pull Request" || echo "Issue")"
fi

# Test 2: List existing comments
echo ""
echo "2. Fetching existing comments..."
if [ "$USE_GH" = true ]; then
  COMMENTS=$(gh api "repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}/comments" 2>&1)
  COMMENT_COUNT=$(echo "$COMMENTS" | jq '. | length')
else
  COMMENTS=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
    "https://api.github.com/repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}/comments")
  COMMENT_COUNT=$(echo "$COMMENTS" | jq '. | length')
fi

echo "   ✅ Found $COMMENT_COUNT total comments"

# Show recent comments
RECENT_COUNT=$(echo "$COMMENTS" | jq '[.[] | select((.created_at | fromdateiso8601) > (now - 600))] | length')
echo "   Recent comments (last 10 min): $RECENT_COUNT"

# Test 3: Check for github-actions[bot] comments
echo ""
echo "3. Checking for github-actions[bot] comments..."
BOT_COMMENTS=$(echo "$COMMENTS" | jq '[.[] | select(.user.login == "github-actions[bot]")]')
BOT_COUNT=$(echo "$BOT_COMMENTS" | jq '. | length')
echo "   Found $BOT_COUNT comments from github-actions[bot]"

RECENT_BOT=$(echo "$BOT_COMMENTS" | jq '[.[] | select((.created_at | fromdateiso8601) > (now - 120))]')
RECENT_BOT_COUNT=$(echo "$RECENT_BOT" | jq '. | length')
echo "   Recent bot comments (last 2 min): $RECENT_BOT_COUNT"

if [ "$RECENT_BOT_COUNT" -gt 0 ]; then
  LATEST_BODY=$(echo "$RECENT_BOT" | jq -r '.[0].body' | head -c 100)
  HAS_AGENTREADY=$(echo "$RECENT_BOT" | jq -r '.[0].body' | grep -q '@agentready-dev' && echo "true" || echo "false")
  echo "   Latest: ${LATEST_BODY}..."
  echo "   Has @agentready-dev: $HAS_AGENTREADY"
fi

# Test 4: Post a test comment
echo ""
echo "4. Posting test comment..."
TEST_BODY=$(cat <<EOF
🤖 **@agentready-dev Agent** (Test)

✅ Test comment posted successfully.

This is a test comment to verify the workflow can post to issue/PR #${ISSUE_NUMBER}.

---
*This is a test comment from the workflow test script.*
EOF
)

if [ "$USE_GH" = true ]; then
  COMMENT_RESULT=$(gh api "repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}/comments" \
    -X POST \
    -f body="$TEST_BODY" 2>&1)
  if [ $? -ne 0 ]; then
    echo "   ❌ Error posting comment: $COMMENT_RESULT"
    exit 1
  fi
  COMMENT_URL=$(echo "$COMMENT_RESULT" | jq -r '.html_url')
  echo "   ✅ Successfully posted comment!"
  echo "   Comment URL: $COMMENT_URL"
else
  COMMENT_RESULT=$(curl -s -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}/comments" \
    -d "{\"body\": $(echo "$TEST_BODY" | jq -Rs .)}")

  COMMENT_URL=$(echo "$COMMENT_RESULT" | jq -r '.html_url // empty')
  if [ -z "$COMMENT_URL" ] || [ "$COMMENT_URL" = "null" ]; then
    echo "   ❌ Error posting comment"
    echo "   Response: $COMMENT_RESULT"
    exit 1
  fi
  echo "   ✅ Successfully posted comment!"
  echo "   Comment URL: $COMMENT_URL"
fi

# Test 5: Verify comment was posted
echo ""
echo "5. Verifying comment was posted..."
sleep 2

if [ "$USE_GH" = true ]; then
  UPDATED_COMMENTS=$(gh api "repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}/comments" 2>&1)
else
  UPDATED_COMMENTS=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
    "https://api.github.com/repos/${OWNER}/${REPO}/issues/${ISSUE_NUMBER}/comments")
fi

TEST_COMMENT=$(echo "$UPDATED_COMMENTS" | jq '[.[] | select(.body | contains("Test comment posted successfully"))] | .[0]')

if [ "$TEST_COMMENT" != "null" ] && [ -n "$TEST_COMMENT" ]; then
  COMMENT_ID=$(echo "$TEST_COMMENT" | jq -r '.id')
  COMMENT_URL=$(echo "$TEST_COMMENT" | jq -r '.html_url')
  echo "   ✅ Test comment found!"
  echo "   Comment ID: $COMMENT_ID"
  echo "   Comment URL: $COMMENT_URL"
else
  echo "   ⚠️  Test comment not found (may need to wait longer)"
fi

echo ""
echo "✅ All tests completed successfully!"
