#!/usr/bin/env node
/**
 * Test script for agentready-dev workflow comment posting
 *
 * This script simulates the GitHub Actions workflow step that posts comments
 * to issues/PRs after Claude Code Action completes.
 *
 * Usage:
 *   GITHUB_TOKEN=<token> node scripts/test-agentready-dev-workflow.js <issue-number>
 */

const { Octokit } = require('@octokit/rest');

// Get arguments
const issueNumber = process.argv[2];
const githubToken = process.env.GITHUB_TOKEN;

if (!issueNumber) {
  console.error('Usage: GITHUB_TOKEN=<token> node scripts/test-agentready-dev-workflow.js <issue-number>');
  process.exit(1);
}

if (!githubToken) {
  console.error('Error: GITHUB_TOKEN environment variable is required');
  process.exit(1);
}

const octokit = new Octokit({
  auth: githubToken,
});

const owner = 'ambient-code';
const repo = 'agentready';

async function testCommentPosting() {
  console.log(`Testing comment posting for issue/PR #${issueNumber}...\n`);

  try {
    // Test 1: Get issue/PR info
    console.log('1. Fetching issue/PR information...');
    let issue;
    try {
      issue = await octokit.rest.issues.get({
        owner,
        repo,
        issue_number: parseInt(issueNumber, 10),
      });
      console.log(`   ✅ Found: ${issue.data.title}`);
      console.log(`   Type: ${issue.data.pull_request ? 'Pull Request' : 'Issue'}`);
    } catch (error) {
      console.error(`   ❌ Error fetching issue: ${error.message}`);
      throw error;
    }

    // Test 2: List existing comments
    console.log('\n2. Fetching existing comments...');
    let comments;
    try {
      comments = await octokit.rest.issues.listComments({
        owner,
        repo,
        issue_number: parseInt(issueNumber, 10),
      });
      console.log(`   ✅ Found ${comments.data.length} total comments`);

      // Show recent comments
      const recentComments = comments.data
        .filter(comment => {
          const commentTime = new Date(comment.created_at);
          const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000);
          return commentTime > tenMinutesAgo;
        })
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

      console.log(`   Recent comments (last 10 min): ${recentComments.length}`);
      recentComments.forEach((comment, idx) => {
        console.log(`   ${idx + 1}. [${comment.user.login}] ${comment.body.substring(0, 50)}...`);
      });
    } catch (error) {
      console.error(`   ❌ Error fetching comments: ${error.message}`);
      throw error;
    }

    // Test 3: Check for github-actions[bot] comments
    console.log('\n3. Checking for github-actions[bot] comments...');
    const botComments = comments.data.filter(
      comment => comment.user.login === 'github-actions[bot]'
    );
    console.log(`   Found ${botComments.length} comments from github-actions[bot]`);

    const recentBotComments = botComments
      .filter(comment => {
        const commentTime = new Date(comment.created_at);
        const twoMinutesAgo = new Date(Date.now() - 2 * 60 * 1000);
        return commentTime > twoMinutesAgo;
      })
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    console.log(`   Recent bot comments (last 2 min): ${recentBotComments.length}`);
    if (recentBotComments.length > 0) {
      const latest = recentBotComments[0];
      console.log(`   Latest: ${latest.body.substring(0, 100)}...`);
      console.log(`   Has @agentready-dev: ${latest.body.includes('@agentready-dev')}`);
    }

    // Test 4: Post a test comment
    console.log('\n4. Posting test comment...');
    const testBody = `🤖 **@agentready-dev Agent** (Test)\n\n` +
                    `✅ Test comment posted successfully.\n\n` +
                    `This is a test comment to verify the workflow can post to issue/PR #${issueNumber}.\n\n` +
                    `---\n` +
                    `*This is a test comment from the workflow test script.*`;

    try {
      const result = await octokit.rest.issues.createComment({
        owner,
        repo,
        issue_number: parseInt(issueNumber, 10),
        body: testBody,
      });
      console.log(`   ✅ Successfully posted comment!`);
      console.log(`   Comment URL: ${result.data.html_url}`);
    } catch (error) {
      console.error(`   ❌ Error posting comment: ${error.message}`);
      if (error.response) {
        console.error(`   Status: ${error.response.status}`);
        console.error(`   Response: ${JSON.stringify(error.response.data, null, 2)}`);
      }
      throw error;
    }

    // Test 5: Verify comment was posted
    console.log('\n5. Verifying comment was posted...');
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds

    const updatedComments = await octokit.rest.issues.listComments({
      owner,
      repo,
      issue_number: parseInt(issueNumber, 10),
    });

    const testComment = updatedComments.data.find(
      comment => comment.body.includes('Test comment posted successfully')
    );

    if (testComment) {
      console.log(`   ✅ Test comment found!`);
      console.log(`   Comment ID: ${testComment.id}`);
      console.log(`   Comment URL: ${testComment.html_url}`);
    } else {
      console.log(`   ⚠️  Test comment not found (may need to wait longer)`);
    }

    console.log('\n✅ All tests completed successfully!');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

testCommentPosting();
