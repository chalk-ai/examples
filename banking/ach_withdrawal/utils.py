from enum import Enum


class AccountKind(Enum):
    plaid = "plaid"
    checking = "checking"
    savings = "savings"


class TransferStatus(Enum):
    complete = "settled"
    pending = "pending"
