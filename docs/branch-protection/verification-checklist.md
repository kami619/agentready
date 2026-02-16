# Branch Protection Verification Checklist

Use this checklist to verify that branch protection rules are correctly configured and functioning as expected on the `main` branch.

## Pre-Implementation Verification

Before applying the protection rules, document the current state:

- [ ] **Confirm current protection status**
  - Navigate to Settings → Branches
  - Screenshot the current state (no rules should exist)
  - Document any existing rules for comparison

## Post-Implementation Verification

After applying the protection rules via the implementation guide:

### Visual Verification in GitHub UI

- [ ] **Verify rule appears in branch list**
  - Navigate to Settings → Branches
  - Confirm a protection rule for `main` is listed
  - Click **Edit** to review the configuration

- [ ] **Verify required settings are enabled**
  - [ ] "Require a pull request before merging" is checked
  - [ ] "Require approvals" is set to `1`
  - [ ] "Dismiss stale pull request approvals when new commits are pushed" is checked
  - [ ] "Require status checks to pass before merging" is checked
  - [ ] "Require branches to be up to date before merging" is checked
  - [ ] Required status checks include: `blocking-checks (3.12)` and `blocking-checks (3.13)`
  - [ ] "Do not allow force pushes" is checked
  - [ ] "Do not allow deletions" is checked

- [ ] **Verify branch indicator in repository**
  - Go to the main repository page
  - Look for a shield/lock icon next to the `main` branch dropdown
  - Tooltip should indicate "Branch is protected"

### Functional Testing

#### Test 1: Attempt Direct Push (Should Fail)

- [ ] **Clone the repository** (or use existing local clone)
  ```bash
  git clone https://github.com/ambient-code/agentready.git
  cd agentready
  git checkout main
  ```

- [ ] **Make a trivial change**
  ```bash
  echo "# Test" >> TEST_FILE.md
  git add TEST_FILE.md
  git commit -m "test: verify branch protection"
  ```

- [ ] **Attempt to push directly to main**
  ```bash
  git push origin main
  ```

- [ ] **Expected Result:** Push should be **rejected** with an error message like:
  ```
  remote: error: GH006: Protected branch update failed for refs/heads/main.
  remote: error: Changes must be made through a pull request.
  ```

- [ ] **Clean up test**
  ```bash
  git reset HEAD~1
  rm TEST_FILE.md
  ```

#### Test 2: Create PR Without Approval (Should Block Merge)

- [ ] **Create a feature branch**
  ```bash
  git checkout -b test/branch-protection-verification
  echo "# Test" >> TEST_FILE.md
  git add TEST_FILE.md
  git commit -m "test: verify PR approval requirement"
  git push origin test/branch-protection-verification
  ```

- [ ] **Create a pull request**
  - Navigate to https://github.com/ambient-code/agentready/pulls
  - Click "New pull request"
  - Select `test/branch-protection-verification` as the compare branch
  - Create the PR

- [ ] **Verify merge is blocked without approval**
  - Look for a message in the PR indicating checks are required
  - The "Merge" button should be disabled or show "Merging is blocked"
  - Status should show "Review required" and "Required status checks must pass"

#### Test 3: Create PR With Approval But Failing CI (Should Block Merge)

Use the same PR from Test 2, but intentionally break CI:

- [ ] **Add a failing test or linting error**
  ```bash
  echo "intentionally_bad_code = ( incomplete syntax" >> src/agentready/cli/main.py
  git add src/agentready/cli/main.py
  git commit -m "test: verify CI requirement (will fail)"
  git push origin test/branch-protection-verification
  ```

- [ ] **Request approval** from a maintainer
  - Get the PR approved by someone with write access

- [ ] **Verify merge is still blocked**
  - Even with approval, the "Merge" button should be disabled
  - Status should show "Required status checks must pass"
  - CI workflow should be failing (red X)

- [ ] **Clean up the failing code**
  ```bash
  git checkout src/agentready/cli/main.py
  git commit -m "test: fix intentional failure"
  git push origin test/branch-protection-verification
  ```

#### Test 4: Create PR With Approval And Passing CI (Should Allow Merge)

- [ ] **Verify CI passes**
  - Wait for the CI workflow to complete
  - All required status checks should show green checkmarks

- [ ] **Verify approval is still valid**
  - The previous approval should remain valid (unless "Require approval of the most recent reviewable push" is enabled)

- [ ] **Verify merge is allowed**
  - The "Merge" button should now be enabled (green)
  - Status should show "All checks have passed"

- [ ] **Merge the PR**
  - Click "Merge pull request"
  - Confirm the merge
  - Delete the test branch after merging

- [ ] **Verify the test file is in main**
  ```bash
  git checkout main
  git pull origin main
  ls TEST_FILE.md  # Should exist
  ```

- [ ] **Clean up test file**
  ```bash
  git checkout -b chore/remove-test-file
  git rm TEST_FILE.md
  git commit -m "chore: remove branch protection test file"
  git push origin chore/remove-test-file
  # Create and merge a PR to remove the test file
  ```

#### Test 5: Attempt Force Push (Should Fail)

- [ ] **Attempt to force push to main**
  ```bash
  git checkout main
  git reset --hard HEAD~1  # Go back one commit (dangerous!)
  git push --force origin main
  ```

- [ ] **Expected Result:** Force push should be **rejected** with an error like:
  ```
  remote: error: GH006: Protected branch update failed for refs/heads/main.
  remote: error: Cannot force-push to this branch
  ```

- [ ] **Clean up**
  ```bash
  git reset --hard origin/main  # Restore to remote state
  ```

#### Test 6: Attempt Branch Deletion (Should Fail)

- [ ] **Attempt to delete the main branch**
  ```bash
  git push origin --delete main
  ```

- [ ] **Expected Result:** Deletion should be **rejected** with an error like:
  ```
  remote: error: GH006: Protected branch update failed for refs/heads/main.
  remote: error: Cannot delete this branch
  ```

## Verification Summary

After completing all tests, confirm:

- [ ] Direct pushes to `main` are blocked ✅
- [ ] PRs require at least 1 approval ✅
- [ ] PRs require passing CI checks ✅
- [ ] Both approval AND passing CI are required to merge ✅
- [ ] Force pushes are blocked ✅
- [ ] Branch deletion is blocked ✅

## Documentation

- [ ] **Take screenshots** of:
  - Branch protection settings page showing all enabled rules
  - A successful PR merge showing required checks passed
  - A blocked merge attempt showing the protection working

- [ ] **Update issue #281** with:
  - Confirmation that protection rules are applied
  - Screenshots demonstrating the configuration
  - Date/time of implementation
  - Name of person who applied the settings

## Optional: Advanced Verification

If you enabled optional settings:

### Signed Commits (if enabled)
- [ ] Attempt to push an unsigned commit
- [ ] Verify it's rejected
- [ ] Push a signed commit
- [ ] Verify it's accepted

### Linear History (if enabled)
- [ ] Attempt to merge with a merge commit
- [ ] Verify it's rejected
- [ ] Use "Rebase and merge" or "Squash and merge"
- [ ] Verify it's accepted

## Rollback Testing (Optional)

Only perform if you need to verify the rollback procedure:

- [ ] **Temporarily remove protection rules**
  - Go to Settings → Branches
  - Click "Delete" on the main branch protection rule
  - Confirm deletion

- [ ] **Verify direct push now works**
  - Attempt a direct push to main
  - It should succeed

- [ ] **Re-apply protection rules**
  - Follow the implementation guide again
  - Verify all settings are restored

## Sign-Off

Once all verification steps pass:

**Verified by:** ______________________
**Date:** ______________________
**Status:** ☐ Pass ☐ Fail ☐ Partial (see notes)

**Notes:**
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

**Next Steps:**
- [ ] Announce to team (see `team-announcement.md`)
- [ ] Update CONTRIBUTING.md to reference enforced protections
- [ ] Close issue #281
