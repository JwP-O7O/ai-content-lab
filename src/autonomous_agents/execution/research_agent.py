import os
from googlesearch import search
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class ResearchAgent:
    def __init__(self):
        self.name = "ResearchAgent"
        self.ai = AIService()
        self.output_dir = "data/research"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def search_web(self, query, max_results=5):
        """Voert een zoekopdracht uit via Google"""
        logger.info(f"[{self.name}] 🌍 Zoeken op Google naar: '{query}'")
        results_data = []
        try:
            # advanced=True geeft ons Titel + Beschrijving + URL
            # We halen iets meer resultaten op om filters te overleven
            search_generator = search(query, num_results=max_results, advanced=True)
            
            for result in search_generator:
                results_data.append({
                    "title": result.title,
                    "body": result.description,
                    "href": result.url
                })
                # Stop als we genoeg hebben
                if len(results_data) >= max_results:
                    break
                    
            return results_data
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def conduct_research(self, topic):
        """Hoofdfunctie: Zoeken, Analyseren, Rapporteren"""
        logger.info(f"[{self.name}] 🕵️ Start onderzoek: {topic}")
        
        # 1. Verzamel Ruwe Data
        raw_results = self.search_web(topic)
        if not raw_results:
            return {"status": "failed", "error": "Geen resultaten gevonden"}

        # Maak context string voor Gemini
        context_text = ""
        for idx, res in enumerate(raw_results):
            context_text += f"BRON {idx+1}: {res['title']}\nURL: {res['href']}\nSAMENVATTING: {res['body']}\n\n"

        # 2. Analyseer met Gemini
        prompt = f"""
        Je bent een Expert Onderzoeker.
        ONDERWERP: {topic}
        
        GEVONDEN ZOEKRESULTATEN:
        {context_text}
        
        OPDRACHT:
        Schrijf een helder, beknopt onderzoeksrapport (in Markdown).
        - Vat de belangrijkste punten samen op basis van de snippets.
        - Geef antwoord op de vraag.
        - Vermeld de bronnen (URLs).
        """
        
        report = await self.ai.generate_text(prompt)
        
        # 3. Opslaan
        safe_title = "".join([c for c in topic if c.isalnum() or c=='_'])[:20]
        filename = f"research_{safe_title}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"# 🕵️ Onderzoek: {topic}\n\n{report}")
            
        logger.success(f"[{self.name}] 📚 Rapport opgeslagen: {filepath}")
        return {"status": "success", "file": filepath, "summary": report}
