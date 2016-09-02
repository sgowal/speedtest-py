Inspired by a [Reddit post](https://www.reddit.com/r/technology/comments/43fi39/i_set_up_my_raspberry_pi_to_automatically_tweet/), this program measures download and upload speed at regular intervals (using speedtest.net) and displays the measurements through a simple web interface.

# Run the program and exit session (for Raspberry Pi)

```bash
nohup python run.py --root html --host 10.0.0.100 --port 8080 --interval 1800 -db database.db &
exit
```

# Connect

Open Chrome and navigate to http://10.0.0.100:8080.
Once measurements have been made, you should be able to see plots like these:

![Bandwidth](https://raw.githubusercontent.com/sgowal/speedtest-py/master/doc/bandwidth.png)
![Ping](https://raw.githubusercontent.com/sgowal/speedtest-py/master/doc/ping.png)

# If you miss some python packages

```bash
sudo apt-get install python-matplotlib
sudo apt-get install python-pandas
sudo apt-get install python-numpy
```
