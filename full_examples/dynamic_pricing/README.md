# Dynamic Price Prediction with Chalk

In this example we set up some code showing how to write dynamic pricing features in Chalk. The goal```
is to show how a company that dynamically prices hotels might define their features. This example assumes that data is defined in two places:
- A Postgres database with a `hotel` table which contains basic features like `num_rooms` and `location`,
- A Kafka stream which updates in realtime with customer-hotel interaction information.
