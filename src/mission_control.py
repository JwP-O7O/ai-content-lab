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
from rich import box

console = Console()

# --- CONFIGURATIE ---
# Icon: Het plaatje
# Color: Kleur van de tekst
# Tag: Korte naam voor in de kolom (max 6 letters)
AGENT_CONFIG = {
    "ResearchAgent":    {"c": "yellow",   "i": "🌍", "tag": "ZOEKT"},
    "WebArchitect":     {"c": "cyan",     "i": "🌐", "tag": "BOUWT"},
    "FeatureArchitect": {"c": "green",    "i": "⚙️", "tag": "CODET"},
    "VisionaryAgent":   {"c": "magenta",  "i": "🎨", "tag": "ART"},
    "GitHubListener":   {"c": "blue",     "i": "📡", "tag": "LEEST"},
    "GitPublisher":     {"c": "white",    "i": "📦", "tag": "PUSHT"},
    "SystemOptimizer":  {"c": "orange1",  "i": "🔧", "tag": "FIXT"},
    "Evolutionary":     {"c": "purple",    "i": "🧬", "tag": "DENKT"},
    "StaffingAgent":    {"c": "bright_white", "i": "👔", "tag": "HUURT"},
    "QualityAssurance": {"c": "red",      "i": "🛡️", "tag": "TEST"},
    "Master":           {"c": "white",    "i": "🤖", "tag": "CORE"},
    "IDLE":             {"c": "dim white","i": "•",  "tag": "WAIT"}
}

def get_file_tail(filepath, lines=50):
    try:
        if not os.path.exists(filepath): return []
        with open(filepath, 'r') as f:
            return f.readlines()[-lines:]
    except: return []

def parse_log_line(line):
    """Breekt een regel op in: (Icoon, Tag, Bericht, Kleur)"""
    line = line.strip()
    if not line: return None
    
    # 1. FILTER RUIS (Belangrijk!)
    if "Cycle #" in line or "Ruststand" in line or "---" in line:
        return None

    # 2. Bepaal Agent Config
    cfg = AGENT_CONFIG["IDLE"]
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
    
    # Check voor algemene status in de tekst
    if "ERROR" in line: cfg = {"c": "bold red", "i": "✖", "tag": "FOUT"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "KLAAR"}
    if "WARNING" in line: cfg = {"c": "yellow", "i": "⚠", "tag": "WARN"}

    # 3. Schoon bericht op
    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    
    # Verwijder [AgentNaam] tags uit bericht
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    
    # Verkort bericht voor mobiel scherm
    if len(msg) > 40: msg = msg[:38] + ".."

    return (cfg['i'], cfg['tag'], msg, cfg['c'])

def get_active_stats():
    """Haalt live data op voor de bovenbalk"""
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=10)
    last_action = "System Idle"
    active_agent = "Standby"
    
    if logs:
        last_line = logs[-1].strip()
        parts = last_line.split(' - ')
        last_action = parts[-1].strip() if len(parts) > 1 else last_line
        last_action = re.sub(r'\[.*?\]', '', last_action).strip()[:25]
        
        for key in AGENT_CONFIG:
            if key in last_line:
                active_agent = key.replace("Agent", "")
                break

    cycle = "0"
    for l in reversed(logs):
        if "Cycle #" in l:
            cycle = l.split("#")[-1].split(" ")[0]
            break
            
    return active_agent, last_action, cycle

def generate_layout(frame):
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="stats", size=4),
        Layout(name="feed")
    )

    # --- 1. HEADER (Compact & Strak) ---
    title = "[bold white]PHOENIX[/] [dim]OS[/] [bold cyan]V6.0[/]"
    layout["header"].update(Panel(Align.center(title), style="blue", box=box.HEAVY_EDGE))

    # --- 2. STATS (Grid View) ---
    agent, action, cycle = get_active_stats()
    
    # Animatie balkje
    load_len = int((math.sin(frame * 0.2) + 1) * 4) + 1
    load_bar = "█" * load_len
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    
    grid.add_row(
        "[dim]CYCLE[/]", "[dim]ACTIVE[/]", "[dim]LOAD[/]"
    )
    grid.add_row(
        f"[bold white]#{cycle}[/]", 
        f"[cyan]{agent}[/]", 
        f"[green]{load_bar}[/]"
    )
    
    layout["stats"].update(Panel(grid, style="white", box=box.ROUNDED))

    # --- 3. FEED (De Grote Schoonmaak) ---
    # We gebruiken hier een TABEL in plaats van platte tekst voor perfecte uitlijning
    log_table = Table(show_header=False, box=None, expand=True, padding=(0,1))
    log_table.add_column("Icon", width=2, justify="center")
    log_table.add_column("Tag", width=6, justify="left")
    log_table.add_column("Message", ratio=1) # Neemt de rest van de ruimte

    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=25)
    
    # Verwerk logs (van nieuw naar oud voor de lijst)
    count = 0
    display_logs = []
    
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            count += 1
        if count >= 16: break # Pas aan op schermhoogte

    # Voeg toe aan tabel (oudste onderaan? Nee, nieuwste bovenaan is handiger op mobiel dashboard)
    # Maar in logs lezen we vaak van boven naar beneden. Laten we nieuwste BOVENAAN zetten.
    for icon, tag, msg, color in display_logs:
        log_table.add_row(
            f"[{color}]{icon}[/]",
            f"[bold {color}]{tag}[/]",
            f"[dim white]{msg}[/]"
        )

    layout["feed"].update(Panel(log_table, title="[bold]NEURAL STREAM[/]", border_style="blue", box=box.ROUNDED))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=4) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.25)
