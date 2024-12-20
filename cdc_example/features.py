from datetime import datetime
from decimal import Decimal
from typing import Optional
from chalk.features import features, DataFrame, has_many

@features
class User:
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    transactions: DataFrame['Transaction'] = has_many(lambda: Transaction.user_id == User.id)

@features
class Transaction:
    id: int
    user_id: int
    amount: Decimal
    merchant: str
    transaction_date: datetime
    status: str
    user: Optional['User'] = None  # Will be resolved via SQL resolver
