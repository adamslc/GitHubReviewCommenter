# GitHubReviewCommenter

This is a simple python script to automate the creation of `suggestion`
comments in a GitHub review of a PR.

To use it, you will need to have `gh` and the python packages `unidiff` and
`subprocess` installed. Then go to a branch associated with a GitHub pull
request, make some changes, and stage those changes. Running `make_comments.py`
will attempt to create review comments suggesting the changes you have
proposed.

This will fail if you make a change to a line that is not included in the pull
request's diff. In the future, I want to check that each suggestion is
accessible before sending the comment. It would also be nice to enable users to
add additional comments to each suggestion before sending it, and also add an
overall review comment.

Ideally, all of this functionality will be added into `gh` in the future.
See https://github.com/cli/cli/discussions/5904.

Testing testing testing...
