from chalk.features import features, feature, is_primary


# Feature classes have exactly one primary key,
# which by default, is taken to be the field with
# the name `id`.
@features
class Book1:
    id: str


# If you want to name your primary key something other than `id`,
# you can explicitly assign it a primary key
@features
class Book2:
    book_id: str = feature(primary=True)


assert is_primary(Book2.book_id)
assert is_primary(Book1.id)
