from pathlib import Path
from typing import Any

from chalk.features import unwrap_feature


class CustomModel:
    def __init__(self, url: str, dependencies: dict[str, Any], computes: Any):
        self.url = url
        self.dependencies = dependencies
        self.computes = unwrap_feature(computes)

    @classmethod
    def render_all(cls, *, header: str, path: Path | str, models: "list[CustomModel]"):
        children = "\n".join(model.render() for model in models)
        content = f"""{header}
from chalk import online
import requests


{children}
"""
        with open(path, "w") as f:
            f.write(content)

    def render(self):
        args: dict[str, str] = {}
        for k, v in self.dependencies.items():
            f = unwrap_feature(v)
            args[k] = f"{f.features_cls.__name__}.{f.attribute_name}"
        json_body = ", ".join(f'"{k}": {k}' for k in args.keys())
        returns = f"{self.computes.features_cls.__name__}.{self.computes.attribute_name}"

        return f"""
@online
def get_{self.computes.name}(
    {', '.join(f'{k}: {v}' for k, v in args.items())}
) -> {returns}:
    response = requests.post(
        "{self.url}",
        headers={{"accept": "application/json"}},
        json={{{json_body}}},
    )
    return response.json().get("prediction")
"""
