from chalk import online
from chalk.features import features, DataFrame, has_one, has_many

@features
class SeriesLink:
    id: int
    books: "Book" = has_many(
        lambda: SeriesLink.id==Book.series_id
    )

@features
class Author:
	id: int
	name: str
	books: "DataFrame[Book]"

@features
class PrequelLink:
    id: int
    prequel_id: int
    book: "Book" = has_one(
            lambda:  Book.id==PrequelLink.prequel_id
    )

@features
class Book:
    id: int
    title: str
    author_id: Author.id
    prequel_id: PrequelLink.id | None
    prequel: PrequelLink | None = has_one(lambda: Book.id==PrequelLink.prequel_id)
    series_id: SeriesLink.id | None
    series: SeriesLink = has_one(lambda: SeriesLink.id==Book.series_id)


@online
def get_books() -> DataFrame[Book]:
    return DataFrame([
        Book(id=1, title="To the Lighthouse", author_id=1, series_id=None, prequel_id=None),
        Book(id=2, title="The Fellowship of the Ring", series_id=1, author_id=2, prequel_id=None),
        Book(id=3, title="The Two Towers", series_id=1, author_id=2, prequel_id=2),
        Book(id=4, title="The Return of the King", series_id=1, author_id=2, prequel_id=3)
    ])

@online
def get_prequel_links() -> DataFrame[PrequelLink]:
    return DataFrame([
        PrequelLink(id=3, prequel_id=2),
        PrequelLink(id=4, prequel_id=3)
    ])

@online
def get_series_links() -> DataFrame[SeriesLink]:
    return DataFrame([SeriesLink(id=1)])
