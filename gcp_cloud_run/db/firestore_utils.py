from google.cloud.firestore_v1 import CollectionReference
from google.cloud import firestore

from ..models.models import GraphRouteWeights


def collection_exists(collection_ref: CollectionReference) -> bool:
    query = collection_ref.limit(1)
    result = query.get()

    if len(result) > 0:
        return True
    else:
        return False

def get_latest_graph_route_weights(firestore_client: firestore.Client) -> GraphRouteWeights:
    route_weight_ref = firestore_client.collection(u'route_weight')

    get_latest_route_weight_query = route_weight_ref.order_by(
        field_path="iteration",
        direction=firestore.Query.DESCENDING
    ).limit(1)

    result = get_latest_route_weight_query.get()[0]

    graph_route_weights = GraphRouteWeights.from_dict(result.to_dict())

    return graph_route_weights

