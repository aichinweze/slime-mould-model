from ..models.models import Metrics

def aggregate_metrics(historical_metrics: list[Metrics], new_metric: Metrics) -> Metrics:
    sum_historical_docs = sum([metric.document_count for metric in historical_metrics])
    weighted_latencies = sum([(metric.document_count * metric.avg_latency) for metric in historical_metrics])

    avg_latency = (weighted_latencies + new_metric.avg_latency) / sum_historical_docs + new_metric.document_count

    return Metrics(
        edge_id=new_metric.edge_id,
        avg_latency=avg_latency,
        document_count=new_metric.document_count+len(historical_metrics),
        timestamp=new_metric.timestamp,
    )

