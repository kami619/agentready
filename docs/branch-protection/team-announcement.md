# Branch Protection Enabled on `main` Branch

**Date:** [To be filled in after implementation]
**Effective:** Immediately
**Impact:** All contributors

## Summary

Branch protection rules have been enabled on the `main` branch to enforce code quality, security, and the documented PR workflow in CONTRIBUTING.md.

## What Changed

### Before
- Anyone with write access could push directly to `main`
- Force pushes and branch deletion were possible
- CI checks could be bypassed
- Code could reach production without peer review

### After
All merges to `main` now require:

1. ✅ **Pull request workflow** - No direct pushes allowed
2. ✅ **Peer review** - At least 1 approval required
3. ✅ **Passing CI checks** - Both Python 3.12 and 3.13 test suites must pass
4. ✅ **Up-to-date branches** - Must sync with latest `main` before merging
5. ✅ **Protected history** - No force pushes or branch deletion

## What This Means for You

### For All Contributors

**Your workflow changes:**

```bash
# ❌ This will no longer work:
git checkout main
git commit -m "fix: quick fix"
git push origin main  # REJECTED

# ✅ Use this workflow instead:
git checkout -b fix/issue-description
git commit -m "fix: descriptive commit message"
git push origin fix/issue-description
# Then create a PR via GitHub UI
```

**Pull request requirements:**
- Create a PR from your feature branch
- Wait for CI checks to pass (typically 5-10 minutes)
- Request review from a maintainer
- Address any review feedback
- Wait for approval
- Merge using the GitHub UI (after approval + passing CI)

### For Maintainers

**Review responsibilities:**
- Review code quality, tests, and documentation
- Verify CI checks passed before approving
- Use "Request changes" for issues that must be fixed
- Use "Approve" only when ready to merge

**Merge options:**
- "Merge pull request" - preserves all commits (default)
- "Squash and merge" - combines commits into one (for small PRs)
- "Rebase and merge" - maintains linear history

## Why This Change?

### Code Quality
- Enforces peer review, catching bugs and improving design
- Ensures all code passes automated tests before merging
- Maintains consistent coding standards via linting checks

### Security
- Prevents accidental or malicious force pushes
- Protects against branch deletion
- Creates audit trail of all changes (via PRs)

### Alignment
- Matches our documented workflow in CONTRIBUTING.md (lines 95-123)
- Follows industry best practices for collaborative development
- Supports our mission as an AI-readiness assessment tool (we should model best practices)

## Required Status Checks

The following CI workflows must pass before merging:

| Check | Description | Typical Duration |
|-------|-------------|------------------|
| `blocking-checks (3.12)` | Critical tests + quality checks on Python 3.12 | ~3-5 minutes |
| `blocking-checks (3.13)` | Critical tests + quality checks on Python 3.13 | ~3-5 minutes |

**What's checked:**
- Unit tests (critical paths)
- Code formatting (black, isort)
- Linting (ruff)

## Emergency Procedures

### If CI is Broken
If the CI system itself is broken (not your code):
1. Report the CI issue in Slack/GitHub Discussions
2. Wait for a maintainer to investigate
3. A maintainer may temporarily disable checks if necessary

### If Review is Blocked
If you need urgent review:
1. Tag specific reviewers in the PR
2. Post in the team chat with context
3. For critical hotfixes, request expedited review

### Administrator Override
Repository administrators can bypass these protections in true emergencies. This should be extremely rare and requires:
- Clear justification documented in an issue
- Post-facto review of the change
- Communication to the team

## FAQ

**Q: Can I still create branches and commits locally?**
A: Yes! You can commit to any branch locally. The protection only affects pushing to the remote `main` branch.

**Q: What if I accidentally committed to my local `main`?**
A: Create a feature branch from your current state:
```bash
git checkout -b fix/my-changes
git push origin fix/my-changes
# Then reset your local main to match remote
git checkout main
git reset --hard origin/main
```

**Q: How long will reviews take?**
A: We aim for reviews within 24 hours during weekdays. Urgent fixes can be expedited.

**Q: Can I approve my own PR?**
A: No, you need at least one approval from another team member.

**Q: What if CI is taking too long?**
A: CI should complete within 10 minutes. If it's stuck, check the Actions tab for errors or cancel and re-run.

**Q: What about Dependabot PRs?**
A: Dependabot PRs follow the same rules. We have `dependabot-auto-merge.yml` workflow that can auto-merge after checks pass.

**Q: Why do we need both Python 3.12 and 3.13 checks?**
A: We support both versions. Changes must be compatible with both to avoid breaking users on either version.

## Getting Help

If you have questions or run into issues:

- **Documentation:** See CONTRIBUTING.md for detailed workflow
- **Technical issues:** Open a GitHub Discussion
- **Urgent blockers:** Contact repository maintainers directly

## References

- Implementation details: See `implementation-guide.md`
- Verification testing: See `verification-checklist.md`
- Original issue: #281
- Contributing guide: CONTRIBUTING.md

## Feedback Welcome

This is a quality improvement for the project. If you have feedback on the process or suggestions for improvement, please:

- Open a GitHub Discussion
- Comment on issue #281
- Reach out to maintainers

Thank you for your cooperation in maintaining high code quality! 🎉

---

**Implemented by:** [Name]
**Verified by:** [Name]
**Date implemented:** [Date]
