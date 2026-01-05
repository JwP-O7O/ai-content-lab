import random

class ABTestingAgent:
    def __init__(self, variations):
        self.variations = variations
        self.results = {var: 0 for var in variations}
        self.total_tests = 0

    def execute(self, user_id=None, context=None):
        if not self.variations:
            return {}

        chosen_variation = random.choice(self.variations)
        self.total_tests += 1
        return {"variation": chosen_variation}

    def record_result(self, variation, success):
        if variation in self.results:
            self.results[variation] += 1 if success else 0

    def get_results(self):
        return self.results

    def get_conversion_rates(self):
        conversion_rates = {}
        for variation in self.variations:
            if self.total_tests > 0: # Avoid division by zero
                conversion_rates[variation] = (self.results.get(variation, 0) / self.total_tests) * 100
            else:
                conversion_rates[variation] = 0
        return conversion_rates

    def get_test_count(self):
        return self.total_tests