#!/usr/bin/env python
import time  # for time and delay
import sys  # for arguments
import datetime  # for time and delay
from influxdb import InfluxDBClient  # for collecting data
import socket  # for hostname
import bme680  # for sensor data


def get_raspid():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
    return cpuserial


sensor = bme680.BME680()
raspid = get_raspid()

# InfluxDB Configuration
# Set this variables
host = "192.168.178.54"
port = 8086
user = "root"
password = "root"  # TODO: not so secure..
enable_gas = True

# The database we created
dbname = "logger"

# Allow user to set session and runno via args otherwise auto-generate
if len(sys.argv) > 1:
    if (len(sys.argv) < 4):
        print("Must define session (dev/prod), location and temp-offset!!")
        sys.exit()
    else:
        session = sys.argv[1]
        location = sys.argv[2]
        temp_offset = float(sys.argv[3])
else:
    session = "dev"
    location = "unknown"
    temp_offset = 0

now = datetime.datetime.now()
runNo = now.strftime("%Y%m%d%H%M")
hostname = socket.gethostname()

print("Session: ", session)
print("runNo: ", runNo)
print("raspid: ", raspid)
print("hostname: ", hostname)
print("location: ", location)

# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)


# BME680 configuration
# Set sensor configs
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_temp_offset(temp_offset)

if enable_gas:
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)
else:
    sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)

# Sample period (s)
interval = 5

# start_time and curr_time ensure that the
# burn_in_time (in seconds) is kept track of.
start_time = time.time()
curr_time = time.time()
burn_in_time = 400
burn_in_data = []

# Run until keyboard out
try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
    if enable_gas:
        print("Collecting gas resistance burn-in data\n")
        while curr_time - start_time < burn_in_time:
            curr_time = time.time()
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                gas = sensor.data.gas_resistance
                burn_in_data.append(gas)
                print("Gas: {0} Ohms".format(gas))
                time.sleep(1)

        gas_baseline = int(sum(burn_in_data[-50:]) / 50.0)

        # Set the humidity baseline to 40%, an optimal indoor humidity.
        hum_baseline = 40.0

        # This sets the balance between humidity and gas reading in the
        # calculation of air_quality_score (25:75, humidity:gas)
        hum_weighting = 0.25

        print("Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n".format(gas_baseline, hum_baseline))

    # Sensor read loop
    while True:
        if sensor.get_sensor_data():

            hum = sensor.data.humidity
            temp = sensor.data.temperature
            press = sensor.data.pressure

            iso = time.ctime()

            if enable_gas:

                hum_offset = hum - hum_baseline
                gas = int(sensor.data.gas_resistance)
                gas_offset = gas_baseline - gas

                # Calculate hum_score as the distance from the hum_baseline.
                if hum_offset > 0:
                    hum_score = (100 - hum_baseline - hum_offset) / (100 - hum_baseline) * (hum_weighting * 100)

                else:
                    hum_score = (hum_baseline + hum_offset) / hum_baseline * (hum_weighting * 100)

                # Calculate gas_score as the distance from the gas_baseline.
                if gas_offset > 0:
                    gas_score = (gas / gas_baseline) * (100 - (hum_weighting * 100))

                else:
                    gas_score = 100 - (hum_weighting * 100)

                # Calculate air_quality_score.
                air_quality_score = hum_score + gas_score
                # Round to full
                air_quality_score = round(air_quality_score, 0)

                json_body = [
                    {
                        "measurement": session,
                        "tags": {
                            "run": runNo,
                            "raspid": raspid,
                            "hostname": hostname,
                            "location": location
                        },
                        "time": iso,
                        "fields": {
                            "temp": temp,
                            "press": press,
                            "humi": hum,
                            "gas": gas,
                            "iaq": air_quality_score,
                            "gasbaseline": gas_baseline,
                            "humbaseline": hum_baseline
                        }
                    }
                ]

            else:
                json_body = [
                    {
                        "measurement": session,
                        "tags": {
                            "run": runNo,
                            "raspid": raspid,
                            "hostname": hostname,
                            "location": location
                        },
                        "time": iso,
                        "fields": {
                            "temp": temp,
                            "press": press,
                            "humi": hum,
                        }
                    }
                ]

            print(json_body)

            # Write JSON to InfluxDB
            res = client.write_points(json_body)
            print(res)
        else:
            print("Error: .get_sensor_data() or heat_stable failed.")
            break
        # Wait for next sample
        time.sleep(interval)

except KeyboardInterrupt:
    pass
