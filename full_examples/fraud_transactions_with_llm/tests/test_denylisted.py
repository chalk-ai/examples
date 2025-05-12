from chalk.client import ChalkClient
from src.models import Transaction, User


def test_email_features(client: ChalkClient):
    client.check(
        input={
            User.id: 1,
            User.email: "monica.1984+123@gmail.com",
            User.name: "Monica Geller",
        },
        assertions={
            User.email_username: "monica1984",
            User.domain_name: "gmail.com",
            User.name_email_match_score: 39.89,
        },
    )
    """
    Chalk Feature Value Check Table
    ┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ Kind   ┃ Name                        ┃ Value      ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │ Match  │ user.domain_name            │ gmail.com  │
    │ Match  │ user.email_username         │ monica1984 │
    │ Expect │ user.name_email_match_score │ 39.89      │
    │ Actual │ user.name_email_match_score │ 62.5       │
    └────────┴─────────────────────────────┴────────────┘
    """


def test_transactions(client: ChalkClient):
    client.check(
        input={
            User.id: 1,
            User.transactions: [
                Transaction(id=1, amount=110.0),
                Transaction(id=2, amount=900.0),
                Transaction(id=3, amount=300.0),
            ],
        },
        assertions={
            User.total_spend: 1310.0,
        },
    )
