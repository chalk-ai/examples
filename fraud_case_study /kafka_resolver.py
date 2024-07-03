from pydantic import BaseModel
from datasources import kafka
from chalk.streams import stream

# Pydantic models define the schema of the messages on the stream.
class TransactionMessage(BaseModel):
	id: int
	user_id: int
    timestamp: datetime
	vendor: str
	description: str
	amount: float
	country: str
	is_overdraft: bool

@stream(source=kafka)
def stream_resolver(message: TransactionMessage) -> Features[
    Transaction.id,
    Transaction.user_id,
    Transaction.timestamp,
    Transaction.vendor,
    Transaction.description,
    Transaction.amount,
    Transaction.country,
    Transaction.is_overdraft
]:
	return Transaction(
        id=message.id,
        user_id=message.user_id
        ts=message.timestamp,
        vendor=message.vendor,
        description=message.description,
        amount=message.amount,
        country=message.country,
        is_overdraft=message.is_overdraft
    )
