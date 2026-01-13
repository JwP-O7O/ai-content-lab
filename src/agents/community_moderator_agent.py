from src.agents.base_agent import BaseAgent
import asyncio


class CommunityModeratorAgent(BaseAgent):
    async def execute(self):
        # Simuleer het continu afhandelen van berichten.
        while True:
            # Simuleer het ontvangen van een bericht
            message = "Testbericht van gebruiker: 'Dit is een testbericht met een scheldwoord!'"  # Vervang door echte berichtenbron
            await self.handle_message(message)
            await asyncio.sleep(5)  # Wacht 5 seconden voor het volgende bericht.

    async def handle_message(self, message):
        """Simuleert het ontvangen en verwerken van een bericht."""
        print(f"Community Moderator ontving bericht: '{message}'")

        # Keyword-gebaseerde filtering
        keywords = ["scheldwoord", "haatspraak", "spam"]  # Voeg relevante keywords toe
        for keyword in keywords:
            if keyword in message.lower():  # Case-insensitive check
                print(
                    f"  WAARSCHUWING: Bericht bevat keyword '{keyword}'.  Markeren voor review."
                )
                # Hier kan complexere actie komen (bijv. markeren in een database, etc.)
                break  # Stop met controleren zodra een keyword is gevonden.

        print(
            "Community Moderator voert moderatie-actie uit."
        )  # Vervang door echte logica (kan nu conditioneel zijn)
