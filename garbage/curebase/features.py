from chalk.features import features, DataFrame


@features
class TrialMemberFeatures:
    id: str
    trial_id: str
    age: float
    is_control: bool


@features
class TrialFeatures:
    id: str
    # The raw data coming from Postgres
    raw_json: str

    # Features that we'll derive from Postgres
    trial_name: str
    trial_member: DataFrame[TrialMemberFeatures]
    control_mean_age: float


@features
class SentryFeatures:
    id: str
    exception: str


@features
class EmployeeFeatures:
    id: str
    salary: float
    full_name: str


@features
class AnalyticsFeatures:
    id: str
    user_id: str
    page_name: str
