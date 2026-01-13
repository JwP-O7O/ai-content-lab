from .base_agent import BaseAgent


class ContentStrategistAgent(BaseAgent):
    async def execute(self, task_description: str) -> dict:
        """
        Voert de content strategie uit.

        Args:
            task_description: De beschrijving van de taak of de content strategie
                            die moet worden uitgevoerd.

        Returns:
            Een dictionary met de beschrijving van de strategie.  In dit basis voorbeeld
            wordt de originele taakomschrijving geretourneerd. Dit kan later uitgebreid worden.
        """
        return {"content_strategy": task_description}
