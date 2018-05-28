# bme680_to_influxdb - BME680 Monitoring with InfluxDB

This script sends the data from the RaspberryPI Bosch BME680 module to a InfluxDB. The script itself and the documentation is work-in-progress. However, feel free to open issues for your questions and ideas.

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


### Send data script

You need the [bme680 python lib](https://github.com/pimoroni/bme680) and the InfluxDB client. In my case the bme680 temperature readings are 3.5 degrees celsius to low, therefore I wrote a [pull request](https://github.com/pimoroni/bme680/pull/13) to allow some offset calculation. Until the pull request is merged you should clone from my [bme680 repo](https://github.com/ayeks/bme680/tree/offset).
```
sudo pip3 install influxdb
git clone https://github.com/ayeks/bme680 -b offset
cd bme680/library
sudo python3 setup.py install
```


## Execution

Simply call: `python3 senddata.py` to use the default values. If you want to define a session, location and temperature offset use: `python3 senddata.py "dev" "livingroom" -3.5`.

Often you want your Raspberry to execute the senddata script automatically after it started. Use the following to do so:
```
# automated startup:
sudo nano /etc/rc.local
python3 /home/pi/senddata.py "dev" "livingroom" -3.5 &
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

Stay tuned for some fancy Grafana examples..

## Credits

Thanks to John Whittington who wrote [an awesome tutorial for InfluxDB on a RaspberryPI](https://engineer.john-whittington.co.uk/2016/11/raspberry-pi-data-logger-influxdb-grafana/), to Sandy Macdonald who wrote the [Pimoroni tutorial Getting Started with BME680 Breakout](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout) and all the contributors on the [bme680 python lib](https://github.com/pimoroni/bme680).

