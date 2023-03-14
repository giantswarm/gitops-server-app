## Preliminary notes

The upstream for this repository is the https://github.com/giantswarm/weave-gitops-upstream, which is the fork of the https://github.com/weaveworks/weave-gitops repository.

This document is the shortened version of the Intranet page about using the [Git Subtree for tracking changes](https://intranet.giantswarm.io/docs/product/managed-apps/dev-experience/git-subtree).

## Syncing the `weave-gitops-upstream` with the upstream

First, [fork of the Weave Gitops repository](https://github.com/giantswarm/weave-gitops-upstream) must be synchronnized with the [upstream](https://github.com/weaveworks/weave-gitops). Below is the script snippet for doing this.

```shell
git clone https://github.com/giantswarm/weave-gitops-upstream
cd weave-gitops-upstream

git checkout upstream-main
git fetch --tags upstream
git merge upstream/main

export upstream_latest_tag=$(git tag --sort=-refname | sort -V | grep -E "v[0-9]+\.[0-9]+\.[0-9]+$" | tail -n 1)

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
git remote add -f --no-tags upstream-copy https://github.com/giantswarm/weave-gitops-upstream.git

git fetch upstream-copy refs/tags/${upstream_latest_tag}:refs/tags/upstream-${upstream_latest_tag}

git checkout upstream-${upstream_latest_tag}
```
