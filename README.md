# Run the program and exit session (for Raspberry Pi)

```bash
nohup python run.py --root html --host 10.0.0.100 --port 8080 --interval 1800 &
exit
```

# Connect

Open Chrome and navigate to http://10.0.0.100:8080

# If you miss some python packages

```bash
sudo apt-get install python-matplotlib
sudo apt-get install python-pandas
sudo apt-get install python-numpy
```
