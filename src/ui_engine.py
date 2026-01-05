from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from datetime import datetime

# Aangepast kleurenpalet voor "Neon Cyberpunk" look
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "bold green",
    "task.web": "bold #00ffff",    # Cyaan
    "task.code": "bold #00ff00",   # Matrix Groen
    "task.art": "bold #ff00ff",    # Neon Roze
    "task.research": "bold #ffff00", # Fel Geel
    "task.system": "bold #ffaa00", # Oranje
})

console = Console(theme=custom_theme)

class UIEngine:
    def header(self, title):
        console.print(f"\n[bold white]╔══════════════════════════════════════════════════╗[/]")
        console.print(f"[bold white]║ {title.center(48)} ║[/]")
        console.print(f"[bold white]╚══════════════════════════════════════════════════╝[/]\n")

    def log_cycle(self, number):
        timestamp = datetime.now().strftime("%H:%M:%S")
        console.rule(f"[bold white]🔄 CYCLE #{number} | {timestamp}[/]", style="white")

    def log_task(self, type, title, status):
        """Maakt een mooi gekleurd blok voor een taak"""
        type = type.upper()
        
        # Bepaal kleur en icoon op basis van type
        if "WEB" in type:
            style = "task.web"
            icon = "🌐"
            border_style = "cyan"
        elif "CODE" in type:
            style = "task.code"
            icon = "⚙️"
            border_style = "green"
        elif "IMG" in type or "ART" in type:
            style = "task.art"
            icon = "🎨"
            border_style = "magenta"
        elif "RESEARCH" in type:
            style = "task.research"
            icon = "🌍"
            border_style = "yellow"
        elif "SYSTEM" in type:
            style = "task.system"
            icon = "🧠"
            border_style = "orange1"
        else:
            style = "white"
            icon = "📝"
            border_style = "white"

        # Maak het paneel
        content = f"[{style}]{icon} {title}[/]\n[dim white]{status}[/]"
        panel = Panel(
            content,
            title=f"[bold {border_style}]{type}[/]",
            border_style=border_style,
            expand=False
        )
        console.print(panel)

    def log_success(self, message):
        console.print(f"[bold green]✔ SUCCESS:[/][green] {message}[/]")

    def log_error(self, message):
        console.print(Panel(f"[bold red]❌ ERROR:[/]\n{message}", border_style="red"))

    def log_info(self, message):
        console.print(f"[dim cyan]ℹ {message}[/]")
