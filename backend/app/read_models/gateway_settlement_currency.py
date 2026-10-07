from dataclasses import dataclass


@dataclass(frozen=True)
class GatewaySettlementCurrency:
    name: str
    settlement_currency: str
