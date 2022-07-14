from datetime import datetime

from chalk import offline
from chalk.features import features, Features


@features
class Book:
    id: str
    name: str

    # By default, Chalk marks the time a feature was
    # created as the time that its resolver was run.
    # However, you may want to provide a custom value
    # for this time for data sources like events tables.
    # You can inspect the time a feature was created
    # and set the time for when a feature was created
    # by creating a feature time feature.
    # By default, a feature is a feature time feature if
    # it has the name `ts` and a type of `datetime.datetime`:
    ts: datetime

    # However, you may also explicitly set the feature time
    # via the `chalk.features.FeatureTime` type:
    #
    #    timestamp: FeatureTime
    #


# To set the time a feature was created, assign the feature
# when you resolve it:
@offline
def fn(book_id: Book.id) -> Features[Book.name, Book.ts]:
    return Book(
        name="Anna Karenina",
        ts=datetime(month=9, day=12, year=1877),
    )


# Then, when you sample offline data, the name feature will
# be treated as having been created at the provided date.
