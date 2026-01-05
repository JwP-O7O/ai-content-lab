import time
import os
import re
import math
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich import box
from rich.style import Style

console = Console()

# --- KLEURENPALET ---
NEON_COLORS = ["bright_cyan", "bright_magenta", "bright_green", "bright_yellow", "bright_blue"]

AGENT_CONFIG = {
    "ResearchAgent":    {"c": "bright_yellow", "i": "🌍", "tag": "ZOEKT"},
    "WebArchitect":     {"c": "bright_cyan",   "i": "🌐", "tag": "BOUWT"},
    "FeatureArchitect": {"c": "bright_green",  "i": "⚙️", "tag": "CODET"},
    "VisionaryAgent":   {"c": "bright_magenta","i": "🎨", "tag": "ART"},
    "GitHubListener":   {"c": "dodger_blue1",  "i": "📡", "tag": "LEEST"},
    "GitPublisher":     {"c": "white",         "i": "📦", "tag": "PUSHT"},
    "SystemOptimizer":  {"c": "orange1",       "i": "🔧", "tag": "FIXT"},
    "Evolutionary":     {"c": "medium_purple1","i": "🧬", "tag": "DENKT"},
    "StaffingAgent":    {"c": "white",         "i": "👔", "tag": "HR"},
    "QualityAssurance": {"c": "bright_red",    "i": "🛡️", "tag": "TEST"},
    "Master":           {"c": "white",         "i": "🤖", "tag": "CORE"},
    "IDLE":             {"c": "dim white",     "i": "•",  "tag": "WAIT"}
}

def get_file_tail(filepath, lines=60):
    try:
        if not os.path.exists(filepath): return []
        with open(filepath, 'r') as f:
            return f.readlines()[-lines:]
    except: return []

def parse_log_line(line):
    line = line.strip()
    if not line: return None
    
    # 1. FILTER RUIS (Genadeloos filteren voor een schone lijst)
    skip_terms = ["Cycle #", "Ruststand", "---", "WAIT", "IDLE", "HERSTART", "Nieuwe functionaliteit"]
    if any(x in line for x in skip_terms): return None

    # 2. Bepaal Agent Config
    cfg = AGENT_CONFIG["IDLE"]
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
    
    if "ERROR" in line: cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "WARNING" in line: cfg = {"c": "yellow", "i": "⚠", "tag": "WARN"}

    # 3. Schoon bericht op
    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r'\[.*?\]', '', msg).strip() # Verwijder [Tags]
    
    # Max lengte voor mobiel
    if len(msg) > 35: msg = msg[:32] + "..."

    return (cfg['i'], cfg['tag'], msg, cfg['c'])

def get_scanner_bar(frame, width=40):
    """De Cylon Scanner met Neon Glow"""
    pos = int((math.sin(frame * 0.25) + 1) / 2 * (width - 1))
    chars = ["[dim grey11]─[/]"] * width
    
    # De Kern
    if 0 <= pos < width: chars[pos] = "[bold white]◆[/]"
    # De Gloed
    if 0 <= pos-1 < width: chars[pos-1] = "[bold cyan]━[/]"
    if 0 <= pos+1 < width: chars[pos+1] = "[bold cyan]━[/]"
    if 0 <= pos-2 < width: chars[pos-2] = "[dim cyan]⋅[/]"
    if 0 <= pos+2 < width: chars[pos+2] = "[dim cyan]⋅[/]"
    
    return "".join(chars)

def get_active_agent_info():
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=5)
    if not logs: return ("STANDBY", "System Ready")
    
    last_line = logs[-1].strip()
    active_agent = "PHOENIX"
    for key in AGENT_CONFIG:
        if key in last_line:
            active_agent = key
            break
            
    return active_agent.replace("Agent", "").upper()

def generate_layout(frame):
    # Roteer border kleur op basis van tijd
    border_color = NEON_COLORS[int(frame / 5) % len(NEON_COLORS)]
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="stats", size=3),
        Layout(name="feed")
    )

    # --- 1. HEADER (Scanner + Titel) ---
    # We combineren de scanner en de titel in één strak paneel
    scanner = get_scanner_bar(frame, width=30)
    title_text = f"\n[bold white]PHOENIX[/] [dim]OS[/] [bold {border_color}]V7.0[/]\n{scanner}"
    
    layout["header"].update(Panel(
        Align.center(title_text), 
        border_style=border_color,
        box=box.HEAVY_EDGE
    ))

    # --- 2. STATS (Compacte Balk) ---
    agent = get_active_agent_info()
    
    # Grid voor nette verdeling
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    
    # Knipperende cursor
    blink = "█" if frame % 4 < 2 else " "
    
    grid.add_row(
        f"[bold {border_color}]ACTIVE TASK[/]",
        f"[bold white]{agent}[/]",
        f"[dim cyan]PROCESSING {blink}[/]"
    )
    
    layout["stats"].update(Panel(grid, border_style="dim white", box=box.ROUNDED))

    # --- 3. FEED (Strakke Tabel) ---
    # Dit lost je probleem op met de lijnen die niet kloppen
    log_table = Table(
        show_header=True, 
        header_style=f"bold {border_color}", 
        box=None, 
        expand=True, 
        padding=(0, 1),
        collapse_padding=True
    )
    
    # Definieer vaste breedtes voor de kolommen!
    log_table.add_column("I", width=2, justify="center")
    log_table.add_column("ACTIE", width=8, justify="left")
    log_table.add_column("BERICHT", ratio=1) # Neemt rest van ruimte

    # Haal logs op
    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=30)
    display_logs = []
    
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            if len(display_logs) >= 14: break # Pas aan op schermhoogte

    # Voeg toe aan tabel
    for icon, tag, msg, color in display_logs:
        log_table.add_row(
            f"[{color}]{icon}[/]",
            f"[bold {color}]{tag}[/]",
            f"[white]{msg}[/]"
        )

    layout["feed"].update(Panel(
        log_table, 
        title=f"[bold {border_color}]NEURAL STREAM[/]", 
        border_style=border_color,
        box=box.ROUNDED
    ))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=8) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.125)
