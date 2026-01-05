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
from rich.style import Style

console = Console()

# --- CONFIGURATIE ---
AGENT_CONFIG = {
    "ResearchAgent":    {"c": "yellow",   "i": "🌍", "a": "ZOEKT"},
    "WebArchitect":     {"c": "cyan",     "i": "🌐", "a": "BOUWT"},
    "FeatureArchitect": {"c": "green",    "i": "⚙️", "a": "CODET"},
    "VisionaryAgent":   {"c": "magenta",  "i": "🎨", "a": "PAINT"},
    "GitHubListener":   {"c": "blue",     "i": "📡", "a": "SCAN"},
    "GitPublisher":     {"c": "white",    "i": "📦", "a": "PUSH"},
    "SystemOptimizer":  {"c": "orange1",  "i": "🔧", "a": "OPT"},
    "Evolutionary":     {"c": "purple",   "i": "🧬", "a": "EVO"},
    "StaffingAgent":    {"c": "bright_white", "i": "👔", "a": "HR"},
    "QualityAssurance": {"c": "red",      "i": "🛡️", "a": "QA"},
    "Master":           {"c": "white",    "i": "🤖", "a": "CORE"},
    "ERROR":            {"c": "bold red", "i": "☠️", "a": "FAIL"},
    "SUCCESS":          {"c": "bold green","i": "✔", "a": "OK"}
}

def get_scanner_bar(frame, width=30):
    """
    Simuleert een gloeiende 'Cylon' scanner lijn.
    Effect: [dim] [bright] [WHITE] [bright] [dim]
    """
    # 1. Bereken positie met sinusgolf voor soepele beweging
    # We normaliseren sinus (-1 tot 1) naar (0 tot width)
    pos = (math.sin(frame * 0.3) + 1) / 2 * (width - 1)
    pos = int(pos)
    
    # 2. De basis is een lege lijn
    chars = ["━"] * width
    
    # 3. Teken de 'gloed' (De kern is wit, eromheen cyaan/blauw)
    if 0 <= pos < width:
        chars[pos] = "[bold white]█[/]" # De Hete Kern
    
    # De 'halo' eromheen (links en rechts)
    if 0 <= pos - 1 < width: chars[pos - 1] = "[bold cyan]▓[/]"
    if 0 <= pos + 1 < width: chars[pos + 1] = "[bold cyan]▓[/]"
    
    # De fade-out (nog verder weg)
    if 0 <= pos - 2 < width: chars[pos - 2] = "[dim cyan]▒[/]"
    if 0 <= pos + 2 < width: chars[pos + 2] = "[dim cyan]▒[/]"

    return "".join(chars)

def get_rgb_title(frame):
    """Laat de titel langzaam van kleur veranderen"""
    colors = ["blue", "cyan", "green", "yellow", "magenta", "red"]
    # Kies kleur op basis van tijd, langzaam roterend
    color = colors[int(frame * 0.1) % len(colors)]
    return f"[bold white on {color}] 🦅 PHOENIX CORE V4.0 [/]"

def clean_log_line(line):
    if not line.strip(): return None
    cfg = {"c": "white", "i": "ℹ", "a": "INFO"}
    
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line: cfg = AGENT_CONFIG["ERROR"]
    if "SUCCESS" in line: cfg = AGENT_CONFIG["SUCCESS"]

    parts = line.split(' - ')
    message = parts[-1].strip() if len(parts) > 1 else line.strip()
    message = re.sub(r'\[.*?\]', '', message).strip()
    if len(message) > 40: message = message[:37] + "..."

    return f"[{cfg['c']}]{cfg['i']} {cfg['a']:<5}│ {message}[/]"

def get_hud_logs(n=12):
    log_file = "logs/autonomous_agents/agent.log"
    if not os.path.exists(log_file): return ["[dim]Booting systems...[/]"]
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
    except: return ["[red]Log access denied[/]"]

def generate_layout(frame):
    layout = Layout()
    
    layout.split_column(
        Layout(name="top_bar", size=3),
        Layout(name="scanner", size=3), # <--- NIEUW: DE SCANNER
        Layout(name="main_body")
    )

    # 1. RGB Header
    layout["top_bar"].update(Panel(Align.center(get_rgb_title(frame)), style="black"))

    # 2. The Glowing Scanner
    scan_line = get_scanner_bar(frame, width=40) # Pas breedte aan op S21 scherm
    # We zetten hem in een paneel zonder rand voor een 'zwevend' effect
    layout["scanner"].update(Align.center(f"[bold blue]├──[/]{scan_line}[bold blue]──┤[/]"))

    # 3. Main Body (Stats + Logs)
    layout["main_body"].split_row(
        Layout(name="stats", ratio=1),
        Layout(name="logs", ratio=2)
    )

    # Stats
    running = os.popen("pgrep -f master_orchestrator").read()
    status_icon = "🟢" if running else "🔴"
    status_txt = "[green]ACTIVE[/]" if running else "[red]HALTED[/]"
    
    # Een bewegend 'blokje' om CPU load te simuleren
    load_bar = "█" * (int(math.sin(frame*0.5)*3) + 4)
    
    table = Table(box=None, show_header=False, padding=(0,1))
    table.add_row("STATUS", f"{status_icon} {status_txt}")
    table.add_row("CORE", f"[cyan]{load_bar}[/]")
    table.add_row("BRAIN", "[magenta]Gemini 2.0[/]")
    table.add_row("WEB", "[yellow]Online[/]")
    
    layout["stats"].update(Panel(table, title="[bold]SYS[/]", border_style="blue"))

    # Logs
    logs = get_hud_logs(n=16)
    layout["logs"].update(Panel("\n".join(logs), title="[bold]NEURAL FEED[/]", border_style="cyan"))

    return layout

if __name__ == "__main__":
    console.clear()
    frame = 0
    # Refresh rate op 10fps voor soepele animatie
    with Live(generate_layout(0), refresh_per_second=10) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.1)
