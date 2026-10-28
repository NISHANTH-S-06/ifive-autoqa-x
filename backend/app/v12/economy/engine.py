"""Autonomous Economy Module — Version 12.0 Autonomous Digital Civilization Platform.

Implements:
  - ResourceExchange  : Tokenized trade of compute credits, bandwidth & execution rights
  - ValueEngine       : Value contribution calculation, credit issuance & market equilibrium
  - DigitalEconomy    : Top-level economic orchestrator for the digital civilization economy
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class ResourceListing(BaseModel):
    listing_id: str = Field(default_factory=lambda: f"item-{uuid.uuid4().hex[:8]}")
    seller_org_id: str
    resource_type: str  # COMPUTE_CREDITS | BANDWIDTH_TOKENS | MODEL_INFERENCE_RIGHTS
    quantity: float = Field(1000.0)
    price_per_unit_credits: float = Field(1.0)
    status: str = Field("AVAILABLE")  # AVAILABLE | SOLD | CANCELLED
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class TradeTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: f"tx-{uuid.uuid4().hex[:8]}")
    listing_id: str
    buyer_org_id: str
    seller_org_id: str
    quantity: float
    total_credits: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: str = Field("SETTLED")

class ValueContribution(BaseModel):
    contribution_id: str = Field(default_factory=lambda: f"val-{uuid.uuid4().hex[:8]}")
    org_id: str
    activity_type: str  # CODE_GENERATION | QA_EXECUTION | THREAT_MITIGATION | KNOWLEDGE_SHARING
    value_score: float = Field(95.0)
    reward_credits_issued: float = Field(950.0)
    recorded_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

# ---------------------------------------------------------------------------
# Resource Exchange
# ---------------------------------------------------------------------------

class ResourceExchange:
    """Manages tokenized trading & market listings for compute, storage, and AI inference assets."""

    def __init__(self) -> None:
        self._listings: Dict[str, ResourceListing] = {}
        self._transactions: List[TradeTransaction] = []

        # Pre-seed market listings
        self.create_listing("org-alpha", "COMPUTE_CREDITS", quantity=5000.0, price_per_unit=1.0)
        self.create_listing("org-beta", "BANDWIDTH_TOKENS", quantity=10000.0, price_per_unit=0.5)

    def create_listing(
        self, seller_org_id: str, resource_type: str, quantity: float, price_per_unit: float
    ) -> ResourceListing:
        listing = ResourceListing(
            seller_org_id=seller_org_id,
            resource_type=resource_type,
            quantity=quantity,
            price_per_unit_credits=price_per_unit,
        )
        self._listings[listing.listing_id] = listing
        return listing

    def execute_trade(self, listing_id: str, buyer_org_id: str, quantity: float) -> TradeTransaction:
        listing = self._listings.get(listing_id)
        if not listing or listing.status != "AVAILABLE":
            raise ValueError(f"Listing {listing_id} is not available")

        actual_qty = min(quantity, listing.quantity)
        total_cost = actual_qty * listing.price_per_unit_credits
        listing.quantity -= actual_qty
        if listing.quantity <= 0:
            listing.status = "SOLD"

        tx = TradeTransaction(
            listing_id=listing_id,
            buyer_org_id=buyer_org_id,
            seller_org_id=listing.seller_org_id,
            quantity=actual_qty,
            total_credits=total_cost,
            status="SETTLED",
        )
        self._transactions.append(tx)
        return tx

    def list_listings(self, status: Optional[str] = None) -> List[ResourceListing]:
        if status:
            return [l for l in self._listings.values() if l.status == status]
        return list(self._listings.values())

    def get_trade_history(self) -> List[TradeTransaction]:
        return self._transactions

# ---------------------------------------------------------------------------
# Value Engine
# ---------------------------------------------------------------------------

class ValueEngine:
    """Calculates organizational value contribution and issues reward credits."""

    def __init__(self) -> None:
        self._contributions: List[ValueContribution] = []

    def record_contribution(
        self, org_id: str, activity_type: str, value_score: float = 95.0
    ) -> ValueContribution:
        reward = value_score * 10.0
        contrib = ValueContribution(
            org_id=org_id,
            activity_type=activity_type,
            value_score=value_score,
            reward_credits_issued=reward,
        )
        self._contributions.append(contrib)
        return contrib

    def get_org_rewards(self, org_id: str) -> float:
        return sum(c.reward_credits_issued for c in self._contributions if c.org_id == org_id)

    def get_value_stats(self) -> Dict[str, Any]:
        total_issued = sum(c.reward_credits_issued for c in self._contributions)
        return {
            "total_contributions_recorded": len(self._contributions),
            "total_reward_credits_issued": total_issued,
            "value_multiplier": 10.0,
            "economic_stability": "OPTIMAL_EQUILIBRIUM",
        }

# ---------------------------------------------------------------------------
# Digital Economy
# ---------------------------------------------------------------------------

class DigitalEconomy:
    """Top-level economic orchestrator for the digital civilization platform."""

    def __init__(self) -> None:
        self.exchange = ResourceExchange()
        self.value_engine = ValueEngine()

        # Seed initial value contribution
        self.value_engine.record_contribution("org-alpha", "CODE_GENERATION", 98.0)

    def get_economic_summary(self) -> Dict[str, Any]:
        listings = self.exchange.list_listings()
        available = [l for l in listings if l.status == "AVAILABLE"]
        return {
            "economy_status": "THRIVING",
            "market_listings": {
                "total": len(listings),
                "available": len(available),
            },
            "settled_transactions": len(self.exchange._transactions),
            "value_metrics": self.value_engine.get_value_stats(),
        }
