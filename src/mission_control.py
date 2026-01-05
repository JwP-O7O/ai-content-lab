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

console = Console()

# --- CONFIGURATIE ---
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

def get_smooth_rainbow_color(frame, speed=0.1, offset=0):
    """Genereert een vloeiende RGB hex code (Rainbow Wave)"""
    # Sinus golf voor R, G en B met faseverschuiving
    t = frame * speed + offset
    r = int(math.sin(t) * 127 + 128)
    g = int(math.sin(t + 2) * 127 + 128)
    b = int(math.sin(t + 4) * 127 + 128)
    return f"#{r:02x}{g:02x}{b:02x}"

def parse_log_line(line):
    line = line.strip()
    if not line: return None
    
    # Filter Ruis
    skip_terms = ["Cycle #", "Ruststand", "---", "WAIT", "IDLE", "HERSTART", "Nieuwe functionaliteit"]
    if any(x in line for x in skip_terms): return None

    # Config Bepalen
    cfg = AGENT_CONFIG["IDLE"]
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
    
    if "ERROR" in line: cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "WARNING" in line: cfg = {"c": "yellow", "i": "⚠", "tag": "WARN"}

    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    if len(msg) > 35: msg = msg[:32] + "..."

    return (cfg['i'], cfg['tag'], msg, cfg['c'])

def get_scanner_bar(frame, width=40, color="cyan"):
    """De Cylon Scanner"""
    pos = int((math.sin(frame * 0.2) + 1) / 2 * (width - 1))
    chars = [f"[dim {color}]─[/]"] * width
    if 0 <= pos < width: chars[pos] = "[bold white]◆[/]"
    if 0 <= pos-1 < width: chars[pos-1] = f"[bold {color}]━[/]"
    if 0 <= pos+1 < width: chars[pos+1] = f"[bold {color}]━[/]"
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
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="stats", size=3),
        Layout(name="feed")
    )

    # Bereken vloeiende kleuren (Main en Secondary)
    # Main loopt iets voor op Secondary voor een golvend effect
    color_main = get_smooth_rainbow_color(frame, speed=0.15, offset=0)
    color_sec = get_smooth_rainbow_color(frame, speed=0.15, offset=1.0) 

    # --- 1. HEADER ---
    scanner = get_scanner_bar(frame, width=30, color=color_main)
    # De titel zelf krijgt ook de vloeiende kleur
    title_text = f"\n[bold white]PHOENIX[/] [dim]OS[/] [bold {color_main}]V8.0[/]\n{scanner}"
    
    layout["header"].update(Panel(
        Align.center(title_text), 
        border_style=color_main, # De rand verandert mee
        box=box.HEAVY_EDGE
    ))

    # --- 2. STATS ---
    agent = get_active_agent_info()
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    
    blink = "█" if frame % 4 < 2 else " "
    
    grid.add_row(
        f"[bold {color_sec}]TASK[/]",
        f"[bold white]{agent}[/]",
        f"[dim {color_sec}]PROC {blink}[/]"
    )
    
    layout["stats"].update(Panel(grid, border_style=color_sec, box=box.ROUNDED))

    # --- 3. FEED ---
    log_table = Table(
        show_header=True, 
        header_style=f"bold {color_main}", 
        box=None, 
        expand=True, 
        padding=(0, 1),
        collapse_padding=True
    )
    
    log_table.add_column("I", width=2, justify="center")
    log_table.add_column("ACTIE", width=8, justify="left")
    log_table.add_column("BERICHT", ratio=1)

    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=30)
    display_logs = []
    
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            if len(display_logs) >= 14: break

    for icon, tag, msg, color in display_logs:
        log_table.add_row(
            f"[{color}]{icon}[/]",
            f"[bold {color}]{tag}[/]",
            f"[white]{msg}[/]"
        )

    layout["feed"].update(Panel(
        log_table, 
        title=f"[bold {color_main}]NEURAL STREAM[/]", 
        border_style=color_main,
        box=box.ROUNDED
    ))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    # Iets snellere refresh rate voor vloeiende animaties
    with Live(generate_layout(0), refresh_per_second=10) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.1)
