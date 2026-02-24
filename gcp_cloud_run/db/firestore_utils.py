from google.cloud import firestore
from google.cloud.firestore_v1 import CollectionReference
from google.cloud.firestore_v1.base_document import BaseDocumentReference

from ..models.models import GraphRouteWeights


def collection_exists(collection_ref: CollectionReference) -> bool:
    query = collection_ref.limit(1)
    result = query.get()

    if len(result) > 0:
        return True
    else:
        return False

def document_exists(document_ref: BaseDocumentReference) -> bool:
    doc = document_ref.get()
    doc_exists = doc.exists
    print(f"Checking if document exists in Metrics store: {doc_exists}: data: {doc.to_dict()}")

    if doc_exists:
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

