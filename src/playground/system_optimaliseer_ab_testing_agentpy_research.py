from src.agents.base_agent import BaseAgent
import random


class AbTestingAgent(BaseAgent):
    async def execute(self):
        """
        Voert een vereenvoudigde A/B test uit. Selecteert willekeurig een variant,
        simuleert data en retourneert de resultaten. In een echte implementatie
        zou je hier echte data, parameters, logging en analyse toevoegen.
        """
        variants = ["A", "B"]
        selected_variant = random.choice(variants)

        # Simuleer data
        num_visitors = 1000  # Aantal bezoekers per variant (pas aan)
        if selected_variant == "A":
            # Stel conversion rates in
            conversion_rate_a = 0.10
            num_conversions = int(num_visitors * conversion_rate_a)
            result = {
                "variant": "A",
                "visitors": num_visitors,
                "conversions": num_conversions,
                "conversion_rate": num_conversions / num_visitors,
            }

        else:
            # Stel conversion rates in
            conversion_rate_b = 0.12
            num_conversions = int(num_visitors * conversion_rate_b)
            result = {
                "variant": "B",
                "visitors": num_visitors,
                "conversions": num_conversions,
                "conversion_rate": num_conversions / num_visitors,
            }
        return result
