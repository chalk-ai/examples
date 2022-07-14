from datetime import datetime, timedelta
from decimal import Decimal

from chalk import realtime
from chalk.features import features, DataFrame, has_many
from banking.ach_withdrawal.resolvers import TransferStatus, AccountKind


@features
class Transfer:
    id: str
    amount: Decimal
    status: TransferStatus
    user_id: str

    from_id: str
    to_id: str


@features
class User:
    id: str
    transfers: DataFrame[Transfer] = has_many(lambda: Transfer.user_id == User.id)


@features
class Account:
    id: str
    kind: AccountKind
    transfers: DataFrame[Transfer] = has_many(lambda: Transfer.user_id == User.id)


@features
class ProposedTransfer:
    amount: Decimal
    from_id: str
    to_id: str

    from_account: Account
    to_account: Account


@realtime
def compute_limit(settlement_time: User.settlement_times):
    pass


@realtime
def compute_withdrawal(
    settlement_time: User.settlement_times,
    from_account: ProposedTransfer.from_account,
    to_account: ProposedTransfer.to_account,
) -> Account.available_balance:
    settled_deposits = (
        transfers[
            Transfer.status == TransferStatus.complete
            and Transfer.ts < datetime.now() - timedelta(days=90),
            Transfer.destination == account_id,
            Transfer.amount,
        ].sum()
        * settlement_time.ratio_90_day
    ) + (
        transfers[
            Transfer.status == TransferStatus.complete
            and Transfer.ts < datetime.now() - timedelta(days=30),
            Transfer.destination == account_id,
            Transfer.amount,
        ].sum()
        * settlement_time.ratio_90_day
    )
    return 4
