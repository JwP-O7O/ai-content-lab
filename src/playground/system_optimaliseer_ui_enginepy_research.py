from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from datetime import datetime
from typing import Tuple

# Aangepast kleurenpalet voor "Neon Cyberpunk" look
custom_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "magenta",
        "error": "bold red",
        "success": "bold green",
        "task.web": "bold #00ffff",  # Cyaan
        "task.code": "bold #00ff00",  # Matrix Groen
        "task.art": "bold #ff00ff",  # Neon Roze
        "task.research": "bold #ffff00",  # Fel Geel
        "task.system": "bold #ffaa00",  # Oranje
    }
)

console = Console(theme=custom_theme)


class UIEngine:
    def header(self, title: str) -> None:
        """Prints a header with a centered title."""
        try:
            console.print(f"\n[bold white]╔{'═' * 48}╗[/]")
            console.print(f"[bold white]║ {title.center(48)} ║[/]")
            console.print(f"[bold white]╚{'═' * 48}╝[/]\n")
        except Exception as e:
            console.print(f"[bold red]❌ ERROR in header:[/]\n{e}")

    def log_cycle(self, number: int) -> None:
        """Logs the cycle number with a timestamp."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.rule(
                f"[bold white]🔄 CYCLE #{number} | {timestamp}[/]", style="white"
            )
        except Exception as e:
            console.print(f"[bold red]❌ ERROR in log_cycle:[/]\n{e}")

    def _get_task_style(self, task_type: str) -> Tuple[str, str, str]:
        """Helper function to determine the style, icon, and border style for a task."""
        task_type = task_type.upper()
        if "WEB" in task_type:
            return "task.web", "🌐", "cyan"
        elif "CODE" in task_type:
            return "task.code", "⚙️", "green"
        elif "IMG" in task_type or "ART" in task_type:
            return "task.art", "🎨", "magenta"
        elif "RESEARCH" in task_type:
            return "task.research", "🌍", "yellow"
        elif "SYSTEM" in task_type:
            return "task.system", "🧠", "orange1"
        else:
            return "white", "📝", "white"

    def log_task(self, type: str, title: str, status: str) -> None:
        """Logs a task with a colored panel."""
        try:
            style, icon, border_style = self._get_task_style(type)
            content = f"[{style}]{icon} {title}[/]\n[dim white]{status}[/]"
            panel = Panel(
                content,
                title=f"[bold {border_style}]{type.upper()}[/]",
                border_style=border_style,
                expand=False,
            )
            console.print(panel)
        except Exception as e:
            console.print(f"[bold red]❌ ERROR in log_task:[/]\n{e}")

    def log_success(self, message: str) -> None:
        """Logs a success message."""
        try:
            console.print(f"[bold green]✔ SUCCESS:[/][green] {message}[/]")
        except Exception as e:
            console.print(f"[bold red]❌ ERROR in log_success:[/]\n{e}")

    def log_error(self, message: str) -> None:
        """Logs an error message."""
        try:
            console.print(
                Panel(f"[bold red]❌ ERROR:[/]\n{message}", border_style="red")
            )
        except Exception as e:
            console.print(f"[bold red]❌ ERROR in log_error:[/]\n{e}")

    def log_info(self, message: str) -> None:
        """Logs an informational message."""
        try:
            console.print(f"[dim cyan]ℹ {message}[/]")
        except Exception as e:
            console.print(f"[bold red]❌ ERROR in log_info:[/]\n{e}")
