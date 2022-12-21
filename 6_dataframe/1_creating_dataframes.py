from chalk.features import features, DataFrame
import pandas as pd


@features
class User:
    id: int
    email: str


# Constructing an empty DataFrame
df = DataFrame()
assert df.is_empty and not df.is_not_empty

# Constructing from a Python dictionary
DataFrame.from_dict(
    {
        User.id: [1, 2],
        User.email: ["elliot@chalk.ai", "samantha@chalk.ai"],
    }
)

# Constructing from a Pandas DataFrame
pandas_df = pd.DataFrame(
    {
        User.id: [1, 2],
        User.email: ["elliot@chalk.ai", "samantha@chalk.ai"],
    }
)
DataFrame(pandas_df)

# Loading a .csv
DataFrame.read_csv("s3://...")
DataFrame.read_parquet("s3://...")
