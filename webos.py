
from flask import Flask, request, render_template_string, jsonify
import subprocess
import os
import pwd
import grp
import socket
import platform
from datetime import datetime

app = Flask(__name__)

# Configuración de seguridad básica
ADMIN_TOKEN = "admin_secret_2024"  # Cambiar por algo más seguro
BASIC_COMMANDS = ['ls', 'pwd', 'whoami', 'date', 'uname', 'ps', 'df', 'free', 'uptime']

def is_privileged(token):
    """Verifica si el token tiene privilegios administrativos"""
    return token == ADMIN_TOKEN

def execute_command(command, privileged=False):
    """Ejecuta comandos del sistema con diferentes niveles de privilegio"""
    try:
        if not privileged:
            # Comandos básicos sin privilegios
            cmd_parts = command.strip().split()
            if not cmd_parts or cmd_parts[0] not in BASIC_COMMANDS:
                return "❌ Comando no permitido sin privilegios", False
        
        # Ejecutar comando
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nERROR: {result.stderr}"
        
        return output, True
        
    except subprocess.TimeoutExpired:
        return "❌ Comando excedió el tiempo límite", False
    except Exception as e:
        return f"❌ Error ejecutando comando: {str(e)}", False

def get_system_info():
    """Obtiene información básica del sistema"""
    try:
        info = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'user': pwd.getpwuid(os.getuid()).pw_name,
            'uid': os.getuid(),
            'gid': os.getgid(),
            'cwd': os.getcwd(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return info
    except:
        return {'error': 'No se pudo obtener información del sistema'}

# Template HTML para la interfaz web
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Web Shell - Control Remoto</title>
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #00ff00; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        .terminal { background: #000; border: 1px solid #333; padding: 15px; border-radius: 5px; }
        .input-group { margin: 10px 0; }
        input[type="text"], input[type="password"] { 
            background: #333; color: #00ff00; border: 1px solid #555; 
            padding: 8px; width: 70%; font-family: monospace; 
        }
        button { 
            background: #444; color: #00ff00; border: 1px solid #555; 
            padding: 8px 15px; cursor: pointer; margin-left: 10px; 
        }
        button:hover { background: #555; }
        .output { 
            background: #111; border: 1px solid #333; padding: 10px; 
            margin: 10px 0; white-space: pre-wrap; max-height: 400px; 
            overflow-y: auto; 
        }
        .info { color: #ffff00; }
        .error { color: #ff0000; }
        .success { color: #00ff00; }
        .privileged { color: #ff6600; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐚 Web Shell - Control Remoto</h1>
            <div class="info">
                Sistema: {{ info.platform }}<br>
                Usuario: {{ info.user }} (UID: {{ info.uid }})<br>
                Directorio: {{ info.cwd }}<br>
                Timestamp: {{ info.timestamp }}
            </div>
        </div>
        
        <div class="terminal">
            <div class="input-group">
                <input type="text" id="command" placeholder="Ingresa comando..." onkeypress="handleEnter(event)">
                <button onclick="executeCommand()">Ejecutar</button>
                <button onclick="clearOutput()">Limpiar</button>
            </div>
            
            <div class="input-group">
                <input type="password" id="token" placeholder="Token admin (opcional)">
                <span class="privileged">⚠️ Token requerido para comandos privilegiados</span>
            </div>
            
            <div class="input-group">
                <button onclick="showHelp()">Ayuda</button>
                <button onclick="getSystemInfo()">Info Sistema</button>
                <button onclick="listFiles()">Listar Archivos</button>
            </div>
            
            <div id="output" class="output">
Bienvenido al Web Shell
Comandos básicos disponibles: {{ basic_commands|join(', ') }}
Para comandos privilegiados, proporciona el token de administrador.

Escribe 'help' para ver más opciones.
            </div>
        </div>
    </div>

    <script>
        function handleEnter(event) {
            if (event.key === 'Enter') {
                executeCommand();
            }
        }
        
        function executeCommand() {
            const command = document.getElementById('command').value;
            const token = document.getElementById('token').value;
            
            if (!command.trim()) return;
            
            appendOutput(`$ ${command}`, 'info');
            
            fetch('/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command, token: token})
            })
            .then(response => response.json())
            .then(data => {
                appendOutput(data.output, data.success ? 'success' : 'error');
                if (data.privileged) {
                    appendOutput('⚠️ Comando ejecutado con privilegios', 'privileged');
                }
            })
            .catch(error => {
                appendOutput(`Error: ${error}`, 'error');
            });
            
            document.getElementById('command').value = '';
        }
        
        function appendOutput(text, className = '') {
            const output = document.getElementById('output');
            const div = document.createElement('div');
            div.textContent = text;
            if (className) div.className = className;
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }
        
        function clearOutput() {
            document.getElementById('output').innerHTML = '';
        }
        
        function showHelp() {
            const helpText = `
Comandos disponibles:
- Básicos (sin token): ls, pwd, whoami, date, uname, ps, df, free, uptime
- Privilegiados (con token): cualquier comando del sistema

Ejemplos:
  ls -la
  ps aux
  cat /etc/passwd (requiere token)
  sudo su (requiere token)
            `;
            appendOutput(helpText, 'info');
        }
        
        function getSystemInfo() {
            fetch('/info')
            .then(response => response.json())
            .then(data => {
                appendOutput(JSON.stringify(data, null, 2), 'info');
            });
        }
        
        function listFiles() {
            document.getElementById('command').value = 'ls -la';
            executeCommand();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Página principal del web shell"""
    info = get_system_info()
    return render_template_string(HTML_TEMPLATE, info=info, basic_commands=BASIC_COMMANDS)

@app.route('/execute', methods=['POST'])
def execute():
    """Endpoint para ejecutar comandos"""
    data = request.get_json()
    command = data.get('command', '').strip()
    token = data.get('token', '').strip()
    
    if not command:
        return jsonify({'output': 'No se proporcionó comando', 'success': False})
    
    # Verificar privilegios
    privileged = is_privileged(token)
    
    # Ejecutar comando
    output, success = execute_command(command, privileged)
    
    return jsonify({
        'output': output,
        'success': success,
        'privileged': privileged
    })

@app.route('/info')
def info():
    """Endpoint para información del sistema"""
    return jsonify(get_system_info())

@app.route('/health')
def health():
    """Endpoint de salud"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Iniciando Web Shell...")
    print(f"📡 Servidor corriendo en puerto 80")
    print(f"🔑 Token admin: {ADMIN_TOKEN}")
    print("⚠️  ADVERTENCIA: Solo usar en entornos controlados")
    
    # Ejecutar en puerto 80 (requiere privilegios root)
    try:
        app.run(host='0.0.0.0', port=80, debug=False)
    except PermissionError:
        print("❌ Error: Se requieren privilegios root para usar puerto 80")
        print("💡 Alternativa: Ejecutar con sudo o usar puerto > 1024")
        # Fallback a puerto 8080
        app.run(host='0.0.0.0', port=8080, debug=False)
