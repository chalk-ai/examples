from pydantic import BaseModel
from src.datasources import kafka_stream

from chalk import online
from chalk.features import features, feature, DataFrame, _
from chalk.streams import stream, Windowed, windowed


@features
class Hotel:
    id: int
    num_rooms: int
    location: str

    # We specify a has-many join to interactions by annotating hotel interactions with
    # a DataFrame of HotelInteractions.

    hotel_interactions: "DataFrame[HotelInteraction]"

    # We define two windowed materialized aggregates which will be calculated from our stream:
    # every time a message from the hotel_interaction topic is processed
    # these windowed aggregate features are updated.

    mean_view_time_s: Windowed[float] = windowed(
        "15m",
        "30m",
        "1h",
        expression=_.hotel_interactions[
            _.customer_id, _.transaction_time > _.chalk_window
        ].sum(),
        materialization={"bucket_duration": "15m"},
    )
    count_distinct_views: Windowed[int] = windowed(
        "15m",
        "30m",
        "1h",
        expression=_.hotel_interactions[
            _.customer_id, _.transaction_time > _.chalk_window
        ].approx_count_distinct(),
        materialization={"bucket_duration": "15m"},
    )

    # Running ML models on realtime features

    # features_csv is our encoded csv string of feautures—we define this feature
    # using a python online resolver.
    features_csv: str

    # We can run a sagemaker prediction directly from chalk on a set of encoded prediction
    # features
    pricing: bytes = feature(
        expression=F.sagemaker_predict(F.string_to_bytes(_.features_csv))
        # by setting a max staleness of 30m, we cache this feature and don't rerun prediction
        # if the pricing feature for a particular hotel has been computed in the last 30m
        max_staleness="30m",
    )


@features
class HotelInteraction:
    id: int
    customer_id: int
    hotel_id: Hotel.id
    view_time_s: float


@online
def prediction_to_csv(
    mvt: Hotel.mean_view_time_s,
    num_rooms: Hotel.num_rooms,
    location: Hotel.location,
    cdv: Hotel.count_distinct_views,
) -> Hotel.features_csv:
    return f'{mvt["15m"]},{mvt["30m"]},{mvt["1h"]},{num_rooms},{location},{cdv["15m"]},{cdv["30m"]},{cdv["1h"]}'


# Set up a stream message to continously update materialized aggregates
class HotelInteractionMessage(BaseModel):
    id: int
    customer_id: int
    hotel_id: int
    view_time_s: float


# To connect our stream to our features, we set up a python function that maps our stream messages
# (which are defined as pydantic dataclasses) into our Chalk Feature Classes.
@stream(source=kafka_stream)
def get_customer_hotel_interactions(
    message: HotelInteractionMessage,
) -> HotelInteraction:
    return HotelInteraction(
        id=message.id,
        customer_id=message.customer_id,
        hotel_id=message.hotel_id,
        view_time_s=message.view_time_s,
    )


# Now, we can run a query to get the price of a hotel from a sagemaker model prediction on
# stream aggregates and postgres features:
if __name__ == "__main__":
    from chalk.client import ChalkClient
    client = ChalkClient()
    dynamic_price = client.query(
        input={
            Hotel.id: 1,
        },
        output=[Hotel.pricing],
    )
