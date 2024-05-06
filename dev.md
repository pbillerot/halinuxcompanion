
- https://github.com/muniter/halinuxcompanion/tree/master


## Python
- sudo apt install virtualenv
- virtualenv --python=/usr/bin/python3 venv

- source venv/bin/activate
- (venv) pip install --upgrade pip
- (venv) pip install -r requirements.txt

- python -m halinuxcompanion --config config.json

```python
import datetime as dt
def get_current_charge():
     f = open('/sys/class/power_supply/BAT0/capacity')
     charge, time = round(int(f.read().strip('\n'))/1000), dt.datetime.now().strftime('%H:%M %D') 
     f.close()
     return charge,time 
```

- sudo cp /home/billerot/dev/halinuxcompanion/halinuxcompanion/resources/halinuxcompanion.service /etc/systemd/system/halinuxcompanion.service
- sudo systemctl start halinuxcompanion
- sudo systemctl enable halinuxcompanion
