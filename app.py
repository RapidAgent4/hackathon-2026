from flask import Flask, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def home():
    # Minimal inline HTML + SocketIO client just to test the connection
    return """
    <h1>Server is running!</h1>
    <p id="status">Connecting to WebSocket...</p>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io();
        socket.on('connect', () => {
            document.getElementById('status').innerText = "✅ WebSocket Connected! ID: " + socket.id;
        });
    </script>
    """

@socketio.on('connect')
def handle_connect():
    print(f"🔥 A user connected! Their session ID is: {request.sid}")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)