import os
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

def clear_screen(): os.system('clear')

def get_last_log_lines(n=10):
    if not os.path.exists(LOG_FILE): return ["Wachten op logs..."]
    with open(LOG_FILE, 'r') as f: return [line.strip() for line in f.readlines()[-n:]]

def draw_dashboard():
    clear_screen()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║              🔵 ALL IN AI  V14.0                 ║{RESET}")
    print(f"{BOLD}{CYAN}║            S21 ULTRA - THE HIVE MIND             ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════╝{RESET}")
    
    status = os.popen("pgrep -f master_orchestrator").read()
    print(f"\n{BOLD}🤖 AGENT WORKFORCE:{RESET}")
    if status:
        print(f"  [{GREEN}ONLINE{RESET}] Master Orchestrator")
        print(f"  [{GREEN}ACTIVE{RESET}] GitHub Command Center")
        print(f"  [{GREEN}ACTIVE{RESET}] FeatureArchitect {YELLOW}(CODE){RESET}")
        print(f"  [{GREEN}ACTIVE{RESET}] VisionaryAgent {CYAN}(ART){RESET}")
        print(f"  [{GREEN}ACTIVE{RESET}] Gemini Writer")
    else:
        print(f"  [{RED}OFFLINE{RESET}] Systeem ligt stil")

    print(f"\n{BOLD}📝 LIVE LOGS:{RESET}")
    for log in get_last_log_lines(10):
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
