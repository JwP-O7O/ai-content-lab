import time
import os
import re
import math
import json
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich import box

console = Console()

AGENT_CONFIG = {
    "ResearchAgent": {"c": "bright_yellow", "i": "🌍", "tag": "ZOEKT"},
    "WebArchitect": {"c": "bright_cyan", "i": "🌐", "tag": "BOUWT"},
    "FeatureArchitect": {"c": "bright_green", "i": "⚙️", "tag": "CODET"},
    "VisionaryAgent": {"c": "bright_magenta", "i": "🎨", "tag": "ART"},
    "GitHubListener": {"c": "dodger_blue1", "i": "📡", "tag": "LEEST"},
    "GitPublisher": {"c": "white", "i": "📦", "tag": "PUSHT"},
    "SystemOptimizer": {"c": "orange1", "i": "🔧", "tag": "FIXT"},
    "Evolutionary": {"c": "medium_purple1", "i": "🧬", "tag": "DENKT"},
    "StaffingAgent": {"c": "white", "i": "👔", "tag": "HR"},
    "QualityAssurance": {"c": "bright_red", "i": "🛡️", "tag": "TEST"},
    "Master": {"c": "white", "i": "🤖", "tag": "CORE"},
}


def get_file_tail(filepath, lines=150):
    try:
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r") as f:
            return f.readlines()[-lines:]
    except:
        return []


def get_smooth_color(frame, speed=0.05, offset=0):
    t = frame * speed + offset
    r = int(math.sin(t) * 127 + 128)
    g = int(math.sin(t + 2.0) * 127 + 128)
    b = int(math.sin(t + 4.0) * 127 + 128)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_scanner_line(frame, width=30, color="#ffffff"):
    pos = int((math.sin(frame * 0.15) + 1) / 2 * (width - 1))
    chars = ["[dim grey15]─[/]"] * width
    if 0 <= pos < width:
        chars[pos] = "[bold white]●[/]"
    if 0 <= pos - 1 < width:
        chars[pos - 1] = f"[bold {color}]•[/]"
    if 0 <= pos + 1 < width:
        chars[pos + 1] = f"[bold {color}]•[/]"
    return "".join(chars)


def get_current_mission_title():
    try:
        if os.path.exists("data/current_mission.json"):
            with open("data/current_mission.json", "r") as f:
                data = json.load(f)
                title = data.get("title", "NO MISSION")
                # Max lengte afkappen
                return title[:20].upper()
    except:
        pass
    return "FREE ROAM"


def parse_log_line(line):
    line = line.strip()
    if not line:
        return None
    skip = [
        "Cycle #",
        "Ruststand",
        "---",
        "WAIT",
        "IDLE",
        "HERSTART",
        "Nieuwe functionaliteit",
        "Geen nieuwe orders",
        "Error while finding module",
    ]
    if any(s in line for s in skip):
        return None

    cfg = {"c": "dim white", "i": "•", "tag": "SYS"}
    for key, config in AGENT_CONFIG.items():
        if key in line:
            cfg = config
            break

    if "ERROR" in line or "FAIL" in line:
        cfg = {"c": "bold red", "i": "☠️", "tag": "FAIL"}
    if "SUCCESS" in line:
        cfg = {"c": "bold green", "i": "✔", "tag": "OK"}
    if "FILE:" in line:
        cfg = {"c": "bold orange1", "i": "📝", "tag": "FILE"}

    parts = line.split(" - ")
    msg = parts[-1].strip() if len(parts) > 1 else line
    msg = re.sub(r"\[.*?\]", "", msg).strip()
    if len(msg) > 90:
        msg = msg[:87] + "..."
    return (cfg["i"], cfg["tag"], msg, cfg["c"])


def get_changed_files_data():
    logs = get_file_tail("logs/autonomous_agents/agent.log", lines=250)
    files = []
    seen = set()
    for line in reversed(logs):
        if "FILE:" in line or "Code geschreven naar" in line or "App gebouwd" in line:
            parts = line.split(" - ")
            msg = parts[-1].strip()
            raw_file = (
                msg.replace("FILE:", "")
                .replace("Code geschreven naar:", "")
                .replace("App gebouwd/geüpdatet:", "")
                .strip()
            )
            if "|" in raw_file:
                raw_file = raw_file.split("|")[0].strip()

            # Filter init files uit de lijst
            if "__init__" in raw_file:
                continue

            try:
                time_part = line.split(" - ")[0].split(" ")[1].split(",")[0]
            except:
                time_part = "--:--"

            if raw_file not in seen:
                files.append((time_part, raw_file))
                seen.add(raw_file)
            if len(files) >= 5:
                break
    return files


def generate_layout(frame):
    layout = Layout()
    layout.split_column(
        Layout(name="top_bar", size=3),
        Layout(name="evidence", size=7),
        Layout(name="feed"),
    )

    main_color = get_smooth_color(frame, speed=0.08)
    sec_color = get_smooth_color(frame, speed=0.08, offset=2.0)

    # --- TOP BAR ---
    scanner = get_scanner_line(frame, width=20, color=main_color)
    mission = get_current_mission_title()

    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left", ratio=1)
    header_grid.add_column(justify="center", ratio=2)
    header_grid.add_column(justify="right", ratio=1)
    header_grid.add_row(
        f"[bold {main_color}]PHOENIX V15[/]", scanner, f"OP: [bold white]{mission}[/]"
    )
    layout["top_bar"].update(
        Panel(
            header_grid, style="on black", border_style=main_color, box=box.HEAVY_EDGE
        )
    )

    # --- EVIDENCE ---
    files_table = Table(
        show_header=True,
        header_style=f"bold {sec_color}",
        box=None,
        expand=True,
        padding=(0, 1),
    )
    files_table.add_column("TIMESTAMP", style="dim white", width=12)
    files_table.add_column("MODIFIED ASSETS", style="bold white")

    recent_files = get_changed_files_data()
    if not recent_files:
        files_table.add_row("--:--:--", "[dim italic]Wachten op wijzigingen...[/]")
    else:
        for t, f in recent_files:
            files_table.add_row(t, f)

    layout["evidence"].update(
        Panel(
            files_table,
            title=f"[bold {sec_color}]EVIDENCE LOCKER[/]",
            border_style=sec_color,
            box=box.ROUNDED,
        )
    )

    # --- FEED ---
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
            if len(display_logs) >= 20:
                break

    for icon, tag, msg, color in display_logs:
        log_table.add_row(
            f"[{color}]{icon}[/]", f"[bold {color}]{tag}[/]", f"[white]{msg}[/]"
        )

    layout["feed"].update(
        Panel(
            log_table,
            title=f"[bold {main_color}]ACTIVITY STREAM[/]",
            border_style=main_color,
            box=box.ROUNDED,
        )
    )

    return layout


if __name__ == "__main__":
    console.clear()
    frame = 0
    with Live(generate_layout(0), refresh_per_second=4, screen=True) as live:
        while True:
            live.update(generate_layout(frame))
            frame += 1
            time.sleep(0.25)
