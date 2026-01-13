import os
import json
import importlib
import aiofiles
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
        research = await self.researcher.conduct_research(
            "Best types of autonomous AI agents for software development 2025"
        )

        # 3. Vraag Gemini om een beslissing
        prompt = f"""
        WIJ ZIJN: Een autonoom AI systeem op een telefoon.
        HUIDIG TEAM: {existing_agents}
        ONDERZOEK: {research.get("summary", "")}

        OPDRACHT:
        Het laatste onderzoek geeft aan dat specifieke agents effectiever zijn.  Kies een rol die zeer specifiek is voor een taak binnen softwareontwikkeling.
        Hebben we een NIEUWE agent nodig om onze capaciteit te vergroten?
        Zo ja, kies er 1 en geef een zeer specifieke rol (bijv. 'CodeReviewer voor de 'user authentication module', 'PerformanceTester voor API endpoints', etc.)
        Als we compleet zijn, antwoord 'GEEN'.

        ANTWOORD FORMAT (in JSON):

        {{
            "rol": "[Specifieke NaamAgent, of 'GEEN']",
            "bestandsnaam": "[naam_agent.py, of leeg]",
            "beschrijving": "[Wat doet hij? Zeer specifiek]",
            "code": "[De volledige Python class code, of leeg]"
        }}

        """

        response_text = await self.ai.generate_text(prompt)

        try:
            response_json = json.loads(response_text)

            if response_json.get("rol", "").upper() == "GEEN":
                logger.info(f"[{self.name}] Team is compleet voor nu.")
                return

            # Extra validatie
            if not all(
                key in response_json
                for key in ["rol", "bestandsnaam", "beschrijving", "code"]
            ):
                raise ValueError("JSON response is incomplete")

            #  Check of de rol specifiek genoeg is (simpele versie)
            if (
                "specifiek" not in response_json["beschrijving"].lower()
                and "taak" not in response_json["beschrijving"].lower()
            ):
                logger.warning(
                    f"[{self.name}] De agent rol lijkt niet specifiek genoeg. Response: {response_json['beschrijving']}"
                )
                return  # Skip de creatie

            filename = response_json["bestandsnaam"]
            code_part = response_json["code"]

            if not filename or not code_part:  # Check of filename en code leeg zijn
                logger.info(
                    f"[{self.name}] Team is compleet voor nu (of er ging iets fout met de response)."
                )
                return

            filepath = os.path.join(self.agents_dir, filename)

            # Eerst een simpele validatie (syntax check)
            try:
                module_name = filename.replace(".py", "").replace(
                    "/", "."
                )  # Aanpassen voor path
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                logger.info(f"[{self.name}] Code validatie geslaagd: {filename}")
            except Exception as e:
                logger.error(
                    f"[{self.name}] Code validatie mislukt voor {filename}: {e}"
                )
                # Optioneel: Verwijder het bestand als de validatie faalt.
                if os.path.exists(filepath):
                    os.remove(filepath)
                return

            async with aiofiles.open(filepath, "w") as f:
                await f.write(code_part)  # Gebruik await

            logger.success(
                f"[{self.name}] 👶 {filename} is geboren! (Herstart vereist voor activatie)"
            )
            return {"status": "born", "file": filename}

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                f"[{self.name}] Geboorte mislukt (fout met parsing JSON response): {e}\nResponse: {response_text}"
            )
        except Exception as e:
            logger.exception(f"[{self.name}] Geboorte mislukt: {e}")
