import os

from google.api_core import retry
from google.cloud import pubsub_v1

# Local development script. Requires the Pub/Sub and Firestore emulators to be running.
# See firebase.json for emulator configuration. Not intended for production use.

subscriber = pubsub_v1.SubscriberClient()

os.environ["PROJECT_ID"] = "testing-123"
os.environ["SUBSCRIPTION_ID"] = "subscription-testing-123"
os.environ["MAX_MESSAGES"] = "10"
os.environ["PUBSUB_EMULATOR_HOST"]= "localhost:8085"

subscription_path = subscriber.subscription_path(os.environ["PROJECT_ID"], os.environ["SUBSCRIPTION_ID"])

messages = []
ack_ids = []

with subscriber:
    try:
        # The subscriber pulls a specific number of messages.
        response = subscriber.pull(
            request= { "subscription": subscription_path, "max_messages": int(os.environ["MAX_MESSAGES"]) },
            # Use a retry policy to handle transient errors and timeouts
            retry=retry.Retry(deadline=300),
            timeout=30.0
        )
    except Exception as e:
        print(f"An error occurred during Pub/Sub pull: {e}")

    if not response.received_messages:
        print("No messages received in this pull request.")

    for received_message in response.received_messages:
        data = received_message.message.data.decode("utf-8")
        messages.append({"data": data, "attributes": received_message.message.attributes })
        ack_ids.append(received_message.ack_id)
        print(f"Received message: {data}")
        print(f"Ack ID: {received_message.ack_id}")


