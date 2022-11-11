# Features
Chalk lets you spell our your features directly in Python.
To create a new FeatureSet, apply the `@features` decorator
to a Python class with typed attributes.

https://docs.chalk.ai/docs/features


## 1. Feature Types
Create a namespaced set of features.

**[1_feature_types.py](1_feature_types.py)**

```python
@features
class Book:
    name: str
    copyright_ended_at: datetime | None
    authors: list[str]
```
https://docs.chalk.ai/docs/features


## 2. Custom Feature Types
Use [pydantic](https://docs.chalk.ai/docs/feature-types#pydantic-models),
[attrs](https://docs.chalk.ai/docs/feature-types#attrs), 
[dataclasses.dataclass](https://docs.chalk.ai/docs/feature-types#dataclass),
or [custom types](https://docs.chalk.ai/docs/feature-types#custom-serializers) as feature values.

**[2_custom_feature_types.py](2_custom_feature_types.py)**

```python
@dataclass
class JacketInfo:
    title: str

@features
class Book:
    jacket: JacketInfo
    custom: CustomClass = feature(encoder=..., decoder=...)
```
https://docs.chalk.ai/docs/feature-types


## 3. Primary Keys
Set the primary key for an entity.

**[3_primary_keys.py](3_primary_keys.py)**

```python
@features
class Book:
    id: str
```
https://docs.chalk.ai/docs/features#primary-keys

## 4. Has One
Define a has-one relationship between feature classes.

**[4_has_one.py](4_has_one.py)**

```python
@features
class Author:
    id: str

@features
class Book:
    author_id: str
    author: Author = has_one(lambda: Book.author_id == Author.id)
```
https://docs.chalk.ai/docs/has-one


## 5. Has Many
Define a has-many relationship between feature classes.

**[5_has_many.py](5_has_many.py)**

```python
@features
class Book:
    author_id: str

@features
class Author:
    id: str
    books: DataFrame[Book] = has_many(lambda: Book.author_id == Author.id)
```
https://docs.chalk.ai/docs/has-many

## 6. Has One + Has Many
Define a has-many relationship between feature classes.

**[6_has_one_has_many.py](6_has_one_has_many.py)**

```python
@features
class Book:
    author_id: str
    author: "Author"

@features
class Author:
    id: str
    books: DataFrame[Book] = has_many(lambda: Book.author_id == Author.id)
```
https://docs.chalk.ai/docs/has-many#one-to-many


## 7. Feature Time
Access and override the time at which a feature should be recorded.

**[7_feature_time.py](7_feature_time.py)**

```python
@features
class Book:
    ts: datetime = feature_time()
```
https://docs.chalk.ai/docs/features#feature-time

## 8. Constructing Features
Create sets of features from your feature classes.

**[8_constructing_features.py](8_constructing_features.py)**

```python
assert Book(name="Anna Karenina") == Book(name="Anna Karenina")
assert Book(name="Anna Karenina") != Book(name="Anna Karenina", author="Leo Tolstoy")
x: Features[Book.author, Book.name] = Book(name="Anna Karenina", author="Leo Tolstoy")
assert dict(Book(name="Anna Karenina", pages=864)) == {
    "book.name": "Anna Karenina",
    "book.pages": 864,
}
```
https://docs.chalk.ai/docs/features#constructing-feature-classes
