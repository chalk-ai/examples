from chalk.features import Features, features


@features
class Book:
    id: str
    name: str
    pages: int
    author: str


# Feature classes function like data classes, except that they
# are allowed to take only part of their arguments.
# Here, we're not providing `author` or `id`, even though
# they don't have default values or allow optional values.
assert Book(name="Anna Karenina") == Book(name="Anna Karenina")
assert Book(name="Anna Karenina") != Book(name="Anna Karenina", author="Leo Tolstoy")

# Feature classes are a bag of `Features`.
# If you use Chalk's mypy plugin, the types below will behave as you expect.
x: Features[Book.author, Book.name] = Book(name="Anna Karenina", author="Leo Tolstoy")

# `Features` is commutative, so `Features[A, B] == Feature[B, A]`
y: Features[Book.name, Book.author] = x

# Features are iterable, and iterate as tuples of
# (feature_name, feature_value)
for feature_name, value in Book(name="Anna Karenina", pages=864):
    print(f"{feature_name=}, {value=}")

# This iterable property means that features convert nicely into dicts
assert dict(Book(name="Anna Karenina", pages=864)) == {
    "book.name": "Anna Karenina",
    "book.pages": 864,
}

# And also into lists
assert [
    ("book.name", "Anna Karenina"),
    ("book.pages", 864),
] == list(Book(name="Anna Karenina", pages=864))
