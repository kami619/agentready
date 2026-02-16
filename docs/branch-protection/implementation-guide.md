# Branch Protection Implementation Guide

This guide provides step-by-step instructions for configuring branch protection rules on the `main` branch of the `ambient-code/agentready` repository.

## Prerequisites

- **Repository Administrator** access to `ambient-code/agentready`
- GitHub web browser access

## Implementation Steps

### Step 1: Navigate to Branch Protection Settings

1. Go to https://github.com/ambient-code/agentready
2. Click **Settings** (top navigation bar)
3. In the left sidebar, click **Branches** (under "Code and automation")
4. Click **Add branch protection rule** (or **Add rule** button)

### Step 2: Configure Branch Name Pattern

In the **Branch name pattern** field, enter:
```
main
```

This ensures the rule applies to the default branch.

### Step 3: Configure Pull Request Requirements

Under **Protect matching branches**, enable and configure:

#### ✅ Require a pull request before merging
- **Check this box**
- Then configure the sub-options:
  - ✅ **Require approvals**: Set to `1`
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**
  - ⬜ **Require review from Code Owners** (optional - only if you have a CODEOWNERS file)
  - ⬜ **Restrict who can dismiss pull request reviews** (optional)
  - ⬜ **Allow specified actors to bypass required pull requests** (leave unchecked)
  - ⬜ **Require approval of the most recent reviewable push** (optional but recommended)

### Step 4: Configure Required Status Checks

#### ✅ Require status checks to pass before merging
- **Check this box**
- Then configure:
  - ✅ **Require branches to be up to date before merging** (recommended)

#### Search and Add Required Status Checks

In the search box that appears, search for and add these status checks:

**Required Checks:**
1. **`blocking-checks (3.12)`** - Critical tests and quality checks on Python 3.12
2. **`blocking-checks (3.13)`** - Critical tests and quality checks on Python 3.13

**How to find them:**
- Type "blocking" in the search field
- Select both matrix job variations from the dropdown

**Note:** The `podman-rootless-test` check only runs when container-related files change (path-specific workflow), so it's **not required** as a universal status check.

**Optional Checks to Consider:**
- `coverage-report` - Ensures coverage data is collected (non-blocking, informational)

### Step 5: Configure Force Push and Deletion Protection

#### ✅ Do not allow bypassing the above settings
- Check this box to ensure all users (including admins) must follow the rules
- **OR** leave unchecked if you want administrators to be able to bypass in emergencies

#### ✅ Do not allow force pushes
- **Check this box** (critical for preventing history rewriting)
- This prevents `git push --force` on the main branch

#### ✅ Do not allow deletions
- **Check this box** (critical for preventing branch deletion)

### Step 6: Optional Advanced Settings

These are optional but recommended for enhanced security:

#### ⬜ Require signed commits (Optional)
- Enforces GPG/SSH commit signature verification
- **Trade-off:** Requires all contributors to set up commit signing
- **Recommendation:** Enable if your team already uses signed commits

#### ⬜ Require linear history (Optional)
- Prevents merge commits, enforces rebase workflow
- **Trade-off:** Contributors must rebase instead of merge
- **Recommendation:** Consider enabling if your team prefers linear history

#### ⬜ Require deployments to succeed before merging (Optional)
- Only relevant if you have deployment workflows
- **Recommendation:** Skip for now

#### ⬜ Lock branch (Optional)
- Makes the branch read-only
- **Recommendation:** Do not enable (would prevent all merges)

#### ⬜ Allow fork syncing (Optional)
- Allows forked repositories to sync with upstream
- **Recommendation:** Enable if you accept external contributions

### Step 7: Save Configuration

1. Scroll to the bottom of the page
2. Click **Create** (or **Save changes** if editing an existing rule)
3. Confirm the settings are applied

## Configuration Summary

After completing these steps, your branch protection rule should enforce:

| Setting | Status | Value |
|---------|--------|-------|
| Branch pattern | ✅ | `main` |
| Require PR | ✅ | Yes |
| Required approvals | ✅ | 1 |
| Dismiss stale approvals | ✅ | Yes |
| Required status checks | ✅ | `blocking-checks (3.12)`, `blocking-checks (3.13)` |
| Require up-to-date branches | ✅ | Yes |
| Allow force pushes | ❌ | No |
| Allow deletions | ❌ | No |

## Next Steps

1. **Verify the configuration** using the verification checklist (`verification-checklist.md`)
2. **Test with a sample PR** to ensure the rules work as expected
3. **Announce the change** to the team using the announcement template (`team-announcement.md`)
4. **Update CONTRIBUTING.md** to reference the enforced protections (optional)

## Troubleshooting

### Issue: Status checks don't appear in the search
**Solution:** The status checks only appear after they've run at least once. If you don't see them:
1. Create a test PR to trigger the CI workflow
2. Wait for the workflow to complete
3. Return to branch protection settings and search again

### Issue: Can't find the Settings tab
**Solution:** You need administrator access. Contact the repository owner to grant you admin permissions.

### Issue: Warning about existing PRs
**Solution:** Existing open PRs may not meet the new requirements. You can:
- Grandfather existing PRs (approve and merge them quickly)
- Or require them to meet the new standards

## Rollback Procedure

If you need to remove or modify the protection rules:

1. Go to **Settings → Branches**
2. Find the `main` branch rule
3. Click **Edit** to modify, or **Delete** to remove
4. Make your changes and click **Save changes**

**Warning:** Removing protection rules exposes the repository to the original risks. Only do this temporarily and with team awareness.

## Documentation References

- [GitHub: Managing a branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [GitHub: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub: About status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
