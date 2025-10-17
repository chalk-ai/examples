import chalk.functions as F
from chalk.features import Primary, _, features


@features
class GithubArchive:
    id: int
    path: Primary[str]
    api_url: str
    stars: int = -1
    is_valid_repo_path: bool = F.regexp_like(
        expr=_.path,
        pattern=r"^[a-zA-Z0-9_-]+\/[a-zA-Z0-9._-]+$",
    )
    url: str | None = F.if_then_else(
        condition=_.is_valid_repo_path,
        if_true="https://github.com/" + _.path,
        if_false=None,
    )
