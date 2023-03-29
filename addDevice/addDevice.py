import os
import subprocess


def addDevice(deviceId, code):
    print(f"Sending pair request to chip-tool: {deviceId}")

    script = "./addDevice.sh"

    expiration = 5*60

    process = subprocess.Popen(
        [script, deviceId, code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    success = False

    try:
        # wait for the process to complete up to expiration
        output, error = process.communicate(timeout=expiration)

        # TODO: handle error

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

        # read temp-{deviceId}.txt
        with open(f"temp-{deviceId}.txt", "r") as f:
            fileLines = f.readlines()

            # check if any lines contain "error" regardless of case and is not errorCode=0
            for line in fileLines:
                if "error" in line.lower() and "errorCode=0" not in line and "Unsolicited msg with originator bit clear" not in line:
                    # delete temp.txt
                    try:
                        os.remove(f"temp-{deviceId}.txt")
                    except:
                        pass

                    print(f"Error: {line}")
                    return None

                if "Device commissioning completed with success" in line:
                    success = True

        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass
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

    return success


def getDeviceType(deviceId):
    script = "./getDeviceType.sh"

    process = subprocess.Popen(
        [script, deviceId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    deviceType = "sensor"

    try:
        # wait for the process to complete
        output, error = process.communicate()

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

        # read temp-{deviceId}.txt
        with open(f"temp-{deviceId}.txt", "r") as f:
            fileLines = f.readlines()

            # check if any lines contain "error" regardless of case
            for line in fileLines:
                if "error" in line.lower():
                    # delete temp.txt
                    try:
                        os.remove(f"temp-{deviceId}.txt")
                    except:
                        pass

                    print(f"Error: {line}")
                    return None

                if "UNSUPPORTED_CLUSTER:" in line:
                    deviceType = "actuator"
                    break

        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass
    except Exception as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        print(f"Error: {e}")
        return None

    return deviceType


if __name__ == '__main__':
    code = "31337008017"

    print(f"Pairing code: {code}")

    # read nodeIds.csv
    with open("../nodeIds.csv", "r") as f:
        fileLines = f.readlines()

        # remove all empty lines
        fileLines = [line for line in fileLines if line.strip() != ""]

        # get next nodeId. if file is empty, use 1
        if len(fileLines) == 0:
            nodeId = 1
        else:
            nodeId = int(fileLines[-1].split(",")[0]) + 1

        # check if nodeId already exists. if it does, keep incrementing until it doesn't
        while True:
            if any(str(nodeId) in line for line in fileLines):
                nodeId += 1
            else:
                break

        deviceId = str(nodeId)

        print(f"Adding device with deviceId: {deviceId}")

        success = addDevice(deviceId, code)
        if success is not None and success == True:
            # get device type
            print(f"Getting device type for {deviceId}")
            deviceType = getDeviceType(deviceId)

            if deviceType is not None:
                print(f"Device added successfully: {deviceId}, {deviceType}")

                # write nodeId to file on the next line
                with open("../nodeIds.csv", "a") as f:
                    f.write(f"{deviceId},{deviceType}\n")
