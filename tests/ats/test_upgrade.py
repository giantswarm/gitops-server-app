import logging

import pytest
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.k8s.deployment import wait_for_deployments_to_run

logger = logging.getLogger(__name__)


@pytest.mark.upgrade
def test_pods_available_after_upgraded(
    kube_cluster: Cluster
) -> None:
    deployments = wait_for_deployments_to_run(
        kube_cluster.kube_client,
        [
            "gitops-server",
        ],
        "default",
        300,
    )

    for d in deployments:
        assert int(d.obj["status"]["readyReplicas"]) > 0
        logger.info(f"Deployment '{d.name}' is ready")
