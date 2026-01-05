import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.execution.research_agent import ResearchAgent

class StaffingAgent:
    def __init__(self):
        self.name = "StaffingAgent"
        self.ai = AIService()
        self.researcher = ResearchAgent()
        self.agents_dir = "src/autonomous_agents/execution"

    async def evaluate_team_needs(self):
        """Bepaalt of we een nieuwe agent nodig hebben"""
        # 1. Kijk wie we al hebben
        existing_agents = os.listdir(self.agents_dir)
        
        # 2. Doe onderzoek: Wat zijn nuttige autonomous agents?
        logger.info(f"[{self.name}] 🕵️ Marktonderzoek naar nieuwe agent rollen...")
        research = await self.researcher.conduct_research("Best types of autonomous AI agents for software development 2025")
        
        # 3. Vraag Gemini om een beslissing
        prompt = f"""
        WIJ ZIJN: Een autonoom AI systeem op een telefoon.
        HUIDIG TEAM: {existing_agents}
        ONDERZOEK: {research.get('summary', '')}
        
        OPDRACHT:
        Hebben we een NIEUWE agent nodig om onze capaciteit te vergroten?
        Zo ja, welke rol? (Bijv. DatabaseManager, SecurityGuard, DocumentationBot).
        Kies er max 1. Als we compleet zijn, antwoord 'GEEN'.
        
        ANTWOORD FORMAT:
        Rol: [NaamAgent]
        Bestandsnaam: [naam_agent.py]
        Beschrijving: [Wat doet hij?]
        Code: [De volledige Python class code]
        """
        
        response = await self.ai.generate_text(prompt)
        
        if "GEEN" in response or "Code:" not in response:
            logger.info(f"[{self.name}] Team is compleet voor nu.")
            return

        # 4. Parse en Bouw de Agent
        logger.warning(f"[{self.name}] 🧬 NIEUW LEVEN CREËREN...")
        
        try:
            filename = response.split("Bestandsnaam:")[1].split("\n")[0].strip()
            code_part = response.split("Code:")[1].strip()
            # Verwijder markdown quotes indien aanwezig
            code_part = code_part.replace("```python", "").replace("```", "")
            
            filepath = os.path.join(self.agents_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(code_part)
                
            logger.success(f"[{self.name}] 👶 {filename} is geboren! (Herstart vereist voor activatie)")
            return {"status": "born", "file": filename}
            
        except Exception as e:
            logger.error(f"[{self.name}] Geboorte mislukt: {e}")
