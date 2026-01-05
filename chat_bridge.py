from flask import Flask, request, jsonify, render_template_string
import json
import os
import time

app = Flask(__name__)
COMMAND_FILE = "data/local_commands.json"
LOG_FILE = "logs/autonomous_agents/agent.log"

# --- DE MODERNE INTERFACE (BOOTSTRAP 5 + CUSTOM CSS) ---
HTML = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PHOENIX OS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #09090b;
            --card-bg: #18181b;
            --accent: #00ff9d; /* Phoenix Neon Green */
            --accent-dim: rgba(0, 255, 157, 0.1);
            --text-main: #e4e4e7;
            --text-dim: #a1a1aa;
        }
        body { background-color: var(--bg-dark); color: var(--text-main); font-family: 'Segoe UI', Roboto, sans-serif; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
        
        /* NAVIGATION */
        .navbar { background-color: rgba(24, 24, 27, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid #333; }
        .navbar-brand { color: var(--accent) !important; font-weight: 800; letter-spacing: 1px; }
        .nav-tabs { border-bottom: none; }
        .nav-link { color: var(--text-dim); border: none !important; font-weight: 600; }
        .nav-link.active { color: var(--accent) !important; background: transparent !important; border-bottom: 2px solid var(--accent) !important; }

        /* CONTENT AREA */
        .tab-content { flex: 1; overflow: hidden; position: relative; }
        .tab-pane { height: 100%; display: flex; flex-direction: column; }

        /* CHAT INTERFACE */
        #chat-container { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .message { max-width: 85%; padding: 10px 15px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; position: relative; animation: fadeIn 0.3s ease; }
        .msg-ai { align-self: flex-start; background-color: var(--card-bg); border-left: 3px solid var(--accent); color: var(--text-main); }
        .msg-user { align-self: flex-end; background-color: var(--accent); color: #000; font-weight: 500; border-bottom-right-radius: 2px; }
        .msg-meta { font-size: 0.7rem; color: var(--text-dim); margin-bottom: 2px; display: block; }
        
        /* INPUT AREA */
        .input-area { padding: 15px; background-color: var(--card-bg); border-top: 1px solid #333; display: flex; gap: 10px; }
        .form-control { background-color: #000; border: 1px solid #333; color: white; border-radius: 25px; padding-left: 20px; }
        .form-control:focus { background-color: #000; color: white; border-color: var(--accent); box-shadow: 0 0 5px var(--accent-dim); }
        .btn-send { background-color: var(--accent); color: black; border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; border: none; }

        /* AGENT GRID */
        .agent-grid { padding: 15px; overflow-y: auto; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .agent-card { background-color: var(--card-bg); border: 1px solid #333; border-radius: 12px; padding: 15px; text-align: center; transition: transform 0.2s; }
        .agent-card:active { transform: scale(0.98); }
        .agent-icon { font-size: 1.8rem; margin-bottom: 10px; display: block; }
        .agent-name { font-weight: 700; color: white; font-size: 0.9rem; margin-bottom: 5px; }
        .agent-desc { font-size: 0.75rem; color: var(--text-dim); margin-bottom: 10px; display: block; }
        .btn-agent { width: 100%; font-size: 0.8rem; border-radius: 8px; font-weight: 600; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <a class="navbar-brand" href="#"><i class="fas fa-microchip"></i> PHOENIX OS</a>
            <ul class="nav nav-tabs ms-auto" id="myTab" role="tablist">
                <li class="nav-item"><button class="nav-link active" id="chat-tab" data-bs-toggle="tab" data-bs-target="#chat-view"><i class="fas fa-comment-alt"></i> CHAT</button></li>
                <li class="nav-item"><button class="nav-link" id="agents-tab" data-bs-toggle="tab" data-bs-target="#agents-view"><i class="fas fa-users-cog"></i> AGENTS</button></li>
            </ul>
        </div>
    </nav>

    <div class="tab-content" id="myTabContent">
        
        <div class="tab-pane fade show active" id="chat-view">
            <div id="chat-container">
                <div class="message msg-ai">
                    <span class="msg-meta">MASTER ORCHESTRATOR</span>
                    Phoenix Core V16 Online. Ik luister.
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="cmdInput" class="form-control" placeholder="Geef opdracht..." autocomplete="off">
                <button class="btn-send" onclick="sendCmd()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>

        <div class="tab-pane fade" id="agents-view">
            <div class="agent-grid">
                
                <div class="agent-card">
                    <span class="agent-icon" style="color: #00e5ff;">🌐</span>
                    <h5 class="agent-name">Web Architect</h5>
                    <span class="agent-desc">Bouwt apps & sites</span>
                    <button class="btn btn-outline-info btn-agent" onclick="quickCmd('WEB: Bouw een moderne landing page')">BOUW IETS</button>
                </div>

                <div class="agent-card">
                    <span class="agent-icon" style="color: #00ff9d;">⚙️</span>
                    <h5 class="agent-name">Feature Dev</h5>
                    <span class="agent-desc">Python backend logic</span>
                    <button class="btn btn-outline-success btn-agent" onclick="quickCmd('SYSTEM: Optimaliseer de huidige code')">OPTIMALISEER</button>
                </div>

                <div class="agent-card">
                    <span class="agent-icon" style="color: #ffcc00;">🌍</span>
                    <h5 class="agent-name">Researcher</h5>
                    <span class="agent-desc">Zoekt kennis online</span>
                    <button class="btn btn-outline-warning btn-agent" onclick="quickCmd('RESEARCH: Zoek trending AI technieken')">ZOEK INFO</button>
                </div>

                <div class="agent-card">
                    <span class="agent-icon" style="color: #ff4757;">🔧</span>
                    <h5 class="agent-name">System Ops</h5>
                    <span class="agent-desc">Onderhoud & Fixes</span>
                    <button class="btn btn-outline-danger btn-agent" onclick="quickCmd('SYSTEM: STATUS REPORT')">CHECK STATUS</button>
                </div>

                <div class="agent-card">
                    <span class="agent-icon" style="color: #d63384;">🎨</span>
                    <h5 class="agent-name">Visionary</h5>
                    <span class="agent-desc">Creatieve Ideeën</span>
                    <button class="btn btn-outline-light btn-agent" onclick="quickCmd('MISSION: Verzin een nieuwe game')">NIEUW IDEE</button>
                </div>

                <div class="agent-card" style="border-color: #ff0000;">
                    <span class="agent-icon">☠️</span>
                    <h5 class="agent-name">EMERGENCY</h5>
                    <span class="agent-desc">Herstart alles</span>
                    <button class="btn btn-danger btn-agent" onclick="quickCmd('SYSTEM: HERSTART')">RESTART</button>
                </div>

            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const chatBox = document.getElementById('chat-container');
        const input = document.getElementById('cmdInput');
        
        // Geluidseffect (optioneel)
        // const beep = new Audio('data:audio/wav;base64,...'); 

        async function sendCmd() {
            const val = input.value.trim();
            if (!val) return;
            postCommand(val);
            input.value = '';
        }

        async function quickCmd(cmd) {
            // Switch naar chat tab om resultaat te zien
            document.querySelector('#chat-tab').click();
            postCommand(cmd);
        }

        async function postCommand(cmd) {
            addMessage(cmd, 'user');
            try {
                await fetch('/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
            } catch(e) {
                addMessage("Verbindingsfout!", 'ai');
            }
        }

        function addMessage(text, type) {
            const div = document.createElement('div');
            div.className = `message msg-${type}`;
            
            let meta = type === 'ai' ? 'PHOENIX AI' : 'COMMANDER';
            div.innerHTML = `<span class="msg-meta">${meta}</span>${text}`;
            
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // Poll Logs (Live Feed)
        let lastLogSize = 0;
        setInterval(async () => {
            try {
                const res = await fetch('/poll?offset=' + lastLogSize);
                const data = await res.json();
                lastLogSize = data.offset;
                
                if (data.lines.length > 0) {
                    data.lines.forEach(line => {
                        if (line.includes("Cycle #") || line.includes("Ruststand")) return;
                        
                        // Iconen mapping
                        let icon = "🤖";
                        if (line.includes("ZOEKT")) icon = "🌍";
                        if (line.includes("BOUWT")) icon = "🌐";
                        if (line.includes("CODET")) icon = "⚙️";
                        if (line.includes("PUSHT")) icon = "📦";
                        if (line.includes("ERROR")) icon = "❌";

                        let cleanMsg = line.split(" - ").pop().trim();
                        addMessage(`${icon} ${cleanMsg}`, 'ai');
                    });
                }
            } catch(e) {}
        }, 2000);

        // Enter toets
        input.addEventListener("keypress", function(event) {
            if (event.key === "Enter") sendCmd();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/send', methods=['POST'])
def send_command():
    data = request.json
    os.makedirs("data", exist_ok=True)
    with open(COMMAND_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({"status": "sent"})

@app.route('/poll')
def poll_logs():
    offset = int(request.args.get('offset', 0))
    if not os.path.exists(LOG_FILE): return jsonify({"lines": [], "offset": 0})
    
    with open(LOG_FILE, 'r') as f:
        f.seek(0, 2)
        size = f.tell()
        if offset > size: offset = 0
        f.seek(offset)
        lines = f.readlines()
        
    return jsonify({"lines": lines, "offset": size})

if __name__ == '__main__':
    print("PHOENIX WEB OS RUNNING ON PORT 5000")
    app.run(host='0.0.0.0', port=5000)
