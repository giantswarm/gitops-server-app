## Preliminary notes

The upstream for this repository is the https://github.com/giantswarm/weave-gitops-upstream, which is the fork of the https://github.com/weaveworks/weave-gitops repository.

This document is the shortened version of the Intranet page about using the [Git Subtree for tracking changes](https://intranet.giantswarm.io/docs/product/managed-apps/dev-experience/git-subtree).

## Syncing the `weave-gitops-upstream` with the upstream

First, [fork of the Weave Gitops repository](https://github.com/giantswarm/weave-gitops-upstream) must be synchronnized with the [upstream](https://github.com/weaveworks/weave-gitops). Below is the script snippet for doing this.

```shell
# Clone the repository if you haven't done it already.
git clone https://github.com/giantswarm/weave-gitops-upstream
cd weave-gitops-upstream

# Fetch the changes from the upstream repository, being the `weaveworks/weave-gitops`,
# and merge it into the `upstream-main` branch that tracks changes from the upstream.
git checkout upstream-main
git fetch --tags upstream
git merge upstream/main

# Find the latest non-rc tag in the upstream.
export upstream_latest_tag=$(git tag --sort=-refname | sort -V | grep -E "v[0-9]+\.[0-9]+\.[0-9]+$" | tail -n 1)

# Push the changes and the latest tag.
git push origin upstream-main
git push origin ${upstream_latest_tag}

git checkout main

git merge upstream-main
git push origin main
git push origin ${upstream_latest_tag}
```

After applying the above steps, all the latest changes should be pulled.

## Syncing this repository with the changes from the `weave-gitops-upstream`

Once the `weave-gitops-upstream` has the latest changes, this repository can be updated with them. Below is the script snippet
for doing this.

```shell
# Clone the repository if you haven't done it already.
git clone https://github.com/giantswarm/gitops-server-app
cd gitops-server-app

# For freshly cloned repository, or if you haven't configured upstream remote yet,
# add remote pointing to the `weave-gitops-upstream` and fetch changes from it.
git remote add -f --no-tags upstream-copy https://github.com/giantswarm/weave-gitops-upstream.git
git fetch upstream-copy refs/tags/${upstream_latest_tag}:refs/tags/upstream-${upstream_latest_tag}
git checkout upstream-${upstream_latest_tag}

# The `weave-gitops-upstream` keeps Helm Chart in the sub-dir, so we need to split it and its
# commits to the separate branch before we can use it for upgrading.
git subtree split -P charts/gitops-server -b temp-split-branch

# Prepare the upgrade branch.
git checkout main
git checkout -b upgrade-to-${upstream_latest_tag}

# Merge the previously splitted out branch with the Helm Chart.
git subtree merge --squash -P helm/gitops-server temp-split-branch
git notes add -m "upstreamSync: https://github.com/weaveworks/weave-gitops/tree/${upstream_latest_tag}"

# Generate `values.schema.json`. Bear in mind, the `schema-gen` plugin is deprecated,
# so use it with care. Also, when using this plugin you may notice sometimes the information
# is incomplete, which is not wrong, but may influence schema validation later on. An example
# of this is the `.ingress.hosts: []`. When empty by default, the schema will only tell us its an array:
# "hosts": {
#    "type": "array"
# }
# Which is incomplete in a sense that Helm Chart actually expects certain fields to be present when array
# is field in. To mitigate this, fill in the array with some synthetic values, and then generate the schema.
helm schema-gen helm/gitops-server/values.yaml > helm/gitops-server/values.schema.json

# Push the changes to the upgrade branch.
git push origin upgrade-to-${upstream_latest_tag}

# Delete the temporary branches and tags.
git tag -d upstream-${upstream_latest_tag}
git branch -D temp-split-branch
```
