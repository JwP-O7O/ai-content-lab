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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_file_tail(filepath, lines=100):
    try:
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r') as f:
            return f.readlines()[-lines:]
    except Exception as e:
        logging.error(f"Error reading file tail for {filepath}: {e}")
        return []

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
    skip = ["Cycle #", "Ruststand", "---", "WAIT", "IDLE", "HERSTART", "Nieuwe functionaliteit", "Geen nieuwe orders"]
    if any(s in line for s in skip): return None

    cfg = {"c": "dim white", "i": "•", "tag": "SYS"}
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break

    if "ERROR" in line or "FAIL" in line: cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line: cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "FILE:" in line: cfg = {"c": "bold orange1", "i": "📝", "tag": "FILE"} # Speciaal voor files

    parts = line.split(' - ')
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    return (cfg['i'], cfg['tag'], msg, cfg['c'])

def get_changed_files_data():
    """Zoekt specifiek naar bewijs van verandering in de logs"""
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=200)
    files = []
    regex = r"FILE: ([\w\/\.\-]+)(?: \(commit: ([0-9a-f]+)\))?" # Verbeterde regex voor files
    for line in logs:
        try:
            match = re.search(regex, line)
            if match:
                filename = match.group(1)
                commit_hash = match.group(2) if match.group(2) else None
                files.append({"filename": filename, "commit_hash": commit_hash})
        except Exception as e:
            logging.error(f"Error processing log line: {line}. Error: {e}")
            continue
    return files


def generate_layout(frame):
    layout = Layout()
    layout.split_column(
        Layout(name="top_bar", size=3),
        Layout(name="main_body") # Split body
    )
    
    layout["main_body"].split_row(
        Layout(name="feed", ratio=3),  # Logs links
        Layout(name="files", ratio=2)  # Bewijs rechts
    )

    main_color = get_smooth_color(frame, speed=0.08)
    
    # --- 1. TOP BAR ---
    scanner = get_scanner_line(frame, width=20, color=main_color)
    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left", ratio=1)
    header_grid.add_column(justify="center", ratio=2)
    header_grid.add_column(justify="right", ratio=1)
    header_grid.add_row(f"[bold {main_color}]PHOENIX V13 TRUTH[/]", scanner, f"ACT: [bold white]WATCHING[/]")
    layout["top_bar"].update(Panel(header_grid, style="on black", border_style=main_color, box=box.HEAVY_EDGE))

    # --- 2. FEED (Links) ---
    log_table = Table(show_header=False, box=None, expand=True, padding=(0, 1))
    log_table.add_column("I", width=2)
    log_table.add_column("Tag", width=6)
    log_table.add_column("Msg", ratio=1)

    raw_logs = get_file_tail("logs/autonomous_agents/agent.log", lines=50)
    display_logs = []
    for line in reversed(raw_logs):
        parsed = parse_log_line(line)
        if parsed:
            display_logs.append(parsed)
            if len(display_logs) >= 25: break 

    for icon, tag, msg, color in display_logs:
        # Als het een bestands-log is, highlighten we hem
        style = f"bold {main_color}" if tag == "FILE" else "white"
        log_table.add_row(f"[{color}]{icon}[/]", f"[bold {color}]{tag}[/]", f"[{style}]{msg}[/]")

    layout["feed"].update(Panel(log_table, title=f"[bold {main_color}]ACTIVITY LOG[/]", border_style=main_color, box=box.ROUNDED))

    # --- 3. EVIDENCE BOARD (Rechts) ---
    files_table = Table(show_header=True, header_style=f"bold {main_color}", box=None, expand=True)
    files_table.add_column("Filename", style="bold white")
    files_table.add_column("Commit Hash", style="dim white")

    recent_files = get_changed_files_data()
    if not recent_files:
        files_table.add_row("[dim]Geen wijzigingen...[/]", "")
    else:
        for file_info in recent_files:
            filename = file_info["filename"]
            commit_hash = file_info["commit_hash"]
            files_table.add_row(filename, commit_hash or "")

    layout["files"].update(Panel(files_table, title=f"[bold {main_color}]EVIDENCE LOCKER[/]", border_style=main_color, box=box.ROUNDED))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    try:
        with Live(generate_layout(0), refresh_per_second=4, screen=True) as live:
            while True:
                live.update(generate_layout(frame))
                frame += 1
                time.sleep(0.25)
    except KeyboardInterrupt:
        console.print("Interrupted by user. Exiting...")
    except Exception as e:
        console.print_exception()
        logging.error(f"An unexpected error occurred: {e}")