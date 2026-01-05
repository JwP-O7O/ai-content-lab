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

# 🎨 KLEUREN & ICOON CONFIGURATIE PER AGENT
AGENT_CONFIG = {
    "ResearchAgent":    {"color": "bold yellow",  "icon": "🌍", "act": "ZOEKT"},
    "WebArchitect":     {"color": "bold cyan",    "icon": "🌐", "act": "BOUWT"},
    "FeatureArchitect": {"color": "bold green",   "icon": "⚙️", "act": "CODET"},
    "VisionaryAgent":   {"color": "bold magenta", "icon": "🎨", "act": "TEKENT"},
    "GitHubListener":   {"color": "blue",         "icon": "📡", "act": "LEEST"},
    "GitPublisher":     {"color": "dim white",    "icon": "📦", "act": "PUSHT"},
    "SystemOptimizer":  {"color": "orange1",      "icon": "🔧", "act": "FIXT"},
    "Evolutionary":     {"color": "purple",       "icon": "🧬", "act": "DENKT"},
    "ContentWriter":    {"color": "cyan",         "icon": "✍️", "act": "SCHRIJFT"},
    "Master":           {"color": "white",        "icon": "🤖", "act": "LEIDT"},
    "ERROR":            {"color": "bold red",     "icon": "❌", "act": "FOUT"},
    "SUCCESS":          {"color": "bold green",   "icon": "✔", "act": "KLAAR"}
}

def clean_log_line(line):
    """Vertaalt ruwe log regels naar strakke HUD output"""
    if not line.strip(): return None
    
    # 1. Bepaal de Agent / Type
    cfg = {"color": "white", "icon": "ℹ", "act": "INFO"} # Default
    
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break
            
    # Check voor algemene errors of successen als er geen agent gevonden is
    if "ERROR" in line and cfg["act"] == "INFO": cfg = AGENT_CONFIG["ERROR"]
    if "SUCCESS" in line and cfg["act"] == "INFO": cfg = AGENT_CONFIG["SUCCESS"]

    # 2. Schoon het bericht op (Verwijder datum, paden, module namen)
    # Splits op het scheidingsteken ' - ' dat Loguru gebruikt
    parts = line.split(' - ')
    if len(parts) > 1:
        message = parts[-1].strip()
    else:
        message = line.strip()

    # Verwijder de [AgentNaam] tag uit het bericht zelf, want die hebben we nu als icoon
    message = re.sub(r'\[.*?\]', '', message).strip()
    
    # Als bericht te lang is, inkorten
    if len(message) > 65:
        message = message[:62] + "..."

    # 3. Formatteer de output regel
    # Vorm: [ICOON] ACTIE | Bericht
    return f"[{cfg['color']}]{cfg['icon']} {cfg['act']:<6} │ {message}[/]"

def get_hud_logs(n=12):
    log_file = "logs/autonomous_agents/agent.log"
    if not os.path.exists(log_file): return ["[dim]Wachten op signaal...[/]"]
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        processed_logs = []
        # We lezen van achter naar voor, maar filteren onnodige regels
        for line in reversed(lines):
            # Filter de 'Cycle' regels en lege regels eruit voor rust
            if "Cycle #" in line or "Ruststand" in line: continue
            
            clean = clean_log_line(line)
            if clean:
                processed_logs.insert(0, clean)
                
            if len(processed_logs) >= n: break
            
        return processed_logs
    except: return ["[bold red]Log file locked...[/]"]

def generate_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main")
    )
    layout["main"].split_row(
        Layout(name="stats", ratio=1),
        Layout(name="feed", ratio=2)
    )

    # 1. HEADER
    title = Align.center("[bold white on blue] 🦅 PHOENIX HUD v1.0 [/] [dim]S21 ULTRA AUTONOMOUS NODE[/]")
    layout["header"].update(Panel(title, style="blue"))

    # 2. STATS (Linker kolom)
    table = Table(show_header=False, expand=True, box=None, padding=(0, 1))
    
    # Check proces
    running = os.popen("pgrep -f master_orchestrator").read()
    status = "[bold green]ONLINE[/]" if running else "[bold red]OFFLINE[/]"
    
    table.add_row("STATUS", status)
    table.add_row("MODEL", "[cyan]Gemini 2.0[/]")
    table.add_row("WEB", "[yellow]DuckDuckGo[/]")
    table.add_row("AUTO", "[magenta]Active[/]")
    table.add_row("", "") # Spacer
    table.add_row("[bold underline]AGENTS", "")
    table.add_row("🌍 Research", "[green]Ready[/]")
    table.add_row("🌐 WebArch", "[green]Ready[/]")
    table.add_row("⚙️ SysArch", "[green]Ready[/]")
    table.add_row("🔧 Optimizer", "[green]Ready[/]")

    layout["stats"].update(Panel(table, title="[bold]SYSTEM[/]", border_style="blue"))

    # 3. FEED (Rechter kolom)
    logs = get_hud_logs()
    log_content = "\n".join(logs)
    layout["feed"].update(Panel(log_content, title="[bold]LIVE AGENT FEED[/]", border_style="cyan"))

    return layout

if __name__ == "__main__":
    console.clear()
    with Live(generate_layout(), refresh_per_second=2) as live:
        while True:
            live.update(generate_layout())
            time.sleep(0.5)
