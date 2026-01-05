import time
import os
import re
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.text import Text

console = Console()

# 🎨 KLEUREN & ICOON CONFIGURATIE
AGENT_CONFIG = {
    "StaffingAgent":    {"color": "bold white",   "icon": "👔", "act": "HUURT"},
    "QualityAssurance": {"color": "bold red",     "icon": "🛡️", "act": "TEST"},
    "ResearchAgent":    {"color": "bold yellow",  "icon": "🌍", "act": "ZOEKT"},
    "WebArchitect":     {"color": "bold cyan",    "icon": "🌐", "act": "BOUWT"},
    "FeatureArchitect": {"color": "bold green",   "icon": "⚙️", "act": "CODET"},
    "VisionaryAgent":   {"color": "bold magenta", "icon": "🎨", "act": "TEKENT"},
    "GitHubListener":   {"color": "blue",         "icon": "📡", "act": "LEEST"},
    "GitPublisher":     {"color": "dim white",    "icon": "📦", "act": "PUSHT"},
    "SystemOptimizer":  {"color": "orange1",      "icon": "🔧", "act": "FIXT"},
    "Evolutionary":     {"color": "purple",       "icon": "🧬", "act": "DENKT"},
    "ContentWriter":    {"color": "cyan",         "icon": "✍️", "act": "TEXT"},
    "Master":           {"color": "white",        "icon": "🤖", "act": "LEIDT"},
    "ERROR":            {"color": "bold red",     "icon": "❌", "act": "FOUT"},
    "SUCCESS":          {"color": "bold green",   "icon": "✔", "act": "KLAAR"}
}

def clean_log_line(line):
    """Vertaalt log regels naar korte HUD regels"""
    if not line.strip(): return None
    
    cfg = {"color": "white", "icon": "ℹ", "act": "INFO"}
    
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    if "ERROR" in line and cfg["act"] == "INFO": cfg = AGENT_CONFIG["ERROR"]
    if "SUCCESS" in line and cfg["act"] == "INFO": cfg = AGENT_CONFIG["SUCCESS"]

    parts = line.split(' - ')
    message = parts[-1].strip() if len(parts) > 1 else line.strip()
    message = re.sub(r'\[.*?\]', '', message).strip()
    
    # Iets meer tekst ruimte op S21 Ultra
    if len(message) > 55:
        message = message[:52] + "..."

    return f"[{cfg['color']}]{cfg['icon']} {cfg['act']:<6} │ {message}[/]"

def get_hud_logs(n=22): # Meer logs want we hebben verticaal de ruimte!
    log_file = "logs/autonomous_agents/agent.log"
    if not os.path.exists(log_file): return ["[dim]Wachten...[/]"]
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        processed_logs = []
        for line in reversed(lines):
            if "Cycle #" in line or "Ruststand" in line: continue
            clean = clean_log_line(line)
            if clean: processed_logs.insert(0, clean)
            if len(processed_logs) >= n: break
            
        return processed_logs
    except: return ["[bold red]Log file locked...[/]"]

def generate_layout():
    layout = Layout()
    
    # VERTICALE OPBOUW: Header -> Info Balk -> Logs (Rest)
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="top_stats", size=5),
        Layout(name="feed")
    )

    # 1. HEADER
    title = Align.center("[bold white on blue] 🦅 PHOENIX HUD V2.0 [/]")
    layout["header"].update(Panel(title, style="blue"))

    # 2. TOP STATS (Horizontale Grid)
    # Check proces
    running = os.popen("pgrep -f master_orchestrator").read()
    status_icon = "🟢 ONLINE" if running else "🔴 OFFLINE"
    status_style = "bold green" if running else "bold red"

    stats_table = Table(show_header=True, header_style="bold white", expand=True, box=None, padding=(0,1))
    
    # Kolommen centreren voor mooie uitlijning
    stats_table.add_column("SYSTEM", justify="center")
    stats_table.add_column("BRAIN", justify="center")
    stats_table.add_column("WEB", justify="center")
    
    stats_table.add_row(
        f"[{status_style}]{status_icon}[/]", 
        "[cyan]Gemini 2.0[/]", 
        "[yellow]Google[/]"
    )

    layout["top_stats"].update(Panel(stats_table, border_style="blue"))

    # 3. FEED (Vult de rest van het scherm)
    logs = get_hud_logs(n=20) # Aantal regels afgestemd op schermhoogte
    log_content = "\n".join(logs)
    layout["feed"].update(Panel(log_content, title="[bold]LIVE STREAM[/]", border_style="cyan"))

    return layout

if __name__ == "__main__":
    console.clear()
    with Live(generate_layout(), refresh_per_second=2) as live:
        while True:
            live.update(generate_layout())
            time.sleep(0.5)
