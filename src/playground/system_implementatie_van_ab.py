import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ABTestingAgent:
    def __init__(self, variations):
        """
        Initializes the ABTestingAgent.

        Args:
            variations (list): A list of variation names (strings).
        """
        if not isinstance(variations, list) or not all(isinstance(var, str) for var in variations):
            raise ValueError("Variations must be a list of strings.")

        self.variations = variations
        self.results = {var: 0 for var in variations}  # Successes per variation
        self.test_counts = {var: 0 for var in variations}  # Number of tests per variation
        self.total_tests = 0  # Total number of tests

        logging.info(f"ABTestingAgent initialized with variations: {variations}")

    def execute(self, user_id=None, context=None):
        """
        Executes an A/B test by choosing a random variation.

        Args:
            user_id:  Optional user ID (not used in this implementation).
            context:  Optional context (not used in this implementation).

        Returns:
            dict: A dictionary containing the chosen variation. Returns an empty dict if no variations are available.
        """
        if not self.variations:
            logging.warning("No variations available. Returning empty dictionary.")
            return {}

        chosen_variation = random.choice(self.variations)
        self.test_counts[chosen_variation] += 1  # Increment test count for the chosen variation
        self.total_tests += 1
        logging.info(f"Executed test. Chosen variation: {chosen_variation}")
        return {"variation": chosen_variation}

    def record_result(self, variation, success):
        """
        Records the result of a test.

        Args:
            variation (str): The name of the variation.
            success (bool): True if the test was successful, False otherwise.
        """
        if not isinstance(variation, str):
            logging.error(f"Invalid variation type. Expected string, got: {type(variation)}")
            return
        if variation not in self.variations:
            logging.warning(f"Variation '{variation}' not found in available variations. Ignoring result.")
            return
        try:
            if success:
                self.results[variation] += 1
            conversion_rates = self.get_conversion_rates()
            logging.info(f"Recorded result for variation '{variation}': success={success}, tests={self.test_counts[variation]}, successes={self.results[variation]}, conversion_rate={conversion_rates.get(variation, 0.0)}%")

        except Exception as e:
            logging.error(f"Error recording result for variation '{variation}': {e}")


    def get_results(self):
        """
        Gets the number of successes per variation.

        Returns:
            dict: A dictionary where keys are variation names and values are the number of successes.
        """
        logging.info(f"Returning results: {self.results}")
        return self.results

    def get_conversion_rates(self):
        """
        Calculates and returns the conversion rates for each variation.

        Returns:
            dict: A dictionary where keys are variation names and values are the conversion rates (as percentages).
        """
        conversion_rates = {}
        for variation in self.variations:
            if self.test_counts[variation] > 0:
                conversion_rate = (self.results[variation] / self.test_counts[variation]) * 100
                conversion_rates[variation] = round(conversion_rate, 2)  # Round to 2 decimal places
            else:
                conversion_rates[variation] = 0.0  # Or handle as you see fit (e.g., None, NaN)
        logging.info(f"Conversion rates: {conversion_rates}")
        return conversion_rates


    def get_test_count(self):
        """
        Gets the total number of tests.

        Returns:
            int: The total number of tests.
        """
        logging.info(f"Returning total test count: {self.total_tests}")
        return self.total_tests

    def get_test_counts_per_variation(self):
        """
        Gets the number of tests performed for each variation.

        Returns:
            dict: A dictionary where keys are variation names and values are the test counts.
        """
        logging.info(f"Returning test counts per variation: {self.test_counts}")
        return self.test_counts