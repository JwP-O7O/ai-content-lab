import time
import os
import re
import random
import math
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
    "ResearchAgent":    {"color": "bold yellow",  "icon": "🌍", "act": "ZOEKT"},
    "WebArchitect":     {"color": "bold cyan",    "icon": "🌐", "act": "BOUWT"},
    "FeatureArchitect": {"color": "bold green",   "icon": "⚙️", "act": "CODET"},
    "VisionaryAgent":   {"color": "bold magenta", "icon": "🎨", "act": "PAINT"},
    "GitHubListener":   {"color": "blue",         "icon": "📡", "act": "SCAN"},
    "GitPublisher":     {"color": "dim white",    "icon": "📦", "act": "PUSH"},
    "SystemOptimizer":  {"color": "orange1",      "icon": "🔧", "act": "OPT"},
    "Evolutionary":     {"color": "purple",       "icon": "🧬", "act": "EVO"},
    "StaffingAgent":    {"color": "white",        "icon": "👔", "act": "HR"},
    "QualityAssurance": {"color": "bold red",     "icon": "🛡️", "act": "QA"},
    "Master":           {"color": "white",        "icon": "🤖", "act": "CORE"},
    "ERROR":            {"color": "bold red",     "icon": "☠️", "act": "FAIL"},
    "SUCCESS":          {"color": "bold green",   "icon": "✔", "act": "OK"}
}

# Animatie karakters
SPINNERS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
WAVE_CHARS = [" ", "▂", "▃", "▅", "▆", "▇", "▆", "▅", "▃", "▂"]

def get_matrix_stream(lines=3):
    """Genereert willekeurige hex data die eruit ziet als encryptie"""
    stream = ""
    chars = "0123456789ABCDEF"
    for _ in range(lines):
        # Maak willekeurige groene hex codes
        line = "".join([random.choice(chars) for _ in range(40)])
        stream += f"[dim green]{line}[/]\n"
    return stream.strip()

def get_wave_animation(frame):
    """Maakt een bewegende golfbeweging"""
    # Gebruik sinus voor een vloeiende beweging
    pos = int((math.sin(frame * 0.5) + 1) * 4) # Waarde tussen 0 en 8
    # Maak een balkje
    bar = ""
    for i in range(12):
        offset = (i + frame) % len(WAVE_CHARS)
        bar += f"[cyan]{WAVE_CHARS[offset]}[/]"
    return bar

def clean_log_line(line):
    if not line.strip(): return None
    cfg = {"color": "white", "icon": "ℹ", "act": "INFO"}
    
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line: cfg = AGENT_CONFIG["ERROR"]
    if "SUCCESS" in line: cfg = AGENT_CONFIG["SUCCESS"]

    parts = line.split(' - ')
    message = parts[-1].strip() if len(parts) > 1 else line.strip()
    message = re.sub(r'\[.*?\]', '', message).strip()
    if len(message) > 45: message = message[:42] + "..."

    return f"[{cfg['color']}]{cfg['icon']} {cfg['act']:<4} │ {message}[/]"

def get_hud_logs(n=15):
    log_file = "logs/autonomous_agents/agent.log"
    if not os.path.exists(log_file): return ["[dim]Initialiseren...[/]"]
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        processed = []
        for line in reversed(lines):
            if "Cycle #" in line or "Ruststand" in line: continue
            clean = clean_log_line(line)
            if clean: processed.insert(0, clean)
            if len(processed) >= n: break
        return processed
    except: return ["[red]Logs locked[/]"]

def generate_layout(frame):
    layout = Layout()
    
    # INDELING: Header -> Matrix/Stats -> Logs
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="dashboard", size=7),
        Layout(name="feed")
    )

    # 1. HEADER (Met knipperende cursor)
    blink = "█" if frame % 2 == 0 else " "
    title = f"[bold white on blue] 🦅 PHOENIX CORE V3.0 {blink} [/]"
    layout["header"].update(Panel(Align.center(title), style="blue"))

    # 2. DASHBOARD (Split in Links: Stats, Rechts: Matrix)
    layout["dashboard"].split_row(
        Layout(name="stats", ratio=1),
        Layout(name="matrix", ratio=1)
    )

    # --- Linker Paneel: Stats ---
    running = os.popen("pgrep -f master_orchestrator").read()
    
    # Pulse Effect voor status
    pulse_icon = "🟢" if frame % 2 == 0 else "⚪"
    status_text = f"{pulse_icon} [bold green]ONLINE[/]" if running else "🔴 [bold red]OFFLINE[/]"
    
    # Spinner Animatie
    spin_char = SPINNERS[frame % len(SPINNERS)]
    
    stats_table = Table(show_header=False, box=None, padding=(0,1))
    stats_table.add_row("SYS", status_text)
    stats_table.add_row("CPU", f"[blue]{spin_char}[/] Processing")
    stats_table.add_row("NET", get_wave_animation(frame))
    stats_table.add_row("AI", "[magenta]Gemini 2.0[/]")

    layout["stats"].update(Panel(stats_table, title="[bold]METRICS[/]", border_style="green"))

    # --- Rechter Paneel: Matrix Stream ---
    matrix_content = get_matrix_stream(lines=5)
    layout["matrix"].update(Panel(matrix_content, title="[bold]DATA STREAM[/]", border_style="green"))

    # 3. LOG FEED
    logs = get_hud_logs(n=18)
    layout["feed"].update(Panel("\n".join(logs), title="[bold]NEURAL FEED[/]", border_style="cyan"))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=4) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.25) # Sneller verversen voor animatie
