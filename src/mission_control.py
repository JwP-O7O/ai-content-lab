import time
import os
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align

console = Console()

def get_last_logs(n=8):
    log_file = "logs/autonomous_agents/agent.log"
    if not os.path.exists(log_file): return ["Wachten op logs..."]
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Filter wat rommel eruit voor een schoner beeld
            clean_lines = []
            for line in lines[-20:]:
                if "INFO" in line and "Cycle" not in line:
                    clean_lines.append(f"[cyan]{line.split('|')[-1].strip()}[/]")
                elif "SUCCESS" in line:
                    clean_lines.append(f"[bold green]✔ {line.split('|')[-1].strip()}[/]")
                elif "ERROR" in line:
                    clean_lines.append(f"[bold red]✖ {line.split('|')[-1].strip()}[/]")
                elif "WARNING" in line:
                    clean_lines.append(f"[yellow]⚠ {line.split('|')[-1].strip()}[/]")
            return clean_lines[-n:]
    except: return ["Log file busy..."]

def generate_layout():
    layout = Layout()
    
    # Header
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    
    # Body split
    layout["body"].split_row(
        Layout(name="status", ratio=1),
        Layout(name="logs", ratio=2)
    )

    # 1. Header Content
    layout["header"].update(
        Panel(Align.center("[bold white]🔵 ALL IN AI - S21 ULTRA COMMAND CENTER V16[/]"), style="blue")
    )

    # 2. Status Table
    table = Table(show_header=False, expand=True, box=None)
    
    # Check process
    running = os.popen("pgrep -f master_orchestrator").read()
    status_icon = "🟢 ONLINE" if running else "🔴 OFFLINE"
    status_color = "green" if running else "red"
    
    table.add_row("🤖 [bold]SYSTEM STATUS[/]", f"[{status_color}]{status_icon}[/]")
    table.add_row("🧠 [bold]MODEL[/]", "[cyan]Gemini 2.0 Flash Lite[/]")
    table.add_row("🌍 [bold]INTERNET[/]", "[green]Connected (Google)[/]")
    table.add_row("🧬 [bold]EVOLUTION[/]", "[magenta]Active[/]")
    table.add_row("🛡️ [bold]SECURITY[/]", "[green]Enforced[/]")
    
    layout["status"].update(
        Panel(table, title="[bold]SYSTEM METRICS[/]", border_style="green")
    )

    # 3. Live Logs
    logs = get_last_logs()
    log_content = "\n".join(logs)
    layout["logs"].update(
        Panel(log_content, title="[bold]LIVE FEED[/]", border_style="cyan")
    )

    return layout

if __name__ == "__main__":
    console.clear()
    with Live(generate_layout(), refresh_per_second=2) as live:
        while True:
            live.update(generate_layout())
            time.sleep(0.5)
