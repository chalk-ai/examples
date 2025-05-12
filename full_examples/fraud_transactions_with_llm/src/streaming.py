from datetime import datetime

from chalk import Features, stream
from chalk.streams import KafkaSource
from pydantic import BaseModel

from src.models import Transaction

transactions_topic = KafkaSource(name="transactions")


class TransactionMessage(BaseModel):
    id: str
    memo: str
    amount: float
    at: datetime


@stream(source=transactions_topic)
def process_stream_message(
    msg: TransactionMessage,
) -> Features[
    Transaction.id,
    Transaction.amount,
    Transaction.at,
    Transaction.memo,
]:
    return Transaction(
        id=msg.id,
        amount=msg.amount,
        at=msg.at,
        memo=msg.memo,
    )
