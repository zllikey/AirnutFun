"""Airnut Platform"""

import logging
import datetime
import json
import select
import voluptuous as vol
import  threading
import time
import requests
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
)

from .const import (
    DOMAIN,
    ATTR_TEMPERATURE,
    ATTR_HUMIDITY,
    ATTR_PM25,
    ATTR_BATTERY,
    ATTR_VOLUME,
    ATTR_WEATHE,
    ATTR_TIME,
)

CONF_NIGHT_START_HOUR = "night_start_hour"
CONF_NIGHT_END_HOUR = "night_end_hour"
CONF_IS_NIGHT_UPDATE = "is_night_update"
HOST_IP = "0.0.0.0"
CONF_WEATHE_CODE = "weathe_code"
SCAN_INTERVAL = datetime.timedelta(seconds=120)
ZERO_TIME = datetime.datetime.fromtimestamp(0)
weathestate= 0
weathe_status = ""
weathe_code = 101010100


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NIGHT_START_HOUR, default=ZERO_TIME): cv.datetime,
                vol.Optional(CONF_NIGHT_END_HOUR, default=ZERO_TIME): cv.datetime,
                vol.Optional(CONF_IS_NIGHT_UPDATE, default=True): cv.boolean,
                vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
                vol.Optional(CONF_WEATHE_CODE, default="101010100"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

ip_data_dict = {}
socket_ip_dict = {}
sockfda = {}

def setup(hass, config):
    global weathe_code
    """Set up platform using YAML."""
    night_start_hour = config[DOMAIN].get(CONF_NIGHT_START_HOUR)
    night_end_hour = config[DOMAIN].get(CONF_NIGHT_END_HOUR)
    is_night_update = config[DOMAIN].get(CONF_IS_NIGHT_UPDATE)
    scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL)
    weathe_code = config[DOMAIN].get(CONF_WEATHE_CODE)
    
    run_weather = threading.Thread(target=func_weather)  #新建天气循环线程
    run_weather.start()
    
    server = AirnutSocketServer(night_start_hour, night_end_hour, is_night_update, scan_interval,weathe_code,config)

    hass.data[DOMAIN] = {
        'server': server
    }

    return True



def func_weather():
    global weathestate
    global weathe_status
    global weathe_code
    errcount = 0
    wet_dataA={"晴":0,"阴":1,"多云":1,"雨":3,"阵雨":3,"雷阵雨":3,"雷阵雨伴有冰雹":3,"雨夹雪":6,"小雨":3,"中雨":3,"大雨":3,"暴雨":3,"大暴雨":3,"特大暴雨":3,"阵雪":5,"小雪":5,"中雪":5,"大雪":5,"暴雪":5,"雾":2,"冻雨":6,"沙尘暴":2,"小雨转中雨":3,"中雨转大雨":3,"大雨转暴雨":3,"暴雨转大暴雨":3,"大暴雨转特大暴雨":3,"小雪转中雪":5,"中雪转大雪":5,"大雪转暴雪":5,"浮沉":2,"扬沙":2,"强沙尘暴":2,"霾":2}
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}
    while True:
        datayesorno = False
        try:
            res = requests.get('https://api.help.bj.cn/apis/weather/?id='+str(weathe_code),headers=header)
            #print('https://api.help.bj.cn/apis/weather/?id='+str(weathe_code))
            res.encoding='utf-8'
            if res.status_code==200:
                jsonData = res.json()
                jsonwt = jsonData['weather']
                datayesorno = True
                #print(jsonData)
        except:
            continue
        if datayesorno:
            print(jsonData['weather'])
            weathe_status = jsonData['weather']
            try:
                weathestate = wet_dataA[jsonData['weather']]
            except:
                continue
            errcount = 0
            time.sleep(600)
        else:
            errcount = errcount + 1
            if errcount >= 3:
                errcount = 0
                #print(res.text())
                time.sleep(600)
            else:
                time.sleep(30)



def get_time():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

def get_time_unix():
    return int((datetime.datetime.now() + datetime.timedelta(hours=8)).timestamp())
        
async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.config_entries.async_forward_entry_unload(entry, "sensor")

    await hass.async_add_executor_job(hass.data[DOMAIN]['server'].unload)

    return True

class AirnutSocketServer:

    def __init__(self, night_start_hour, night_end_hour, is_night_update, scan_interval,weathe_code,config):
        self._lastUpdateTime = ZERO_TIME
        self._night_start_hour = night_start_hour.strftime("%H%M%S")
        self._night_end_hour = night_end_hour.strftime("%H%M%S")
        self._is_night_update = is_night_update
        self._scan_interval = scan_interval
        self._weathe_code = weathe_code
        self._config = config

        self._socketServer = socket(AF_INET, SOCK_STREAM)
        self._socketServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            self._socketServer.bind((HOST_IP, 10512))
            self._socketServer.listen(5)
        except OSError as e:
            _LOGGER.error("server got %s", e)
            pass

        global socket_ip_dict
        socket_ip_dict[self._socketServer] = HOST_IP

        _LOGGER.debug("socket Server loaded")
        self.update()

    def get_state(self):
        return "new"

    def object_to_json_data(self, object):
        return json.dumps(object).encode('utf-8')

    def json_string_to_object(self, data):
        try:
            return json.loads(data)
        except:
            return None

    def update(self):
        global socket_ip_dict

        read_sockets, write_sockets, error_sockets = select.select(socket_ip_dict.keys(), [], [], 0)

        self.deal_error_sockets(error_sockets)
        self.deal_read_sockets(read_sockets)

        now_time = datetime.datetime.now()
        if now_time - self._lastUpdateTime < self._scan_interval:
            return True
        
        self._lastUpdateTime = now_time

        now_time_str = datetime.datetime.now().strftime("%H%M%S")
        if ((self._is_night_update is False) and
            (self._night_start_hour < now_time_str or self._night_end_hour > now_time_str)):
            return True

        self.deal_write_sockets(socket_ip_dict.keys())
        
        return True
    
    def deal_error_sockets(self, error_sockets):
        global socket_ip_dict
        for sock in error_sockets:
            del socket_ip_dict[sock]
    
    def deal_read_sockets(self, read_sockets):
        #接收数据
        detect_msg = {"common": {"device": "Fun_pm25", "protocol": "detect"}, "param": {"fromport": 8023, "airid": 1010695, "fromhost": "one"}}
        global weathestate
        check_msg = {"common": {"code": 0, "protocol": "get_weather"}, "param": {"weather": "weathercode", "time": get_time_unix()}}
        check_msg=json.dumps(check_msg)
        check_msg=check_msg.replace("weathercode",str(weathestate))
        check_msg=json.loads(check_msg)
        
        global ip_data_dict
        global sockfda
        for sock in read_sockets:
            if sock == self._socketServer:
                _LOGGER.info("going to accept new connection")
                try:
                    sockfd, (host, _) = sock.accept()
                    sockfda = sockfd
                    socket_ip_dict[sockfd] = host
                    _LOGGER.info("Client (%s) connected", socket_ip_dict[sockfd])
                    try:
                        #连接首先发送一次对时
                        sockfd.send(self.object_to_json_data(check_msg))
                        time.sleep(15)
                        sockfd.send(self.object_to_json_data(detect_msg))
                    except OSError as e:
                        _LOGGER.error("Client error 1 %s", e)
                        sockfd.shutdown(2)
                        sockfd.close()
                        del socket_ip_dict[sockfd]
                        continue
                        
                except OSError:
                    _LOGGER.warning("Client accept failed")
                    continue
            else:
                originData = None
                try:
                    originData = sock.recv(1024)
                    _LOGGER.debug("Receive originData %s", originData)
                except OSError as e:
                    _LOGGER.warning("Processing Client error 2 %s", e)
                    continue
                if originData:
                    datas = originData.decode('utf-8').split("\n\r")
                    for singleData in datas:
                        jsonData = self.json_string_to_object(singleData)
                        if (jsonData is not None and
                            jsonData["common"]["protocol"] == "login"):
                            sock.send(self.object_to_json_data({"common": {"data": {}, "code": 0, "protocol": "login"}}))
                        if (jsonData is not None and
                            jsonData["common"]["protocol"] == "post"):
                            global weathe_status
                            ip_data_dict[socket_ip_dict[sock]] = {
                                ATTR_PM25: int(jsonData["param"]["pm25"]),
                                ATTR_TEMPERATURE: format(float(jsonData["param"]["t"]), '.1f'),
                                ATTR_HUMIDITY: format(float(jsonData["param"]["h"]), '.1f'),
                                ATTR_BATTERY: int(jsonData["param"]["battery"]),
                                ATTR_WEATHE: weathe_status,
                                ATTR_TIME: get_time(),
                            }
                            _LOGGER.debug("ip_data_dict %s", ip_data_dict)
                        if (jsonData is not None and
                            jsonData["common"]["protocol"] == "heartbeat"):
                            #心跳一次更新一次时间和天气
                            sock.send(self.object_to_json_data(check_msg))
                            continue
    def deal_write_sockets(self, write_sockets):
        #发送数据
        #持续检测，持续亮屏，风扇问题晚上很吵 ，调整 SCAN_INTERVAL = datetime.timedelta(seconds=60)  里面的数字
        global socket_ip_dict
        global weathestate
        check_msg = {"common": {"device": "Fun_pm25", "protocol": "detect"}, "param": {"fromport": 8023, "airid": 1010695, "fromhost": "interval"}}
        for sock in write_sockets:
            if sock == self._socketServer:
                continue
            try:
                sock.send(self.object_to_json_data(check_msg))
            except:
                del socket_ip_dict[sock]


    def get_data(self, ip):
        try:
            global ip_data_dict
            return ip_data_dict[ip]
        except:
            return {}

    def unload(self):
        """Signal shutdown of sock."""
        _LOGGER.info("AirnutSensor Sock close")
        self._socketServer.shutdown(2)
        self._socketServer.close()
