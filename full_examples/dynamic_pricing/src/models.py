from pydantic import BaseModel
from src.datasources import kafka_stream

from chalk import (DataFrame, FeatureTime, Windowed, _, feature, online,
                   windowed)
from chalk.features import features
from chalk.streams import stream


@features
class Hotel:
    id: int
    customer_hotel_interactions: "DataFrame[HotelInteraction]"
    num_rooms: int
    location: str
    mean_view_time_s: Windowed[float] = windowed(
        "15m",
        "30m",
        "1h",
        expression=_.customer_hotel_interactions[
            _.view_time_s, _.transaction_time > _.chalk_window
        ].sum(),
        materialization={"bucket_duration": "15m"},
    )
    count_distinct_views: Windowed[int] = windowed(
        "15m",
        "30m",
        "1h",
        expression=_.customer_hotel_interactions[
            _.view_time_s, _.transaction_time > _.chalk_window
        ].approx_count_distinct(),
        materialization={"bucket_duration": "15m"},
    )
    features_csv: str
    pricing: F.sagemaker_predict(F.string_to_bytes(_.features_csv))


@online
def prediction_to_csv(
    mvt: Hotel.mean_view_time_s,
    num_rooms: Hotel.num_rooms,
    location: Hotel.location,
    cdv: Hotel.count_distinct_views,
) -> Hotel.features_csv:
    return f'{mvt["15m"]},{mvt["30m"]},{mvt["1h"]},{num_rooms},{location},{cdv["15m"]},{cdv["30m"]},{cdv["1h"]}'


@features
class HotelInteraction:
    id: int
    customer_id: int
    hotel_id: Hotel.id
    view_time_s: float


# Set up a stream message to continously update materialized aggregates
class HotelInteractionMessage(BaseModel):
    id: int
    customer_id: int
    hotel_id: int
    view_time_s: float


@stream(kafka_stream)
def get_customer_hotel_interactions(
    message: HotelInteractionMessage,
) -> HotelInteraction:
    return HotelInteraction(
        id=message.id,
        customer_id=message.customer_id,
        hotel_id=message.hotel_id,
        view_time_s=message.view_time_s,
    )


# Run a query to get the price of a hotel from a sagemaker model prediction on
# stream aggregates and hotel features
if __name__ == "__main__":
    client = ChalkClient()
    dynamic_price = client.query(
        input={
            Hotel.id: 1,
        },
        output=[Hotel.pricing],
    )
