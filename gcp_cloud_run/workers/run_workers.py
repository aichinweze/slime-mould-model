from gcp_cloud_run.workers.worker_a import WorkerA
from gcp_cloud_run.workers.worker_b import WorkerB
from gcp_cloud_run.workers.worker_c import WorkerC

# Get source and target currency from P/S message

# TODO: Write output to publishing topic
    # source_currency
    # target_currency
    # amount

source_currency_a = "BTC"
target_currency_a = "USD"

source_currency_b = "ETH"
target_currency_b = "USD"

source_currency_c = "FET"
target_currency_c = "USD"

worker_a = WorkerA(source_currency=source_currency_a, target_currency=target_currency_a)
worker_b = WorkerB(source_currency=source_currency_b, target_currency=target_currency_b, number_of_loops=5)
worker_c = WorkerC(source_currency=source_currency_c, target_currency=target_currency_c)

print("Worker A")
worker_a_out = worker_a.execute()

print("Worker B")
worker_b_out = worker_b.execute()

print("Worker C")
worker_c_out = worker_c.execute()
