from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import asyncio
import threading
from main import HeartRateMonitor
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Global variables
monitor = None
monitor_thread = None
monitor_loop = None

def debug_print(message):
    """Print message to console and send to frontend."""
    print(message)
    socketio.emit('debug_message', {'message': message})

def run_monitor_async(device_name):
    global monitor, monitor_loop
    
    # Create a new event loop for this thread
    monitor_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(monitor_loop)
    
    monitor = HeartRateMonitor()
    monitor.device_name_filter = device_name
    
    def handle_hr_notification(hr_value, timestamp):
        socketio.emit('heart_rate_update', {'hr': hr_value, 'time': timestamp})
    
    # Set the notification callback
    monitor.notification_callback = handle_hr_notification
    
    # Override print function in monitor to send debug messages
    monitor.debug_print = debug_print
    
    # Run the monitor
    monitor_loop.run_until_complete(monitor.run())
    
    # Clean up
    monitor_loop.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_monitoring():
    global monitor_thread
    device_name = request.json.get('device_name', 'Polar')
    
    if monitor_thread and monitor_thread.is_alive():
        return jsonify({'status': 'error', 'message': 'Monitoring is already running'})
    
    debug_print(f"Starting monitoring for device: {device_name}")
    monitor_thread = threading.Thread(target=run_monitor_async, args=(device_name,))
    monitor_thread.daemon = True  # Make thread daemon so it exits when main program exits
    monitor_thread.start()
    
    return jsonify({'status': 'success', 'message': 'Started monitoring'})

@app.route('/stop', methods=['POST'])
def stop_monitoring():
    global monitor, monitor_thread, monitor_loop
    
    if not monitor or not monitor_thread or not monitor_thread.is_alive():
        return jsonify({'status': 'error', 'message': 'No monitoring session is running'})
    
    filename = request.json.get('filename', 'heart_rate_data')
    debug_print(f"Stopping monitoring and saving to {filename}")
    monitor.running = False
    
    # Wait for the monitoring thread to finish
    monitor_thread.join()
    
    # Save the data
    if monitor.data["heart"]:
        monitor.save_to_csv(filename)
    
    return jsonify({'status': 'success', 'message': 'Stopped monitoring and saved data'})

if __name__ == '__main__':
    socketio.run(app, debug=True) 