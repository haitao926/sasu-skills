# cc-switch and Gitea

## Current conclusion

Based on the local `cc-switch` database schema and installed repo metadata:

- skill repositories are stored as `owner`, `name`, and `branch`
- installed skill records use GitHub-style `readme_url` values
- the public docs use the format:

```text
https://github.com/{owner}/{name}/tree/{branch}/{subdirectory}
```

That strongly suggests `cc-switch` currently assumes a GitHub-hosted repository model for remote skill discovery.

## Practical implication

A self-hosted Gitea repository may be fine as a Git remote, but not necessarily as a first-class `cc-switch` remote skill source unless `cc-switch` adds:

- a configurable host field, or
- generic git clone support, or
- Gitea-aware URL generation

## Recommended workaround

Use dual remotes:

1. `Gitea` as the source-of-truth repo you own and edit
2. `GitHub` as the mirror repo that `cc-switch` indexes

Keep the repository structure identical on both:

```text
skills/<skill-slug>/...
```

Then configure `cc-switch` with:

- Owner: your GitHub owner
- Name: mirrored repository name
- Branch: `main`
- Subdirectory: `skills`

## Future compatibility path

If `cc-switch` later adds a host field, the same repository can work unchanged because the only host-specific assumption is the remote URL pattern, not the on-disk layout.
