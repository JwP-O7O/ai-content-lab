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
    t = frame * speed + offset
    r = int(math.sin(t) * 127 + 128)
    g = int(math.sin(t + 2.0) * 127 + 128)
    b = int(math.sin(t + 4.0) * 127 + 128)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_scanner_line(frame, width=30, color="#ffffff"):
    pos = int((math.sin(frame * 0.2) + 1) / 2 * (width - 1))
    chars = [f"[dim grey15]─[/]"] * width
    
    if 0 <= pos < width: chars[pos] = f"[bold white]●[/]"
    if 0 <= pos-1 < width: chars[pos-1] = f"[bold {color}]•[/]"
    if 0 <= pos+1 < width: chars[pos+1] = f"[bold {color}]•[/]"
    
    return "".join(chars)

def parse_log_line(line):
    line = line.strip()
    if not line: return None
    
    # --- SMART FILTER: WEG MET DE ROMMEL ---
    # We verwijderen regels die alleen maar lijntjes bevatten
    # Dit fixt jouw 'System' border probleem
    bad_chars = ["╭", "╰", "──", "│", "Cycle #", "Ruststand", "WAIT", "IDLE"]
    if any(x in line for x in bad_chars): return None

    cfg = {"c": "dim white", "i": "•", "tag": "SYS"}
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line or "FAIL" in line: cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "ImportError" in line: cfg = {"c": "bold red", "i": "🚑", "tag": "FIX"}

    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    
    # Widescreen lengte
    if len(msg) > 90: msg = msg[:87] + "..."

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
    layout.split_column(
        Layout(name="top_bar", size=3),
        Layout(name="feed", ratio=1)
    )

    main_color = get_smooth_color(frame, speed=0.08)
    
    # --- TOP BAR ---
    scanner = get_scanner_line(frame, width=25, color=main_color)
    active_agent = get_active_agent_info()
    
    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left", ratio=1)
    header_grid.add_column(justify="center", ratio=2)
    header_grid.add_column(justify="right", ratio=1)
    
    header_grid.add_row(
        f"[bold {main_color}]PHOENIX V12[/]",
        scanner,
        f"ACT: [bold white]{active_agent}[/]"
    )
    
    layout["top_bar"].update(Panel(
        header_grid,
        style="on black",
        border_style=main_color,
        box=box.HEAVY_EDGE
    ))

    # --- FEED ---
    log_table = Table(
        show_header=False,
        box=None,
        expand=True,
        padding=(0, 1)
    )
    
    log_table.add_column("Icon", width=2, justify="center")
    log_table.add_column("Tag", width=6, justify="left")
    log_table.add_column("Message", ratio=1)

    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=50)
    display_logs = []
    
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            # Aantal regels afgestemd op scherm
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
    # screen=True voorkomt knipperen!
    with Live(generate_layout(0), refresh_per_second=4, screen=True) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.25)
