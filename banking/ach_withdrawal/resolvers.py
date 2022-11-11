from decimal import Decimal
from enum import Enum

from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import (
    DataFrame,
    before,
    features,
    feature,
)


class AccountKind(Enum):
    plaid = "plaid"
    checking = "checking"
    savings = "savings"


class TransferStatus(Enum):
    complete = "settled"
    pending = "pending"


@features
class Transfer:
    id: str
    status: TransferStatus
    amount: float
    from_account: "Account"
    to_account: "Account"
    user: "User"


@features
class SettlementTimes:
    id: str
    ratio_7_day: float
    ratio_30_day: float
    ratio_60_day: float = 1


@features
class User:
    id: str
    risk_score: str
    account_id: str
    times_id: SettlementTimes.id
    settlement_times: SettlementTimes
    transfers: DataFrame[Transfer]


@features
class Balance:
    id: str
    available_balance: int
    ts = feature_time()
    ...


@features
class Account:
    id: str
    balances: DataFrame[Balance] = feature(max_staleness="40d")
    ...


class Account2:
    balances: DataFrame[Balance] = feature(max_staleness="30d")


ChalkClient(...).query(input={Balance.id: "124"}, output=[Balance.available_balance], max_stalensese={})


def wow(bs: Account.last_balances[Balance.available_balance > 300]) -> ...:
    ...


def refresh_fico(user: User.id, fico: DataFrame[User.fico].take(40)) -> User.fico:
    pass


@realtime(cron="1d")
def get_balances(
    aid: Account.id,
) -> Account.balances:
    return session.query(...).all(incremental=True)


@realtime(cron="1d")
def get_balances(aid: Account2.id) -> Account2.balances:
    return session.query(...).all(incremental=True)


#
# ChalkClient(...).query(
#     input={Account.id: "124"},
#     output=[
#         Account.balances[
#             Balance.available_balance,
#             Balance.ts,
#             after(days_ago=30),
#         ]
#     ],
# )


@features
class ProposedTransfer:
    from_account: Account
    to_account: Account


@features
class TransferLimit:
    amount: Decimal
    user: User
    from_account: Account
    to_account: Account


INTERNAL = {AccountKind.savings, AccountKind.checking}
EXTERNAL = {AccountKind.plaid}


@realtime(when=TransferLimit.from_account.kind in INTERNAL and TransferLimit.to_account.kind in INTERNAL)
def internal_transfer_limit(
    source_balance: TransferLimit.from_account.balances,
) -> TransferLimit.amount:
    """
    We have control over book transfers, so we'll allow moving any amount of money here.
    """
    return source_balance


@realtime(when=TransferLimit.from_account.kind in EXTERNAL and TransferLimit.to_account.kind in EXTERNAL)
def deposit_limit() -> TransferLimit.amount:
    return 0


@realtime(when=TransferLimit.from_account.kind in EXTERNAL)
def deposit_limit(
    email: User.email,
    from_balance: TransferLimit.from_account.available_balance,
) -> TransferLimit.amount:
    return max(0, from_balance - 30)


@realtime(when=TransferLimit.to_account.kind in EXTERNAL)
def withdrawal_limit(
    internal_accounts: TransferLimit.user.accounts[Account.kind in {AccountKind.savings, AccountKind.checking}],
    recent_deposits: TransferLimit.user.transfers[Transfer.from_account.kind == AccountKind.plaid, before(days_ago=90)],
) -> TransferLimit.amount:
    platform_balance = internal_accounts[Account.balances].sum()
    recent_deposits.sum()
    return 4


ChalkClient.get_training_dataframe(output=[])
