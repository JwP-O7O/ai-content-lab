from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)
COMMAND_FILE = "data/local_commands.json"
LOG_FILE = "logs/autonomous_agents/agent.log"

# --- HTML TEMPLATE (CYBERPUNK STYLE) ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PHOENIX UPLINK</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        h1 { text-align: center; border-bottom: 1px solid #00ff41; padding-bottom: 10px; margin-top: 0; text-shadow: 0 0 5px #00ff41; font-size: 1.5rem; }
        #chat-history { flex: 1; overflow-y: auto; border: 1px solid #333; padding: 10px; margin-bottom: 10px; background: #0a0a0a; border-radius: 5px; }
        .msg { margin-bottom: 8px; line-height: 1.4; border-bottom: 1px dashed #222; padding-bottom: 4px; }
        .msg.user { color: #fff; text-align: right; }
        .msg.user span { background: #222; padding: 5px 10px; border-radius: 15px 0 15px 15px; display: inline-block; }
        .msg.ai { color: #00ff41; text-align: left; }
        .msg.ai .icon { font-weight: bold; margin-right: 5px; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; background: #111; border: 1px solid #00ff41; color: white; padding: 15px; font-family: inherit; font-size: 16px; border-radius: 5px; outline: none; }
        input:focus { box-shadow: 0 0 10px #00ff41; }
        button { background: #00ff41; color: black; border: none; padding: 15px 25px; font-weight: bold; cursor: pointer; border-radius: 5px; }
        button:active { background: #fff; }
    </style>
</head>
<body>
    <h1>🦅 PHOENIX COMMAND LINK</h1>
    <div id="chat-history">
        <div class="msg ai"><span class="icon">🤖</span> Verbinding met Master Orchestrator gestart...</div>
    </div>
    <div class="input-area">
        <input type="text" id="cmd" placeholder="Geef commando (bijv: WEB: Maak Snake)" autocomplete="off">
        <button onclick="send()">SEND</button>
    </div>

    <script>
        const chat = document.getElementById('chat-history');
        const input = document.getElementById('cmd');

        async function send() {
            const val = input.value.trim();
            if (!val) return;
            
            // Voeg toe aan UI
            addMsg(val, 'user');
            input.value = '';

            // Stuur naar backend
            await fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: val})
            });
        }

        function addMsg(text, type) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            if (type === 'ai') div.innerHTML = text; // Allow HTML for AI
            else div.innerHTML = `<span>${text}</span>`;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        // Poll voor logs
        let lastLogSize = 0;
        setInterval(async () => {
            try {
                const res = await fetch('/poll?offset=' + lastLogSize);
                const data = await res.json();
                lastLogSize = data.offset;
                
                if (data.lines.length > 0) {
                    data.lines.forEach(line => {
                        // Filter ruis
                        if (line.includes("Cycle #") || line.includes("Ruststand")) return;
                        
                        // Formatteer
                        let clean = line.split(" - ").pop().trim();
                        // Kleurtjes en iconen
                        clean = clean.replace("ZOEKT", "🌍 ZOEKT")
                                     .replace("BOUWT", "🌐 BOUWT")
                                     .replace("CODET", "⚙️ CODET")
                                     .replace("ERROR", "❌ ERROR")
                                     .replace("SUCCESS", "✅ SUCCES");
                        
                        addMsg(clean, 'ai');
                    });
                }
            } catch(e) {}
        }, 2000);
        
        // Enter toets support
        input.addEventListener("keypress", function(event) {
            if (event.key === "Enter") send();
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
        f.seek(0, 2) # Ga naar einde
        size = f.tell()
        if offset > size: offset = 0 # Log rotatie reset
        
        f.seek(offset)
        lines = f.readlines()
        
    return jsonify({"lines": lines, "offset": size})

if __name__ == '__main__':
    print("PHOENIX CHAT SERVER RUNNING ON PORT 5000")
    app.run(host='0.0.0.0', port=5000)
