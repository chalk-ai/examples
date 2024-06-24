from chalk import Validation, online
from chalk.features import features, DataFrame, feature,  before_all, Vector, Primary
from sentence_transformers import SentenceTransformer


global model


@before_all
def load_embedding_model():
    global model
    model = SentenceTransformer('intfloat/e5-small-v2')


@features
class Movie:
    id: int
    title: str
    director: str
    year: int
    description: str
    rating: float = feature(min=0.0, max=10.0),
    runtime: int = feature(min=0.0),
    genres=set[str]
    embedding_text: str
    embedding: Vector[384]

@features
class SearchQuery:
    query: Primary[str]
    embedding: Vector[384]


@online
def get_movie_embedding_text(description: Movie.description, genres: Movie.genres, director: Movie.director) -> Movie.embedding_text:
    genres_text = ", ".join(list(genres))
    return f"passage: {description}. Directed by {director}. {genres_text}"

@online
def get_embedding(embedding_text: Movie.embedding_text) -> Movie.embedding:
    return model.encode(embedding_text)

@online
def get_query_embedding(embedding_text: SearchQuery.query) -> SearchQuery.embedding:
    return model.encode(f"query: {embedding_text}")


@online
def get_movies() -> DataFrame[Movie]:
    return DataFrame([
        Movie(
            id=0,
            title="High and Low",
            year=1963,
            director="Akira Kurosawa",
            rating=8.4,
            runtime=143,
            genres={"Crime", "thriller"},
            description="An executive of a Yokohama shoe company becomes a victim of extortion when his chauffeur's son is kidnapped by mistake and held for ransom."
        ),
        Movie(
            id=1,
            title="Spirited Away",
            year=2001,
            director="Hayao Miyazaki",
            rating=8.6,
            runtime=135,
            genres={"Animation", "Adventure", "Fantasy"},
            description="During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches and spirits, and where humans are changed into beasts.",
        ),
        Movie(
            id=2
            title="Anatomy of a Fall",
            year=2023,
            director="Justine Triet"
            rating=7.7,
            runtime=152,
            genres={"Crime", "Thriller"},
            description="A woman is suspected of murder after her husband's death; their half-blind son faces a moral dilemma as the main witness."
        ),
        Movie(
            id=3,
            title="The Cruz Brothers and Miss Malloy",
            year=1980,
            director="Kathleen Collins",
            rating=6.2,
            runtime=54,
            genres={"Drama"},
            description="Three Puerto Rican brothers retreat to a town in New York following their father's death during a bank robbery. There they are hired by an elderly Irishwoman to renovate her house so she can throw one last house party."
        ),
        Movie(
            id=4,
            title="In the Mood for Love",
            year=2000,
            director="Wong Kar Wai",
            rating=8.1,
            runtime=98,
            genres={"Romance","Drama"},
            description="Two neighbors form a strong bond after both suspect extramarital activities of their spouses. However, they agree to keep their bond platonic so as not to commit similar wrongs."
        ),
        Movie(
            id=5,
            title="Mad Max: Fury Road",
            year=2015,
            director="George Miller",
            rating=8.1,
            runtime=120,
            genres={"Action"}
            description="In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshipper and a drifter named Max.",
        )
    ])
