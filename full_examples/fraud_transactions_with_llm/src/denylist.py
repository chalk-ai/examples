import polars as pl
from chalk import chalk_logger


class Denylist:
    def __init__(
        self,
        source: str,
    ):
        self.source = source
        self.s = set()

    def load(self):
        try:
            self.s = set(pl.read_csv(self.source).to_series().to_list())
        except Exception as e:
            chalk_logger.warn(f"Failed to load denylist {e}", exc_info=True)

    def __contains__(self, email: str) -> bool:
        return email in self.s
