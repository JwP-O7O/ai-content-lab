import time
import os
import re
import math
import random
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.text import Text

console = Console()

# --- CONFIGURATIE ---
AGENT_CONFIG = {
    "ResearchAgent":    {"c": "bold yellow",  "i": "🌍", "load": 0.9},
    "WebArchitect":     {"c": "bold cyan",    "i": "🌐", "load": 0.8},
    "FeatureArchitect": {"c": "bold green",   "i": "⚙️", "load": 0.85},
    "VisionaryAgent":   {"c": "bold magenta", "i": "🎨", "load": 0.95},
    "GitHubListener":   {"c": "blue",         "i": "📡", "load": 0.3},
    "GitPublisher":     {"c": "white",        "i": "📦", "load": 0.4},
    "SystemOptimizer":  {"c": "orange1",      "i": "🔧", "load": 0.7},
    "Evolutionary":     {"c": "purple",       "i": "🧬", "load": 0.6},
    "StaffingAgent":    {"c": "bright_white", "i": "👔", "load": 0.5},
    "QualityAssurance": {"c": "red",          "i": "🛡️", "load": 0.75},
    "Master":           {"c": "white",        "i": "🤖", "load": 0.2},
    "IDLE":             {"c": "dim white",    "i": "💤", "load": 0.1}
}

def get_file_tail(filepath, lines=20):
    """Leest efficiënt de laatste regels"""
    try:
        if not os.path.exists(filepath): return []
        with open(filepath, 'r') as f:
            return f.readlines()[-lines:]
    except: return []

def get_active_agent_info():
    """Bepaalt WIE er nu werkt o.b.v. logs"""
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=5)
    if not logs: return ("IDLE", "System Booting...", 0.1)

    # We kijken naar de allerlaatste logregel
    last_line = logs[-1].strip()
    
    # Zoek agent naam
    agent_key = "IDLE"
    for key in AGENT_CONFIG:
        if key in last_line:
            agent_key = key
            break
            
    # Bericht opschonen
    msg = last_line.split(' - ')[-1]
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    if len(msg) > 25: msg = msg[:22] + "..."
    
    # Load bepalen (met beetje random jitter voor effect)
    base_load = AGENT_CONFIG.get(agent_key, {}).get("load", 0.1)
    jitter = random.uniform(-0.05, 0.05)
    current_load = min(1.0, max(0.1, base_load + jitter))
    
    return (agent_key, msg, current_load)

def get_load_bar(load, width=20):
    """Maakt een mooie gradient progress bar"""
    filled = int(load * width)
    
    # Kleur bepalen o.b.v. load
    if load < 0.3: color = "green"
    elif load < 0.6: color = "yellow"
    elif load < 0.8: color = "orange1"
    else: color = "red"
    
    bar = ""
    for i in range(width):
        if i < filled:
            bar += f"[{color}]█[/]"
        else:
            bar += f"[dim {color}]░[/]"
    return bar

def get_scanner_bar(frame, width=40):
    """De Cylon Scanner"""
    pos = int((math.sin(frame * 0.2) + 1) / 2 * (width - 1))
    chars = ["[dim blue]─[/]"] * width
    if 0 <= pos < width: chars[pos] = "[bold white]◆[/]"
    if 0 <= pos-1 < width: chars[pos-1] = "[bold cyan]━[/]"
    if 0 <= pos+1 < width: chars[pos+1] = "[bold cyan]━[/]"
    return "".join(chars)

def clean_log_line(line):
    parts = line.split(' - ')
    raw_msg = parts[-1].strip() if len(parts) > 1 else line.strip()
    
    cfg = AGENT_CONFIG["IDLE"]
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line: cfg = {"c": "bold red", "i": "☠️"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔"}

    msg = re.sub(r'\[.*?\]', '', raw_msg).strip()
    if len(msg) > 48: msg = msg[:45] + "..."
    
    return f"[{cfg['c']}]{cfg['i']} │ {msg}[/]"

def generate_layout(frame):
    layout = Layout()
    
    # INDELING: Header -> Scanner -> STATS (Top) -> LOGS (Bottom)
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="scanner", size=1),
        Layout(name="stats", size=6), # Groter voor meer detail
        Layout(name="feed")
    )

    # 1. HEADER
    blink = " " if frame % 10 < 5 else "_"
    layout["header"].update(Panel(Align.center(f"[bold white]PHOENIX SENTIENT CORE[/][dim]{blink}[/]"), style="blue"))

    # 2. SCANNER
    layout["scanner"].update(Align.center(get_scanner_bar(frame)))

    # 3. STATS PANEL (Real-Time Info)
    agent_key, agent_act, load = get_active_agent_info()
    agent_cfg = AGENT_CONFIG.get(agent_key, AGENT_CONFIG["IDLE"])
    
    # Haal cyclus nummer op (simpel hackje uit logs)
    cycle = "0"
    try:
        logs = get_file_tail("logs/autonomous_agents/agent.log", 30)
        for l in reversed(logs):
            if "Cycle #" in l:
                cycle = l.split("#")[-1].split(" ")[0].strip()
                break
    except: pass

    # Grid opbouw
    stats_table = Table(box=None, expand=True, show_header=False)
    stats_table.add_column("Label", justify="right", width=10)
    stats_table.add_column("Value", justify="left")
    
    # Rij 1: Huidige Agent (Met icoon en kleur)
    stats_table.add_row(
        "[bold white]ACTIVE:[/]", 
        f"[{agent_cfg['c']}]{agent_cfg['i']} {agent_key}[/]"
    )
    # Rij 2: Huidige Actie
    stats_table.add_row(
        "[dim white]ACTION:[/]", 
        f"[cyan]{agent_act}[/]"
    )
    # Rij 3: Neural Load Bar
    stats_table.add_row(
        "[bold white]LOAD:[/]", 
        get_load_bar(load, width=25)
    )
    # Rij 4: System Info
    running = os.popen("pgrep -f master_orchestrator").read()
    status = "🟢 ONLINE" if running else "🔴 OFFLINE"
    stats_table.add_row(
        "[dim white]SYS:[/]", 
        f"{status}  [dim]Cycle: #{cycle}[/]"
    )

    layout["stats"].update(Panel(stats_table, title="[bold]LIVE METRICS[/]", border_style="green"))

    # 4. LOG FEED
    logs_raw = get_file_tail("logs/autonomous_agents/agent.log", lines=18)
    clean_logs = []
    for line in reversed(logs_raw):
        if "Cycle #" in line or "Ruststand" in line: continue
        clean = clean_log_line(line)
        clean_logs.append(clean)
    
    layout["feed"].update(Panel("\n".join(clean_logs), title="[bold]NEURAL STREAM[/]", border_style="cyan"))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=5) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.1)
