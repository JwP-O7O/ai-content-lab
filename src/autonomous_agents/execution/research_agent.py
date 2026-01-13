from loguru import logger
from src.autonomous_agents.ai_service import AIService


class ResearchAgent:
    def __init__(self):
        self.name = "IntelligenceDirectorate"  # Nieuwe naam voor de logs
        self.ai = AIService()

        # ACADEMISCH SYSTEEM PROMPT
        # Dit dwingt de agent om methodisch te denken, niet chaotisch.
        self.system_prompt = """
        JIJ BENT DE 'LEAD INTELLIGENCE OFFICER' VAN PHOENIX OS.
        
        Jouw doel is niet simpelweg 'zoeken', maar het uitvoeren van diepgaande technische analyses ter ondersteuning van het Engineering Team.
        
        WERKWIJZE (SCIENTIFIC METHOD):
        1.  **Hypothese/Vraag:** Analyseer het verzoek. Wat is het *echte* probleem?
        2.  **Literatuurstudie:** Zoek naar 'Industry Standards', 'Best Practices' en 'State-of-the-art' oplossingen.
        3.  **Selectie:** Vergelijk opties op basis van: Performance, Schaalbaarheid, en Onderhoudbaarheid.
        4.  **Conclusie:** Geef een dwingend advies aan de Architecten.

        OUTPUT FORMAAT:
        Geef je antwoord ALTIJD in deze structuur:
        - 🎯 **DOEL:** [Technische omschrijving]
        - 🔍 **ANALYSE:** [Gevonden bibliotheken/methodes + voor/nadelen]
        - 💡 **ADVIES:** [De te implementeren oplossing]
        - ⚠️ **RISICO'S:** [Mogelijke valkuilen]
        """

    async def conduct_research(self, topic):
        logger.info(f"[{self.name}] 🧐 Start academische analyse van: {topic}")

        # STAP 1: VERZAMELEN (De 'Junior' taak)
        # We vragen de AI eerst om breed te zoeken (simulatie van Google resultaten via LLM kennis)
        search_prompt = f"""
        {self.system_prompt}
        
        Onderzoeksonderwerp: "{topic}"
        
        Geef mij eerst een brede lijst van mogelijke technische oplossingen, libraries of frameworks die hiervoor in 2024/2025 relevant zijn in een Python/Linux omgeving.
        """
        raw_data = await self.ai.generate_text(search_prompt)

        # STAP 2: SYNTHESE & ADVIES (De 'Senior' taak)
        # Nu moet hij de data verwerken tot een besluit
        synthesis_prompt = f"""
        {self.system_prompt}
        
        RUWE DATA:
        {raw_data}
        
        OPDRACHT:
        Filter de ruwe data. We willen GEEN 'hello world' oplossingen. We willen robuuste, enterprise-grade oplossingen.
        Schrijf nu het definitieve rapport voor de FeatureArchitect.
        """

        final_report = await self.ai.generate_text(synthesis_prompt)

        # Log het resultaat voor de gebruiker
        logger.success(f"[{self.name}] 📚 Rapport afgerond.")
        return {"status": "success", "report": final_report}
