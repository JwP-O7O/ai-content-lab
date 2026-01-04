import os
import json
import time
from datetime import datetime

# Kleuren
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

LOG_FILE = "logs/autonomous_agents/agent.log"
MEMORY_FILE = "data/improvement_plans/lessons_learned.json"

def clear_screen(): os.system('clear')

def get_last_log_lines(n=8):
    if not os.path.exists(LOG_FILE): return ["Wachten op logs..."]
    with open(LOG_FILE, 'r') as f: return [line.strip() for line in f.readlines()[-n:]]

def get_learned_lessons():
    if not os.path.exists(MEMORY_FILE): return "0 patronen"
    with open(MEMORY_FILE, 'r') as f: return f"{len(f.readlines())} patronen"

def draw_dashboard():
    clear_screen()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║     AUTONOMOUS SYSTEM V12 - S21 ULTRA            ║{RESET}")
    print(f"{BOLD}{CYAN}║         HIVE MIND (BUILDER & CODER)              ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════╝{RESET}")
    
    status = os.popen("pgrep -f master_orchestrator").read()
    print(f"\n{BOLD}🤖 AGENT WORKFORCE:{RESET}")
    if status:
        print(f"  [{GREEN}ONLINE{RESET}] Master Orchestrator")
        print(f"  [{GREEN}ACTIVE{RESET}] GitHub Listener {YELLOW}(COMMAND CENTER){RESET}")
        print(f"  [{GREEN}ACTIVE{RESET}] FeatureArchitect {YELLOW}(BUILDER){RESET}")
        print(f"  [{GREEN}ACTIVE{RESET}] Gemini Writer {CYAN}(CONTENT){RESET}")
        print(f"  [{GREEN}ACTIVE{RESET}] CodeHealth & GitPublisher")
    else:
        print(f"  [{RED}OFFLINE{RESET}] Systeem ligt stil")

    print(f"\n{BOLD}🧠 INTELLIGENCE:{RESET} {get_learned_lessons()}")
    print(f"\n{BOLD}📝 LIVE LOGS:{RESET}")
    for log in get_last_log_lines(8):
        if "ERROR" in log: print(f"  {RED}✖ {log.split('|')[-1].strip()}{RESET}")
        elif "WARNING" in log: print(f"  {YELLOW}⚠ {log.split('|')[-1].strip()}{RESET}")
        elif "SUCCESS" in log: print(f"  {GREEN}✔ {log.split('|')[-1].strip()}{RESET}")
        elif "INFO" in log: print(f"  {CYAN}ℹ {log.split('|')[-1].strip()}{RESET}")

    print(f"\n{BOLD}🎮 CONTROLS:{RESET} [r]efresh | [k]ill | [s]tart | [q]uit")

def main():
    while True:
        draw_dashboard()
        choice = input(f"\n> ").lower().strip()
        if choice == 'q': break
        elif choice == 'k': os.system("pkill -f master_orchestrator")
        elif choice == 's': os.system("nohup python3 -m src.autonomous_agents.master_orchestrator > logs/autonomous_agents/agent.log 2>&1 &")
        time.sleep(0.5)

if __name__ == "__main__": main()
