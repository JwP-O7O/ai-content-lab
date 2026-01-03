#!/bin/bash
# setup_termux_improvement_system.sh

echo "🚀 Initialiseren van Termux voor Autonomous Improvement System..."

# 1. Update pakketten
pkg update && pkg upgrade -y

# 2. Installeer essentiële dependencies (ARM64 compatibel)
pkg install python nodejs git postgresql build-essential libpq -y

# 3. Setup opslag toegang (bevestig de popup op je telefoon)
termux-setup-storage

# 4. Installeer Python tools die je agents nodig hebben
pip install ruff mypy pip-audit loguru sqlalchemy psycopg2-binary psutil

# 5. Maak de benodigde mappen aan
mkdir -p src/autonomous_agents/{monitoring,analysis,planning,execution,validation,learning}
mkdir -p logs/autonomous_agents
mkdir -p data/improvement_plans

echo "✅ Termux is nu geconfigureerd!"

