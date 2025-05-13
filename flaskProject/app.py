from flask import Flask, request, jsonify, render_template
import csv
from noise import Noiser
import datetime
import os

app = Flask(__name__)

# Example data storage
data_backend = {
    "heart": {
        "rate": [],
        "time": []
    },
    "gyro": {
        "x": [],
        "y": [],
        "z": [],
        "time": []
    },
    "steps": {
        "step_count": [],
        "time": []
    },
    "accel": {
        "x": [],
        "y": [],
        "z": [],
        "time": []
    }

}

collect_data = True

@app.route('/', methods=["POST"])
def save_data():
    data = request.json
    time = datetime.datetime.now()
    if collect_data:
        try:
            data_backend["heart"]["rate"].append(data["heart-rate"])
            data_backend["heart"]["time"].append(time)
        except:
            pass
        try:
            data_backend["gyro"]["x"].append(data["gyro"][0])
            data_backend["gyro"]["y"].append(data["gyro"][1])
            data_backend["gyro"]["z"].append(data["gyro"][2])
            data_backend["gyro"]["time"].append(time)
        except:
            pass
        try:
            data_backend["steps"]["step_count"].append(data["steps"])
            data_backend["steps"]["time"].append(time)
        except:
            pass

        try:
            data_backend["accel"]["x"].append(data["accel"][0])
            data_backend["accel"]["y"].append(data["accel"][1])
            data_backend["accel"]["z"].append(data["accel"][2])
            data_backend["accel"]["time"].append(time)
        except:
            pass

    return 'connected'

@app.route('/data')
def data():
    return jsonify(data_backend)

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/save')
def save():
    time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(f"csv/{time}", exist_ok=True)
    with open(f"csv/{time}/.heart.csv", "w+") as file:
        writer = csv.writer(file)
        writer.writerow(["heartrate", "time"])
        data_obj = data_backend["heart"]

        for index, item in enumerate(data_obj["rate"]):
            writer.writerow([item, data_obj["time"][index]])

    with open(f"csv/{time}/steps.csv", "w+") as file:
        writer = csv.writer(file)
        writer.writerow(["steps", "time"])
        data_obj = data_backend["steps"]

        for index, item in enumerate(data_obj["step_count"]):
            writer.writerow([item, data_obj["time"][index]])

    with open(f"csv/{time}/accel.csv", "w+") as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y", "z", "time"])
        data_obj = data_backend["accel"]

        for index, item in enumerate(data_obj["x"]):
            writer.writerow([item, data_obj["y"][index], data_obj["z"][index], data_obj["time"][index]])

    with open(f"csv/{time}/gyro.csv", "w+") as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y", "z", "time"])
        data_obj = data_backend["gyro"]

        for index, item in enumerate(data_obj["x"]):
            writer.writerow([item, data_obj["y"][index], data_obj["z"][index], data_obj["time"][index]])

    Noiser(time)
    return "success"

@app.route("/reset")
def reset():
    global data_backend
    data_backend = {
        "heart": {
            "rate": [],
            "time": []
        },
        "gyro": {
            "x": [],
            "y": [],
            "z": [],
            "time": []
        },
        "steps": {
            "step_count": [],
            "time": []
        },
        "accel": {
            "x": [],
            "y": [],
            "z": [],
            "time": []
        }

    }
    return "success"

@app.route("/stop")
def stop():
    global collect_data
    collect_data = False
    return "success"

@app.route("/go_on")
def go_on():
    global collect_data
    collect_data = True
    return "success"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
