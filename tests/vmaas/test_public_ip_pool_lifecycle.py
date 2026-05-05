from __future__ import annotations

from uuid import uuid4

from tests.grpc_client import GRPCClient
from tests.helpers import wait_for_public_ip_pool_cr, wait_for_public_ip_pool_deletion, wait_for_public_ip_pool_ready
from tests.k8s_client import K8sClient
from tests.runner import poll_until


def test_public_ip_pool_lifecycle(grpc: GRPCClient, k8s_hub_client: K8sClient) -> None:
    pool_name: str = f"test-pool-{uuid4().hex[:8]}"
    pool_id: str = grpc.create_public_ip_pool(name=pool_name, cidrs=["198.51.100.0/28"])
    cr_name: str = wait_for_public_ip_pool_cr(k8s=k8s_hub_client, uuid=pool_id)

    assert pool_id in grpc.list_public_ip_pool_ids()
    wait_for_public_ip_pool_ready(k8s=k8s_hub_client, name=cr_name)

    grpc.delete_public_ip_pool(pool_id=pool_id)
    wait_for_public_ip_pool_deletion(k8s=k8s_hub_client, name=cr_name)
    poll_until(
        fn=lambda: pool_id not in grpc.list_public_ip_pool_ids(),
        until=lambda v: v is True,
        retries=30,
        delay=5,
        description=f"PublicIPPool {pool_id} removal from API",
    )
