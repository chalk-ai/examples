"""In this example we set up a withdrawl model in Chalk
with Users, Accounts, and Transfers.

In it, we implement flexible withdrawl limits based on
a User risk scores.
"""

import dataclasses

from chalk import online
from chalk.features import (
    DataFrame,
    before,
    features,
    feature,
)
from enum import Enum


class AccountKind(Enum):
    savings = 0
    checking = 1


@dataclasses.dataclass
class Holdback:
    # Percentage of funds deposited within the
    # last 7d that are eligible for withdrawal
    holdback_7d: float

    # Percentage of funds deposited within the
    # last 30d that are eligible for withdrawal
    holdback_30d: float

    # Percentage of funds deposited within the
    # last 90d that are eligible for withdrawal
    holdback_90d: float


@features
class Transfer:
    id: str
    amount: float

    from_account_id: str
    from_account: "Account"

    to_account_id: str
    to_account: "Account"


@features
class User:
    id: str

    # min and max value for the feature are set
    # to 0 and 100 respectively
    risk_score: float = feature(min=0, max=100)
    holdback: Holdback
    transfers: DataFrame[Transfer]


@features
class Account:
    id: str
    kind: AccountKind
    is_internal: bool
    balance: float


@features
class TransferLimit:
    amount: float
    user: User

    from_account_id: str
    from_account: Account

    to_account_id: str
    to_account: Account


@online
def is_internal(kind: Account.kind) -> Account.is_internal:
    return kind in {AccountKind.savings, AccountKind.checking}


@online(when=TransferLimit.from_account.is_internal and TransferLimit.to_account.is_internal)
def internal_transfer_limit(
    source_balance: TransferLimit.from_account.balances,
) -> TransferLimit.amount:
    """
    We have control over book transfers, so we'll allow moving any amount of money here.
    """
    return source_balance


@online(when=TransferLimit.from_account.is_internal is False and TransferLimit.to_account.is_internal is False)
def deposit_limit() -> TransferLimit.amount:
    """
    We can't make a transfer between two external accounts
    """
    return 0


@online(when=TransferLimit.from_account.is_internal is False)
def deposit_limit(
    from_balance: TransferLimit.from_account.available_balance,
) -> TransferLimit.amount:
    """
    A user can deposit almost all of their money,
    but there could be in-flight balances, so to
    avoid NSFs, we'll allow for an extra $30 buffer.
    """
    return max(0, from_balance - 30)


@online
def get_settlement_time(risk_score: User.risk_score) -> User.holdback:
    """
    Users will have a holdback configuration decided by their risk score.
    The riskier a user is, the lower the percentage of funds that have
    recently been deposited that will be eligible for withdrawal.
    """
    if risk_score < 30:
        return Holdback(
            holdback_7d=0.2,
            holdback_30d=0,
            holdback_90d=0,
        )

    if risk_score < 70:
        return Holdback(
            holdback_7d=0.4,
            holdback_30d=0.3,
            holdback_90d=0.1,
        )

    return Holdback(
        holdback_7d=1,
        holdback_30d=0.5,
        holdback_90d=0.3,
    )


@online(when=TransferLimit.to_account.is_internal is False)
def withdrawal_limit(
    internal_accounts: TransferLimit.user.accounts[Account.is_internal is True],
    deposits_last_90: TransferLimit.user.transfers[Transfer.from_account.is_internal is False, before(days_ago=90)],
    user_settlement: TransferLimit.user.holdback,
) -> TransferLimit.amount:
    """
    Withdrawals are more dangerous. Here, we'll let you move
    money based on how long it has been settled in the account.
    """
    platform_balance = internal_accounts[Account.balance].sum()
    return platform_balance - (
        deposits_last_90[before(days_ago=7)].sum() * user_settlement.holdback_7d
        + deposits_last_90[before(days_ago=30)].sum() * user_settlement.holdback_30d
        + deposits_last_90[before(days_ago=90)].sum() * user_settlement.holdback_90d
    )
