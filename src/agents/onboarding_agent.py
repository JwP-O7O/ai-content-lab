from .base_agent import BaseAgent

class OnboardingAgent(BaseAgent):
    async def execute(self):
        """
        Voert de onboarding-procedure uit voor een nieuwe gebruiker.
        Momenteel retourneert deze methode een lege dictionary. In de toekomst
        zal deze methode logica bevatten om taken als het instellen van
        gebruikersaccounts, het versturen van welkomstmails, etc. te
        verwerken.
        """
        return {}