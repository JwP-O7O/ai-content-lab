import logging
import asyncio
import random
import time


class AbTestingAgent:
    def __init__(self, agent_id, data_source, experiment_config):
        self.agent_id = agent_id
        self.data_source = data_source
        self.experiment_config = experiment_config
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(f"AbTestingAgent_{self.agent_id}")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def run_experiment(self):
        try:
            self.logger.info(f"Agent {self.agent_id}: Starting experiment...")
            start_time = time.time()
            results = await self._execute_experiment()
            end_time = time.time()
            execution_time = end_time - start_time
            self.logger.info(
                f"Agent {self.agent_id}: Experiment completed in {execution_time:.2f} seconds. Results: {results}"
            )
            return results
        except Exception as e:
            self.logger.error(
                f"Agent {self.agent_id}: An error occurred: {e}", exc_info=True
            )
            return None

    async def _execute_experiment(self):
        try:
            # Simulate fetching data
            data = await self.data_source.get_data(
                self.experiment_config.get("data_source_params", {})
            )

            # Simulate experiment logic (A/B testing)
            variant_a_data = []
            variant_b_data = []

            for item in data:
                if random.random() < 0.5:
                    variant_a_data.append(item)
                else:
                    variant_b_data.append(item)

            variant_a_result = await self._process_variant(variant_a_data, "A")
            variant_b_result = await self._process_variant(variant_b_data, "B")

            return {"A": variant_a_result, "B": variant_b_result}

        except Exception as e:
            self.logger.error(
                f"Agent {self.agent_id}: Error during experiment execution: {e}",
                exc_info=True,
            )
            raise

    async def _process_variant(self, data, variant_name):
        try:
            self.logger.info(
                f"Agent {self.agent_id}: Processing variant {variant_name} with {len(data)} items"
            )
            await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate processing time
            result = sum(data) / len(data) if data else 0  # Simplified analysis
            self.logger.info(
                f"Agent {self.agent_id}: Variant {variant_name} result: {result}"
            )
            return result
        except ZeroDivisionError:
            self.logger.warning(
                f"Agent {self.agent_id}: Variant {variant_name} has no data, result is zero."
            )
            return 0
        except Exception as e:
            self.logger.error(
                f"Agent {self.agent_id}: Error processing variant {variant_name}: {e}",
                exc_info=True,
            )
            raise


class MockDataSource:
    async def get_data(self, params=None):
        await asyncio.sleep(0.1)  # Simulate data fetching time
        num_items = params.get("num_items", 100) if params else 100
        return [random.uniform(1, 100) for _ in range(num_items)]


async def main():
    data_source = MockDataSource()
    experiment_config = {"data_source_params": {"num_items": 200}}
    agent1 = AbTestingAgent(
        agent_id="agent_001",
        data_source=data_source,
        experiment_config=experiment_config,
    )
    agent2 = AbTestingAgent(
        agent_id="agent_002",
        data_source=data_source,
        experiment_config=experiment_config,
    )

    results1 = await agent1.run_experiment()
    results2 = await agent2.run_experiment()

    print(f"Agent 1 Results: {results1}")
    print(f"Agent 2 Results: {results2}")


if __name__ == "__main__":
    asyncio.run(main())
