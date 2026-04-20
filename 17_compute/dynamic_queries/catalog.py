"""Feature catalog the agent is allowed to request.

Mirrors the subset of the `Transaction` and `User` namespaces deployed in the
staging fraud-template project that actually resolve from the online store
(https://staging.chalk.dev/projects/tmnmau5shs3qe/environments/tmnmc9beyujew).

Every entry here has been confirmed to resolve via POST /v1/query/online with
primary key `transaction.id`. To widen the agent's reachable feature set, add
entries here; if a feature has no online resolver / max_staleness it cannot be
queried online and should stay out of the list.
"""

FEATURE_CATALOG: list[dict[str, str]] = [
    {
        "name": "transaction.amount",
        "type": "float",
        "description": "USD amount of this transaction.",
    },
    {
        "name": "transaction.user_id",
        "type": "int",
        "description": "User who initiated the transaction.",
    },
    {
        "name": "transaction.ts",
        "type": "datetime",
        "description": "Timestamp the transaction was recorded.",
    },
    {
        "name": "transaction.user.socure_score",
        "type": "float",
        "description": "Socure identity-risk score. Cached up to 5 minutes. Higher = riskier.",
    },
    {
        "name": "transaction.user.median_transaction_amount",
        "type": "float",
        "description": "Median historical transaction amount for this user. Useful baseline for spotting outlier spend.",
    },
    {
        "name": "transaction.user.today_cached",
        "type": "date",
        "description": "Today's date from the user row (1-hour cache). Low signal for fraud.",
    },
    {
        "name": "transaction.user.gender",
        "type": "str",
        "description": "User-reported gender (m/f/x). Low signal for fraud — included as a decoy the agent should skip.",
    },
]
