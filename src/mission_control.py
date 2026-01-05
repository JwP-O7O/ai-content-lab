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
}

def get_file_tail(filepath, lines=80):
    try:
        if not os.path.exists(filepath): return []
        with open(filepath, 'r') as f:
            return f.readlines()[-lines:]
    except: return []

def get_smooth_color(frame, speed=0.05, offset=0):
    """Vloeiende RGB golf"""
    t = frame * speed + offset
    r = int(math.sin(t) * 127 + 128)
    g = int(math.sin(t + 2.0) * 127 + 128)
    b = int(math.sin(t + 4.0) * 127 + 128)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_scanner_line(frame, width=30, color="#ffffff"):
    """
    Kleine, felle stip met 'glow' trail
    """
    # Positie berekenen
    pos = int((math.sin(frame * 0.2) + 1) / 2 * (width - 1))
    
    # Donkere rail als achtergrond
    chars = [f"[dim grey15]─[/]"] * width
    
    # 1. De Felle Kop (Puntje)
    if 0 <= pos < width: 
        chars[pos] = f"[bold white]●[/]"
    
    # 2. De Glow (Korte trail links en rechts)
    # Direct naast de kop (Fel gekleurd)
    if 0 <= pos-1 < width: chars[pos-1] = f"[bold {color}]•[/]"
    if 0 <= pos+1 < width: chars[pos+1] = f"[bold {color}]•[/]"
    
    # Iets verder weg (Dim gekleurd)
    if 0 <= pos-2 < width: chars[pos-2] = f"[dim {color}]·[/]"
    if 0 <= pos+2 < width: chars[pos+2] = f"[dim {color}]·[/]"
    
    return "".join(chars)

def parse_log_line(line):
    line = line.strip()
    if not line: return None
    
    # FILTER RUIS
    skip = ["Cycle #", "Ruststand", "---", "WAIT", "IDLE", "HERSTART", "Nieuwe functionaliteit", "Geen nieuwe orders"]
    if any(s in line for s in skip): return None

    cfg = {"c": "dim white", "i": "•", "tag": "SYS"}
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line: cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "ImportError" in line: cfg = {"c": "bold red", "i": "🚑", "tag": "FIX"}

    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    
    # --- UPDATE: LANGERE TEKST VOOR WIDESCREEN ---
    # Hier zat de limiet op 40, nu op 85 voor je S21 Ultra
    if len(msg) > 85: msg = msg[:82] + "..."

    return (cfg['i'], cfg['tag'], msg, cfg['c'])

def get_active_agent_info():
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=5)
    if not logs: return "STANDBY"
    last_line = logs[-1].strip()
    
    for key in AGENT_CONFIG:
        if key in last_line:
            return key.replace("Agent", "").upper()
    return "SYSTEM"

def generate_layout(frame):
    layout = Layout()
    
    # Header en Stats in 1 smalle balk, rest is feed
    layout.split_column(
        Layout(name="top_bar", size=3),
        Layout(name="feed", ratio=1)
    )

    main_color = get_smooth_color(frame, speed=0.08)
    
    # --- 1. TOP BAR ---
    scanner = get_scanner_line(frame, width=25, color=main_color)
    active_agent = get_active_agent_info()
    
    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left", ratio=1)
    header_grid.add_column(justify="center", ratio=2)
    header_grid.add_column(justify="right", ratio=1)
    
    header_grid.add_row(
        f"[bold {main_color}]PHOENIX V10[/]",
        scanner,
        f"ACT: [bold white]{active_agent}[/]"
    )
    
    layout["top_bar"].update(Panel(
        header_grid,
        style="on black",
        border_style=main_color,
        box=box.HEAVY_EDGE
    ))

    # --- 2. FEED ---
    log_table = Table(
        show_header=False,
        box=None,
        expand=True, # Dit dwingt de tabel naar de randen
        padding=(0, 1)
    )
    
    # Kolom definities
    log_table.add_column("Icon", width=2, justify="center")
    log_table.add_column("Tag", width=6, justify="left")
    log_table.add_column("Message", ratio=1) # Neemt ALLE overgebleven ruimte in

    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=40)
    display_logs = []
    
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            if len(display_logs) >= 28: break 

    for icon, tag, msg, color in display_logs:
        log_table.add_row(
            f"[{color}]{icon}[/]",
            f"[bold {color}]{tag}[/]",
            f"[white]{msg}[/]"
        )

    layout["feed"].update(Panel(
        log_table,
        title=f"[bold {main_color}]NEURAL STREAM[/]",
        border_style=main_color,
        box=box.ROUNDED
    ))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=12) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.05)
