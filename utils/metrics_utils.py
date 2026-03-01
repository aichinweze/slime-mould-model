from models.models import Metrics

def aggregate_metrics(historical_metrics: list[Metrics], new_metric: Metrics) -> Metrics:
    sum_historical_docs = sum([metric.get_document_count() for metric in historical_metrics])
    weighted_latencies = sum([(metric.get_document_count() * metric.get_avg_latency()) for metric in historical_metrics])

    avg_latency_num = weighted_latencies + new_metric.get_avg_latency()
    avg_latency_denom = sum_historical_docs + new_metric.get_document_count()
    avg_latency = avg_latency_num / avg_latency_denom

    return Metrics(
        edge_id=new_metric.edge_id,
        avg_latency=avg_latency,
        document_count=new_metric.document_count+len(historical_metrics),
        timestamp=new_metric.timestamp,
    )

