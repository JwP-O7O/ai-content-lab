import time
import os
import re
import math
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
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

def get_file_tail(filepath, lines=150):
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
    pos = int((math.sin(frame * 0.15) + 1) / 2 * (width - 1))
    chars = [f"[dim grey15]─[/]"] * width
    if 0 <= pos < width: chars[pos] = f"[bold white]●[/]"
    if 0 <= pos-1 < width: chars[pos-1] = f"[bold {color}]•[/]"
    if 0 <= pos+1 < width: chars[pos+1] = f"[bold {color}]•[/]"
    return "".join(chars)

def parse_log_line(line):
    line = line.strip()
    if not line: return None
    skip = ["Cycle #", "Ruststand", "---", "WAIT", "IDLE", "HERSTART", "Nieuwe functionaliteit", "Geen nieuwe orders"]
    if any(s in line for s in skip): return None

    cfg = {"c": "dim white", "i": "•", "tag": "SYS"}
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line or "FAIL" in line: cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "FILE:" in line: cfg = {"c": "bold orange1", "i": "📝", "tag": "FILE"}

    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    if len(msg) > 90: msg = msg[:87] + "..."
    return (cfg['i'], cfg['tag'], msg, cfg['c'])

def get_changed_files_data():
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=250)
    files = []
    seen = set() # Voorkom dubbele entries
    
    for line in reversed(logs):
        if "FILE:" in line or "Code geschreven naar" in line or "App gebouwd" in line:
            parts = line.split(' - ')
            msg = parts[-1].strip()
            
            # Extract filename
            raw_file = msg.replace("FILE:", "").replace("Code geschreven naar:", "").replace("App gebouwd/geüpdatet:", "").strip()
            if "|" in raw_file: raw_file = raw_file.split("|")[0].strip()
            
            # Extract time
            try: time_part = line.split(" - ")[0].split(" ")[1].split(",")[0]
            except: time_part = "--:--"

            if raw_file not in seen:
                files.append((time_part, raw_file))
                seen.add(raw_file)
            
            if len(files) >= 5: break # Top 5 files
            
    return files

def generate_layout(frame):
    layout = Layout()
    
    # INDELING:
    # 1. Top Bar (Header) - 3 regels
    # 2. Evidence Locker (Top Focus) - 7 regels (Vast formaat voor stabiliteit)
    # 3. Feed (De rest)
    layout.split_column(
        Layout(name="top_bar", size=3),
        Layout(name="evidence", size=7),
        Layout(name="feed")
    )

    main_color = get_smooth_color(frame, speed=0.08)
    sec_color = get_smooth_color(frame, speed=0.08, offset=2.0)
    
    # --- 1. TOP BAR ---
    scanner = get_scanner_line(frame, width=25, color=main_color)
    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left", ratio=1)
    header_grid.add_column(justify="center", ratio=2)
    header_grid.add_column(justify="right", ratio=1)
    header_grid.add_row(f"[bold {main_color}]PHOENIX V14[/]", scanner, f"MODE: [bold white]WATCHDOG[/]")
    layout["top_bar"].update(Panel(header_grid, style="on black", border_style=main_color, box=box.HEAVY_EDGE))

    # --- 2. EVIDENCE LOCKER (BOVENAAN) ---
    files_table = Table(
        show_header=True, 
        header_style=f"bold {sec_color}", 
        box=None, 
        expand=True,
        padding=(0,1)
    )
    files_table.add_column("TIMESTAMP", style="dim white", width=12)
    files_table.add_column("MODIFIED ASSETS", style="bold white")

    recent_files = get_changed_files_data()
    if not recent_files:
        files_table.add_row("--:--:--", "[dim italic]Wachten op wijzigingen...[/]")
    else:
        for t, f in recent_files:
            # Highlight mapnamen voor leesbaarheid
            f_styled = f.replace("/", f"[dim {main_color}]/[/]")
            files_table.add_row(t, f_styled)

    # We gebruiken de secundaire kleur voor dit paneel om het te onderscheiden
    layout["evidence"].update(Panel(
        files_table, 
        title=f"[bold {sec_color}]EVIDENCE LOCKER[/]", 
        border_style=sec_color, 
        box=box.ROUNDED
    ))

    # --- 3. FEED (ONDER) ---
    log_table = Table(show_header=False, box=None, expand=True, padding=(0, 1))
    log_table.add_column("I", width=2, justify="center")
    log_table.add_column("Tag", width=6)
    log_table.add_column("Msg", ratio=1)

    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=40)
    display_logs = []
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            if len(display_logs) >= 20: break 

    for icon, tag, msg, color in display_logs:
        log_table.add_row(f"[{color}]{icon}[/]", f"[bold {color}]{tag}[/]", f"[white]{msg}[/]")

    layout["feed"].update(Panel(
        log_table, 
        title=f"[bold {main_color}]ACTIVITY STREAM[/]", 
        border_style=main_color, 
        box=box.ROUNDED
    ))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=4, screen=True) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.25)
