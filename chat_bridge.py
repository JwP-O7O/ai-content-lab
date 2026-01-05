from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)
COMMAND_FILE = "data/local_commands.json"
LOG_FILE = "logs/autonomous_agents/agent.log"
LAST_POS = 0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_command():
    data = request.json
    print(f"COMMANDO ONTVANGEN: {data}") # Je ziet dit in je terminal
    os.makedirs("data", exist_ok=True)
    with open(COMMAND_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({"status": "sent"})

@app.route('/poll')
def poll_logs():
    global LAST_POS
    if not os.path.exists(LOG_FILE): return jsonify({"lines": []})
    
    lines = []
    with open(LOG_FILE, 'r') as f:
        f.seek(0, 2)
        current_pos = f.tell()
        if LAST_POS > current_pos: LAST_POS = 0
        
        if current_pos > LAST_POS:
            f.seek(LAST_POS)
            lines = f.readlines()
            LAST_POS = current_pos
            
    return jsonify({"lines": lines})

if __name__ == '__main__':
    print("PHOENIX WEB SERVER GESTART OP POORT 5000")
    app.run(host='0.0.0.0', port=5000)
