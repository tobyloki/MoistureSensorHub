import os
import subprocess


def removeDevice(deviceId):
    print(f"Sending unpair request to chip-tool: {deviceId}")

    script = "./removeDevice.sh"

    expiration = 10

    process = subprocess.Popen(
        [script, deviceId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        # delete row in nodeIds.csv that contains deviceId
        with open("../nodeIds.csv", "r") as f:
            fileLines = f.readlines()

        with open("../nodeIds.csv", "w") as f:
            for line in fileLines:
                # deviceId is first column
                if line.strip().split(",")[0] != deviceId:
                    f.write(line)

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

    return True


if __name__ == '__main__':
    deviceId = "4"

    success = removeDevice(deviceId)
    if success is not None and success == True:
        print("Device removed successfully")
