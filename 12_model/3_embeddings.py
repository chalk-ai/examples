from chalk import Validation, embedding, online
from chalk.features import (
    DataFrame,
    Primary,
    Vector,
    before_all,
    feature,
    features,
    has_many,
)


@features(max_staleness="infinity")
class FAQDocument:
    id: int
    title: str
    body: str
    link: str
    embedding: Vector = embedding(
        input=lambda: FAQDocument.body,
        provider="openai",
        model="text-embedding-ada-002",
    )


@features
class SearchQuery:
    query: Primary[str]
    max_runtime: int = None
    embedding: Vector = embedding(
        input=lambda: SearchQuery.query,
        provider="openai",
        model="text-embedding-ada-002",
    )
    faqs: DataFrame[FAQDocument] = has_many(
        lambda: SearchQuery.embedding.is_near(FAQDocument.embedding)
    )
    response: str


@online
def generate_response(
    # Query for the three most relevant documents, and select their links
    nearest_faqs: SearchQuery.faqs[FAQDocument.link, :3]
) -> SearchQuery.response:
    return "\n".join(nearest_faqs[FAQDocument.link])


@online
def get_faqs() -> (
    DataFrame[FAQDocument.id, FAQDocument.title, FAQDocument.body, FAQDocument.link]
):
    return DataFrame(
        [
            FAQDocument(
                id=1,
                title="What is the difference between the online store and the offline store?",
                body="The online store is intended to store features for low-latency retrieval in online query. Typically, the online store is implemented using Redis, DynamoDB, or (in some cases) Postgres. The offline store is intended to store historical logs of all previously ingested or computed features. It is used to compute large historical training sets. It is typically implemented using BigQuery, Snowflake, or other data warehouses.",
                link="https://docs.chalk.ai/docs/faq#what-is-the-difference-between-the-online-store-and-the-offline-store",
            ),
            FAQDocument(
                id=2,
                title="Can we do RBAC (Role Based Access Control) within Chalk?",
                body="Yes! Within the dashboard you can assign roles with different permissions to different users. The default roles available are shown below.",
                link="https://docs.chalk.ai/docs/faq#can-we-do-rbac-role-based-access-control-within-chalk",
            ),
            FAQDocument(
                id=3,
                title="What are the necessary steps for us to get Chalk in our system?",
                body="Please reach out via your support channel and we’d be happy to walk you through how to get Chalk setup running on your cloud infrastructure!",
                link="https://docs.chalk.ai/docs/faq#what-are-the-necessary-steps-for-us-to-get-chalk-in-our-system",
            ),
            FAQDocument(
                id=4,
                title="Does Chalk have a feature catalog?",
                body="Yes! You can view all the features for all namespaces deployed in your environments, along with some metadata on recent activity and updates.",
                link="https://docs.chalk.ai/docs/faq#does-chalk-have-a-feature-catalog",
            ),
            FAQDocument(
                id=5,
                title="Can I upload features into the online store with an API endpoint?",
                body="Yes! In addition to streaming and scheduled bulk ingests of features, you can submit requests using the upload_features SDK endpoints to synchronously ingest features into the online or offline stores using API clients.",
                link="https://docs.chalk.ai/docs/faq#can-i-upload-features-into-the-online-store-with-an-api-endpoint",
            ),
            FAQDocument(
                id=6,
                title="How are resources provisioned for my Chalk cluster, and can I modify the configuration?",
                body="We have default resource configurations for general environments. You can modify the configuration for your project’s cloud resources by modifying the specs under Settings > Resources > Advanced Resource Configuration. You must hit Save and Apply Changes in order for your configuration changes to go through. If you are not sure how you should configure your cloud resources, please reach out to us in your support channel!",
                link="https://docs.chalk.ai/docs/faq#how-are-resources-provisioned-for-my-chalk-cluster-and-can-i-modify-the-configuration",
            ),
        ]
    )
