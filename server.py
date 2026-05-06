import os, subprocess, requests, json
from flask import Flask, request, send_from_directory

app = Flask(__name__)

# Конфиг WireGuard
WG_CONF = "/etc/wireguard/wg0.conf"

# Пароль для админ-панели
ADMIN_PASS = os.environ.get("ADMIN_PASS", "habvpn2025")

# Хранилище клиентов
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
    
    # Генерируем ключи
    privkey = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
    pubkey = subprocess.run(["wg", "pubkey"], input=privkey, capture_output=True, text=True).stdout.strip()
    
    clients = load_clients()
    clients[name] = {'pubkey': pubkey, 'privkey': privkey}
    save_clients(clients)
    
    # Конфиг для клиента
    config = f"""[Interface]
PrivateKey = {privkey}
Address = 10.0.0.{len(clients) + 1}/24
DNS = 1.1.1.1

[Peer]
PublicKey = SERVER_PUBKEY
Endpoint = habvpn-server.onrender.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    
    return {'config': config, 'name': name}

@app.route('/api/clients')
def list_clients():
    return load_clients()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
