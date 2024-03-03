import datetime
import json
import os
import socket
import time

import requests
import yaml

debug_run = False
try:
    from local_setting import *
    debug_run = True
except:
    SCB_WEBHOOK = os.environ['SCB_WEBHOOK']
    SCB_MESSAGE_ID = os.environ['SCB_MESSAGE_ID']
    SCB_INTERVAL = os.environ['SCB_INTERVAL']

webhook = SCB_WEBHOOK
messageid = SCB_MESSAGE_ID
interval = int(SCB_INTERVAL)*60 # 分に直す

# ステータス絵文字
running = ':white_check_mark:'
stop = ':x:'

class PortCheck:
    def __init__(self, config_path='/script/config.yaml'):
        with open(config_path, encoding='utf-8') as file:
            config = yaml.safe_load(file)
        self.config_yaml = config
    
    def _portcheck(self, config):
        if config['protocol'] == 'TCP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((socket.gethostbyname(config['host']), config['port']))
        elif config['protocol'] == 'UDP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(b'test', (socket.gethostbyname(config['host']), config['port']))
            sock.settimeout(1)
            try:
                sock.recv(1024)
                result = 0
            except:
                result = 1
        
        sock.close()
        if result == 0:
            return running
        else:
            return stop

    def _get_now_time(self):
        dt_now = datetime.datetime.now()
        dt_now = str(dt_now)[:16]
        dt_now = dt_now.replace('-', '/')

        return dt_now

    def _post_discord(self):
        header = {'Content-Type': 'application/json'}
        mes = {
            "embeds": [
                {
                    "title": self.config_yaml['bottitle'],
                    "color": 65280,
                    "footer": {
                        "text": f"last check: {self._get_now_time()}"
                    }
                }
            ]
        }
        body = [
                {
                    'name': '{}'.format(config['name']),
                    'value': '{}'.format(self._portcheck(config=config)),
                    'inline': True
                }for config in self.config_yaml['portcheck']
            ]
        mes['embeds'][0]['fields'] = body

        if len(messageid) == 0:
            requests.post(webhook, json.dumps(mes), headers= header)
        else:
            requests.patch(webhook + '/messages/' + messageid, json.dumps(mes), headers=header)

    def run(self):
        while True:
            self._post_discord()
            time.sleep(interval)



if __name__ == '__main__':
    # デバッグ
    if debug_run:
        # Windowsを想定
        App = PortCheck(r'.\config.yaml')
    else:
        App = PortCheck()

    App.run()