# CONTRIBUTING.md Update

This document describes changes to add to CONTRIBUTING.md to reflect the enforced branch protection rules.

## Proposed Addition

Add this section after the "Pull Request Process" section (after line 123):

---

### Branch Protection Rules

The `main` branch is protected with the following enforced rules:

#### Required Workflow
- **No direct pushes** - All changes must go through pull requests
- **Peer review required** - At least 1 approval from a maintainer
- **CI checks must pass** - All required status checks must complete successfully
- **Up-to-date branches** - Your branch must be current with `main` before merging

#### Protected Actions
- **Force pushes are blocked** - Cannot use `git push --force` on `main`
- **Branch deletion is blocked** - The `main` branch cannot be deleted
- **Stale approvals dismissed** - New commits require re-approval

#### Required Status Checks

The following CI workflows must pass before your PR can be merged:

- `blocking-checks (3.12)` - Tests and code quality on Python 3.12
- `blocking-checks (3.13)` - Tests and code quality on Python 3.13

These typically take 5-10 minutes to complete.

#### What This Means

If you attempt to push directly to `main`, you'll see:
```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: Changes must be made through a pull request.
```

**Always use feature branches:**
```bash
git checkout -b feature/your-feature-name
# Make your changes
git push origin feature/your-feature-name
# Create PR via GitHub UI
```

#### Emergency Procedures

In rare emergencies, repository administrators can override these protections. This requires:
- Clear justification documented in an issue
- Post-facto code review
- Team notification

For questions about branch protection, see [GitHub's branch protection documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

---

## Alternative: Update Existing Section

If you prefer to update the existing "Pull Request Process" section instead of adding a new one, modify lines 95-123 as follows:

### Replace Line 119-122

**Current text:**
```markdown
5. **Wait for approval**:
   - At least one maintainer approval required
   - All CI checks must pass
   - No merge conflicts
```

**New text:**
```markdown
5. **Wait for approval and CI checks**:
   - At least one maintainer approval required (enforced by branch protection)
   - All CI checks must pass (enforced: `blocking-checks` on Python 3.12 and 3.13)
   - Branch must be up-to-date with `main`
   - No merge conflicts

   **Note:** These requirements are enforced by branch protection rules. You will not be able to merge until all conditions are met. See the "Branch Protection Rules" section below for details.
```

Then add the "Branch Protection Rules" section as described above.

## Implementation Instructions

1. Open `CONTRIBUTING.md` in your editor
2. Choose one of the approaches above:
   - **Option A:** Add new section after line 123
   - **Option B:** Update existing section + add new section
3. Commit the changes:
   ```bash
   git checkout -b docs/document-branch-protection
   git add CONTRIBUTING.md
   git commit -m "docs(contributing): document branch protection rules

   - Add section explaining enforced branch protection on main
   - Clarify required status checks and workflow
   - Provide emergency procedures

   Fixes #281"
   git push origin docs/document-branch-protection
   ```
4. Create a PR with the changes
5. Link the PR to issue #281

## Benefits of This Update

1. **Transparency** - Contributors know the rules before they encounter them
2. **Self-service** - Reduces questions about blocked pushes or merge requirements
3. **Onboarding** - New contributors understand the workflow from the start
4. **Reference** - Team can point to this documentation when questions arise

## Related Files

This update complements:
- The implementation guide (`implementation-guide.md`)
- The team announcement (`team-announcement.md`)
- The verification checklist (`verification-checklist.md`)
