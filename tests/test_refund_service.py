from types import SimpleNamespace

import pytest

from app.services import refund_service


class FakeRefundRepository:
    def __init__(self, active_refund: bool = False) -> None:
        self.active_refund = active_refund
        self.calls: list[tuple] = []
        self.refund = SimpleNamespace(id=1001, order_id=2001, status="PENDING_REVIEW")

    async def has_active_refund_for_order(self, order_id: int) -> bool:
        self.calls.append(("has_active_refund_for_order", order_id))
        return self.active_refund

    async def create(self, order_id: int, user_id: int, reason: str, amount: float):
        self.calls.append(("create", order_id, user_id, reason, amount))
        self.refund.order_id = order_id
        return self.refund

    async def create_approval(self, refund):
        self.calls.append(("create_approval", refund.id))
        return SimpleNamespace(id=3001, target_id=refund.id)


def make_service(monkeypatch: pytest.MonkeyPatch, repo: FakeRefundRepository):
    monkeypatch.setattr(refund_service, "RefundRepository", lambda _session: repo)
    return refund_service.RefundService(session=object())


@pytest.mark.asyncio
async def test_create_refund_rejects_unpaid_order_before_repo_checks(monkeypatch):
    repo = FakeRefundRepository()
    service = make_service(monkeypatch, repo)

    with pytest.raises(ValueError, match="Only paid orders can request refund"):
        await service.create_refund(
            order_id=2001,
            user_id=101,
            reason="not needed",
            amount=99.0,
            order_status="DELIVERED",
            payment_status="PENDING",
        )

    assert repo.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("order_status", ["CREATED", "PAID", "CANCELLED"])
async def test_create_refund_rejects_order_statuses_that_do_not_allow_refund(
    monkeypatch,
    order_status,
):
    repo = FakeRefundRepository()
    service = make_service(monkeypatch, repo)

    with pytest.raises(ValueError, match="Order status does not allow refund"):
        await service.create_refund(
            order_id=2001,
            user_id=101,
            reason="changed mind",
            amount=99.0,
            order_status=order_status,
            payment_status="PAID",
        )

    assert repo.calls == []


@pytest.mark.asyncio
async def test_create_refund_rejects_duplicate_active_refund(monkeypatch):
    repo = FakeRefundRepository(active_refund=True)
    service = make_service(monkeypatch, repo)

    with pytest.raises(ValueError, match="Active refund already exists for this order"):
        await service.create_refund(
            order_id=2001,
            user_id=101,
            reason="changed mind",
            amount=99.0,
            order_status="DELIVERED",
            payment_status="PAID",
        )

    assert repo.calls == [("has_active_refund_for_order", 2001)]


@pytest.mark.asyncio
async def test_create_refund_creates_pending_review_refund_and_approval(monkeypatch):
    repo = FakeRefundRepository(active_refund=False)
    service = make_service(monkeypatch, repo)

    response = await service.create_refund(
        order_id=2001,
        user_id=101,
        reason="changed mind",
        amount=99.0,
        order_status="COMPLETED",
        payment_status="PAID",
    )

    assert response.id == 1001
    assert response.order_id == 2001
    assert response.status == "PENDING_REVIEW"
    assert repo.calls == [
        ("has_active_refund_for_order", 2001),
        ("create", 2001, 101, "changed mind", 99.0),
        ("create_approval", 1001),
    ]
