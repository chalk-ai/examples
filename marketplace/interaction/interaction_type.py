from enum import Enum


class InteractionType(str, Enum):
    PRODUCT_INQUIRY = "productInquiry"
    ORDER_PLACEMENT = "orderPlacement"
    FEEDBACK_AND_REVIEWS = "feedbackAndReviews"
