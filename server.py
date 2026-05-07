import os, json, subprocess
from flask import Flask, request, send_from_directory

app = Flask(__name__)

ADMIN_PASS = os.environ.get("ADMIN_PASS", "habvpn2025")
CLIENTS_FILE = "clients.json"

def load_clients():
    try:
        with open(CLIENTS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_clients(data):
    with open(CLIENTS_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return send_from_directory('.', 'admin.html')

@app.route('/api/add_client', methods=['POST'])
def add_client():
    data = request.get_json()
    name = data.get('name', 'client')
    password = data.get('pass', '')
    if password != ADMIN_PASS:
        return {'error': 'wrong password'}, 403
    
    port = 10000 + len(load_clients()) + 1
    secret = subprocess.run(["openssl", "rand", "-base64", "16"], capture_output=True, text=True).stdout.strip()
    method = "chacha20-ietf-poly1305"
    
    clients = load_clients()
    clients[name] = {'port': port, 'secret': secret, 'method': method}
    save_clients(clients)
    
    config = f"ss://{method}:{secret}@habvpn-server.onrender.com:{port}#HabVPN-{name}"
    
    return {'config': config, 'name': name}

@app.route('/api/clients')
def list_clients():
    return load_clients()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
