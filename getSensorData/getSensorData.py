import os
import subprocess
import threading
import time


class SensorData:
    def __init__(self, temperature, humidity, pressure, soilMoisture, light):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.soilMoisture = soilMoisture
        self.light = light


def getSensorData(deviceId):
    print(f"Sending data request to chip-tool: {deviceId}")

    script = "./getSensorData.sh"

    expiration = 20

    process = subprocess.Popen(
        [script, deviceId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # wait for the process to complete up to expiration
        output, error = process.communicate(timeout=expiration)

        # TODO: handle error

        # initialize empty SensorData object
        data = SensorData(None, None, None, None, None)

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

            # parse temperature with line containing "temperature: " and get value after space. store value in SensorData
            if "temperature: " in line:
                data.temperature = int(line.split("temperature: ")[1])
            if "humidity: " in line:
                data.moisture = int(line.split("humidity: ")[1])
            if "pressure: " in line:
                data.pressure = int(line.split("pressure: ")[1])
            if "soilMoisture: " in line:
                data.soilMoisture = int(line.split("soilMoisture: ")[1])
            if "light: " in line:
                data.pressure = int(line.split("light: ")[1])
    except subprocess.TimeoutExpired as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        # get the process ID from the exception object
        pid = process.pid

        print(
            f"Timeout occurred. The command took longer than {expiration} seconds to execute. Killing process {pid}")

        # kill the process using the process ID
        subprocess.run(["kill", str(pid)])

        return None
    except Exception as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        print(f"Error: {e}")
        return None

    return data


def getSensorDataTask(deviceId):
    # run a loop every 5 seconds
    while True:
        # get sensor data
        data = getSensorData(deviceId)

        if data is not None:
            print(f"Temperature: {data.temperature}")
            print(f"Humidity: {data.humidity}")
            print(f"Pressure: {data.pressure}")
            print(f"SoilMoisture: {data.soilMoisture}")
            print(f"Light: {data.light}")

        # NOTE: this sleep only occurs after getSensorData completes
        print("Waiting 5 seconds...")
        time.sleep(5)


if __name__ == '__main__':
    deviceId = "13"

    # run getSensorDataTask in a background thread
    t = threading.Thread(target=getSensorDataTask, args=(deviceId,))
    t.start()

    # optional: wait for thread to finish
    t.join()
