# bme680_to_influxdb - BME680 Monitoring with InfluxDB

This script sends the data from the RaspberryPI Bosch BME680 module to a InfluxDB. The script itself and the documentation is work-in-progress. However, feel free to open issues for your questions and ideas.

Feel free to read the full story on how to send BME680 sensor logs with a RaspberryPi to InfluxDB and into Grafana on [ayeks.de](https://ayeks.de/post/2018-05-29-bme680-influxdb-grafana/).

## Installation

### InfluxDB on a RaspberryPI

Download and install the InfluxDB ARM package: 
```
wget http://ftp.us.debian.org/debian/pool/main/i/influxdb/influxdb_1.1.1+dfsg1-4+b2_armhf.deb
sudo dpkg -i influxdb_1.1.1+dfsg1-4+b2_armhf.deb 

```

Modify influxdb.conf to enable admin GUI and restart the database.
```
sudo nano /etc/influxdb/influxdb.conf 
sudo service influxdb restart
```

Go to the admin GUI of the InfluxDB and create a new database with the name `logger`:
```
# goto: http://localhost:8083/
CREATE DATABASE "logger"
```


### BME680_to_InfluxDB on a RaspberryPI

You need the [bme680 python lib](https://github.com/pimoroni/bme680), the InfluxDB client and the bme680_to_influx script.
```
pip3 install -r requirements.txt 
git clone https://github.com/ayeks/bme680_to_influxdb
```

Go to the config.ini file and change the values to match your environment. You should change at least `host`, `user` and the `password`.


## Execution

Simply call: `python3 senddata.py "./config.ini" `.

Often you want your Raspberry to execute the senddata script automatically after it started. Use the following to do so:
```
# automated startup:
sudo nano /etc/rc.local
python3 /home/pi/senddata.py "/home/pi/config.ini" &
```


## Analysis
Collecting data is just half the fun without proper analyzing. To crawl through your data just use the InfluxDB admin GUI:
```
# select the "logger" database first!
# show all available measurements
SHOW MEASUREMENTS

# show available tags for measurement
SHOW TAG KEYS FROM "dev"

# get results by measurement
select * from dev

```

In this repo is the [JSON](./grafana_dashboard.json) included that generates the following Grafana Dashboard:

![Grafana BME680 Dashboard](https://ayeks.de/assets/blog/2018-05-29-bme680-influxdb-grafana/grafana-complete-bme680.png)

## Credits

Thanks to John Whittington who wrote [an awesome tutorial for InfluxDB on a RaspberryPI](https://engineer.john-whittington.co.uk/2016/11/raspberry-pi-data-logger-influxdb-grafana/), to Sandy Macdonald who wrote the [Pimoroni tutorial Getting Started with BME680 Breakout](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout) and all the contributors on the [bme680 python lib](https://github.com/pimoroni/bme680).

