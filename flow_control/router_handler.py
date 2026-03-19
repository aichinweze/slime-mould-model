import asyncio
import json
import random
import aiohttp
import google.auth.transport.requests
import google.oauth2.id_token
import logging
import google.cloud.logging

from datetime import datetime
from aiohttp import ClientSession
from google.api_core import retry
from google.cloud import pubsub_v1, firestore

from utils.firestore_utils import get_latest_graph_route_weights
from models.models import RouteWeight, GraphRouteWeights, time_format


def get_worker_route_weights(conductivity_list: list[float], source_node: int = 0, sink_node: int = 4) -> list[float]:
    worker_weights = []

    for idx, value in enumerate(conductivity_list):
        if idx != sink_node and idx != source_node:
            worker_weights.append((idx, value))

    sorted_weights = sorted(worker_weights)

    return [value for idx, value in sorted_weights]


def make_route_weights(
        conductivity_list: list[float],
        edge_delimiter: str = ">>",
        source_node: int = 0,
        sink_node: int = 4
) -> list[RouteWeight]:
    route_weights: list[RouteWeight] = []

    for index, value in enumerate(conductivity_list):
        if index != sink_node and index != source_node:
            edge_id = f'{source_node}{edge_delimiter}{index}'
            route_weight = RouteWeight(edge_id=edge_id, conductivity=value)
            route_weights.append(route_weight)

    return route_weights

def get_worker_weights(graph_route_weights: GraphRouteWeights, edge_delimiter: str = ">>") -> list[float]:
    route_weights = graph_route_weights.get_route_weights()

    worker_weights = []
    for route_weight in route_weights:
        nodes = route_weight.edge_id.split(edge_delimiter)
        destination_node = int(nodes[1])
        conductivity = route_weight.get_conductivity()
        worker_weights.append((destination_node, conductivity))

    sorted_weights = sorted(worker_weights)

    return [value for _, value in sorted_weights]


class RouteHandler:
    def __init__(self,
                 worker_routes: list[str],
                 project_id: str,
                 subscription_id: str,
                 error_topic_id: str,
                 max_messages: int,
                 firestore_client: firestore.Client,
    ):
        self.worker_routes = worker_routes
        self.project_id = project_id
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.max_messages = max_messages
        self.subscription_id = subscription_id
        self.error_topic_id = error_topic_id
        self.firestore_client = firestore_client

    def select_worker_route(self, worker_weights: list[float]):
        selected_route: str = random.choices(self.worker_routes, weights=worker_weights, k=1)[0]
        logging.debug("RouteHandler: selected route: {}".format(selected_route))
        return selected_route

    def get_messages_from_topic(self):
        subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)

        messages: list[dict] = []
        ack_ids: list[str] = []

        try:
            # The subscriber pulls a specific number of messages.
            response = self.subscriber.pull(
                request={ "subscription": subscription_path, "max_messages": self.max_messages },
                # Use a retry policy to handle transient errors and timeouts
                retry=retry.Retry(deadline=300),
                timeout=10.0
            )

            if not response.received_messages:
                logging.info("No messages received in this pull request.")
            else:
                for received_message in response.received_messages:
                    data: dict = json.loads(received_message.message.data.decode("utf-8"))
                    messages.append({"data": data})
                    ack_ids.append(received_message.ack_id)
        except Exception as e:
            logging.error("An error occurred during Pub/Sub pull: {}".format(e))

        return messages, ack_ids

    def publish_to_error_topic(self, status_code: int, worker_route: str, data: dict):
        data["error"] = f"Response {status_code} provided while sending message to worker at {worker_route}"
        json_payload = json.dumps(data)
        encoded_payload = json_payload.encode("utf-8")

        publish_result = self.publisher.publish(self.error_topic_id, data=encoded_payload)
        message_id = publish_result.result()
        logging.debug(f"Message ID: {message_id} published to topic {self.error_topic_id}")

    def close_subscriber(self):
        self.subscriber.close()

    async def send_requests(self, session: ClientSession, data: dict, worker_weights: list[float]):
        worker_route = self.select_worker_route(worker_weights)
        timestamp = datetime.now().strftime(time_format)
        data["send_timestamp"] = timestamp

        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, worker_route)

        logging.debug("RouteHandler: data to send: {}".format(data))

        async with session.request(
            method="POST",
            url=worker_route,
            json=data,
            headers={
                "Authorization": f"Bearer {id_token}",
                'Content-Type': 'application/json'
            }
        ) as response:
            if response.status != 200:
                logging.error("RouteHandler: Failed with response status: {}".format(response.status))
                logging.error("RouteHandler: response message: {}".format(response.text))
                self.publish_to_error_topic(response.status, worker_route, data)
            return await response.json(content_type=None)

    async def execute(self):
        # Read N messages from Pub/Sub topic
        logging.info("Executing route handler")
        logging.info("Subscription ID: {}".format(self.subscription_id))
        subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)

        # Read from topic and acknowledge messages
        messages_to_process, ack_ids = self.get_messages_from_topic()

        logging.debug("RouteHandler: Messages to process: {}".format(messages_to_process))
        logging.debug("RouteHandler: Ack IDs: {}".format(ack_ids))

        if len(messages_to_process) > 0:
            graph_route_weights = get_latest_graph_route_weights(self.firestore_client)
            worker_weights = get_worker_weights(graph_route_weights)

            async with aiohttp.ClientSession() as session:
                tasks = [self.send_requests(session, msg, worker_weights) for msg in messages_to_process]
                results = await asyncio.gather(*tasks)
                logging.debug("Route handler execution results...")
                logging.debug(results)

            # Acknowledges the received messages so they will not be sent again.
            if ack_ids:
                self.subscriber.acknowledge(
                    request={"subscription": subscription_path, "ack_ids": ack_ids}
                )
                logging.info(f"Received and acknowledged {len(ack_ids)} messages.")
