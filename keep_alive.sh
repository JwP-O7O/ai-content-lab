#!/bin/bash

# Kleurtjes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🛡️  AIS Watchdog Gestart (Infinity Mode)${NC}"
echo "Druk op CTRL+C om de watchdog te stoppen."

while true; do
    # Check of de orchestrator draait
    if ! pgrep -f "master_orchestrator" > /dev/null; then
        echo -e "${RED}⚠️  Agent is neergestort of gestopt. Herstarten...${NC}"
        
        # Start de agent opnieuw in achtergrond
        nohup python3 -m src.autonomous_agents.master_orchestrator >> logs/autonomous_agents/agent.log 2>&1 &
        
        echo -e "${GREEN}✅  Agent herstart via Watchdog. (Check logs)${NC}"
    else
        # Hij draait nog, doe niks.
        # We checken elke 60 seconden.
        : 
    fi
    
    # Wacht 1 minuut voor volgende check
    sleep 60
done
