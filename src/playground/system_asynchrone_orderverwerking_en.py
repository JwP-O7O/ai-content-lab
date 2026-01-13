import asyncio
import random
import time


class OrderProcessingError(Exception):
    pass


async def simulate_order_processing(order_id, delay=None, success_rate=0.9):
    if delay is None:
        delay = random.uniform(0.1, 1.0)
    await asyncio.sleep(delay)
    if random.random() < success_rate:
        print(f"Order {order_id}: Processed successfully in {delay:.2f}s")
        return f"Order {order_id} processed"
    else:
        raise OrderProcessingError(f"Order {order_id}: Processing failed")


async def process_order(order_id):
    try:
        return await simulate_order_processing(order_id)
    except OrderProcessingError as e:
        print(f"Error processing order {order_id}: {e}")
        return f"Order {order_id} failed"
    except Exception as e:
        print(f"Unexpected error processing order {order_id}: {e}")
        return f"Order {order_id} failed due to unexpected error"


async def main():
    num_orders = 10
    order_ids = list(range(1, num_orders + 1))

    start_time = time.time()

    tasks = [process_order(order_id) for order_id in order_ids]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    print("\nOrder Processing Results:")
    for result in results:
        print(result)
    print(f"\nTotal processing time: {end_time - start_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
