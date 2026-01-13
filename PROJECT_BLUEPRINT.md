# PROJECT PHOENIX (OPENCODE-AI) - BLUEPRINT & ROADMAP

## 1. Projectdefinitie & Scope

**Projectnaam:** Phoenix V17 (Opencode-AI)
**Type:** Autonoom Multi-Agent Software Development Systeem
**Platform:** Android (Termux) / Python 3.12+ Environment

### 🎯 Primaire Doelen
Het creëren van een volledig autonome AI-medewerker die lokaal op Android draait en in staat is om:
1.  High-level opdrachten ("Bouw een webshop", "Analyseer deze markt") om te zetten in werkende software of rapporten.
2.  Zichzelf te onderhouden, refactoren en verbeteren (Self-Healing).
3.  Veilig te opereren binnen een lokale omgeving met versiebeheer als vangnet.

### 👥 Gebruikersgroep
- **Primaire Gebruiker:** System Architect / Developer (JwP).
- **Rol:** Geeft strategische sturing; Phoenix voert de executie uit.

### ✅ Succescriteria
- **Stabiliteit:** Het systeem crasht niet bij API-fouten of netwerkuitval (99.9% uptime van de loop).
- **Autonomie:** Kan complexe taken (zoals "maak een game") uitvoeren zonder tussenkomst voor elke bestandswijziging.
- **Veiligheid:** Geen dataverlies door hallucinaties (Git-integratie is verplicht).
- **Snelheid:** Asynchrone verwerking van LLM-aanvragen om de throughput te maximaliseren.

---

## 2. Technische Stack

- **Core:** Python 3.12+ (Asyncio framework).
- **AI Intelligence:** Google Gemini 2.0 Flash / Pro (via `google-generativeai`).
- **Database / State:** SQLite (voor taakbeheer en geheugen) + JSON (voor configuratie).
- **Versiebeheer:** Git (automatische commits voor en na wijzigingen).
- **Communicatie:** Inter-Process Communication (IPC) via database polling of lokale socket (vervanging van file-polling).
- **Logging:** Loguru (gestructureerde logging).

---

## 3. Architectuurprincipes

1.  **Async-First:** De core loop (`MasterOrchestrator`) mag nooit blokkeren. Alle I/O (netwerk, disk) moet asynchroon zijn.
2.  **Safety-by-Design:**
    -   *Git Safety Net:* Geen schrijfactie zonder voorafgaande commit.
    -   *Sandbox:* Agents mogen niet buiten de werkmap treden (behalve specifieke temp dirs).
3.  **Modulariteit (Squads):**
    -   *Orchestrator:* De "CEO" die taken verdeelt.
    -   *Backend Squad:* Python/Database specialisten.
    -   *Frontend Squad:* HTML/JS/CSS specialisten.
    -   *Intelligence Squad:* Research & Analysis.
4.  **Hallucinatie-Check:** Code gegenereerd door AI moet syntactisch gevalideerd worden (via `ast.parse` of linters) voordat het wordt opgeslagen.

---

## 4. Project Roadmap

### 📅 Fase 1: Fundament & Stabilisatie (Huidige Focus)
*Doel: Het oplossen van de huidige bottlenecks (blocking calls, race conditions).*
- [ ] **Mijlpaal 1.1:** Asynchrone transformatie van `AIService` en `LLMClient`.
- [ ] **Mijlpaal 1.2:** Implementatie van `TaskQueue` via SQLite (vervanging van `local_commands.json` race condition).
- [ ] **Mijlpaal 1.3:** Git Safety Net integratie in `FeatureArchitect` en `WebArchitect`.

### 📅 Fase 2: Geheugen & Context
*Doel: Agents slimmer maken over langere tijd.*
- [ ] **Mijlpaal 2.1:** Vector Database (of lichte JSON-based embedding search) voor code-kennis.
- [ ] **Mijlpaal 2.2:** "Project Context" bestand dat automatisch wordt bijgewerkt (wat is er gebouwd, waar staat het).

### 📅 Fase 3: Kwaliteitsbewaking (Self-Correction)
*Doel: De AI controleert zijn eigen werk.*
- [ ] **Mijlpaal 3.1:** Auto-Linter integratie (Ruff/Black) na generatie.
- [ ] **Mijlpaal 3.2:** Unit Test Generator agent die tests schrijft én uitvoert na wijzigingen.
- [ ] **Mijlpaal 3.3:** Error Recovery Loop (als een test faalt, repareert de AI het zelf).

### 📅 Fase 4: Interface & Interactie
*Doel: Gebruikersgemak.*
- [ ] **Mijlpaal 4.1:** Real-time Web Dashboard (i.p.v. alleen logs).
- [ ] **Mijlpaal 4.2:** Spraak-interactie (optioneel, via Termux API).

---

## 5. Taakverdeling (Agents)

| Agent | Rol | Verantwoordelijkheid |
|-------|-----|----------------------|
| **Master Orchestrator** | Project Manager | Polling van taken, toewijzen aan juiste squad, bewaken van de loop. |
| **Feature Architect** | Backend Lead | Schrijven van Python code, database schema's, systeem-logica. |
| **Web Architect** | Frontend Lead | Bouwen van HTML/JS/CSS, UI/UX design. |
| **Research Agent** | Analist | Verzamelen van informatie, samenvatten van documentatie, strategie bepalen. |
| **Git Publisher** | Release Manager | Versiebeheer, commit messages genereren, veilige rollbacks. |

---

## 6. Communicatieprotocol

Alle communicatie tussen de gebruiker en het systeem verloopt via gestandaardiseerde Task Objects in de database:

```json
{
  "task_id": "uuid",
  "status": "pending|processing|completed|failed",
  "priority": "high|normal|low",
  "squad": "backend",
  "instruction": "Bouw een API endpoint voor user login",
  "context": "Gebruik JWT en SQLite",
  "created_at": "timestamp",
  "result_path": "src/auth/login.py"
}
```
