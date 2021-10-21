# 空气果 Fun Home Assistant 插件

## 接入方式

1. 在路由器自定义域名（DNS劫持，或其他名字）中设置***apn2.airnut.com***指向自己的Home Assistant内网地址，比如我的是***10.0.0.10***，具体方法建议自行搜索。
2. 用[Easylink app](https://www.mxchip.com/easylink/)连接好WiFi后(空气果亮绿灯即连接成功)，双击退出WiFi连接模式。
3. 通过hacs安装，或者复制文件到custom_components
4. 进行如下配置
###
1. 夜间是否更新   is_night_update: False  这功能已经实现，可正常使用
2. 默认情况如下，is_night_update=true  24小时更新，is_night_update=false，夜间停止更新，其余时间照常更新，想一直关闭更新把夜间开始时间改成 00:00:00
3. 检测时间 由 SCAN_INTERVAL = datetime.timedelta(seconds=120)  控制,需要间隔多久自己修改,默认2分钟
4. 想一直亮屏可以修改为1分钟或者更低(触发一次更新pm2.5，会持续亮屏1-2分钟)

```
# 这个是必须有的
airnut:
  #开启定时更新数据 true=24小时更新,false=夜间停止更新，其余时间照常更新，一直关闭更新把夜间开始时间改成 00:00:00
  is_night_update: False
  #夜间开始时间
  night_start_hour: 0001-01-01 23:00:00
  #这里有两个选择，上面的是夜间停止更新，下面的是关闭所有时段自动检测功能
  night_start_hour: 0001-01-01 0:00:00
  #夜间结束时间
  night_end_hour: 0001-01-01 06:00:00
 #天气城市代码
  weathe_code: 101280800
  
# ip为空气果内网的ip地址，空气果1s共四项数据，分别写四个类型的传感器
sensor:
  - platform: airnut
    ip: "10.0.0.105"
    type: temperature
  - platform: airnut
    ip: "10.0.0.105"
    type: humidity
  - platform: airnut
    ip: "10.0.0.105"
    type: pm25
  - platform: airnut
    ip: "10.0.0.105"
    type: battery
  - platform: airnut
    ip: "10.0.0.105"
    type: weathe

# 如果有第二个空气果，可以在下面继续，以此类推
  - platform: airnut
    ip: "10.0.0.xxx"
    type: temperature
  - platform: airnut
    ip: "10.0.0.xxx"
    type: humidity
  - platform: airnut
    ip: "10.0.0.xxx"
    type: pm25
  - platform: airnut
    ip: "10.0.0.xxx"
    type: battery
  - platform: airnut
    ip: "10.0.0.xxx"
    type: weathe



# 定义图标和名称
# 在customize.yaml文件插入下面几项
sensor.airnut_fun_pm25:
  icon: mdi:blur
  friendly_name: 空气质量
sensor.airnut_fun_battery:
  icon: mdi:battery
  friendly_name: 电量
sensor.airnut_fun_temperature:
  icon: mdi:thermometer
  friendly_name: 温度
sensor.airnut_fun_humidity:
  icon: mdi:water-percent
  friendly_name: 湿度
sensor.airnut_fun_weathe:
  icon: mdi:weather-windy
  friendly_name: 天气
  
```
## 里面的城市天气代码需要改成你所在的城市代码
## 代码请到这里寻找
https://help.bj.cn/Weathera/20200304/320AD84ECBB0C14FBCF3518941E56179.html
http://api.help.bj.cn/api/CityCode.XLS
https://cdn.heweather.com/china-city-list.txt 城市代码表
## 天气每隔10分钟更新一次，可谓聊胜于无

# 如果遇到时间不准确，或者是utc时间，请看下面
## 找到项目里面的_init_.py文件，找到下面
## def get_time_unix():
##     return int((datetime.datetime.now() + datetime.timedelta(hours=8)).timestamp())
## 改成
##  return int((datetime.datetime.now() + datetime.timedelta(hours=8)).timestamp())
## 或者
##  return int((datetime.datetime.utcnow() + datetime.timedelta(hours=8)).timestamp())
## 请自行测试那一条适用，导致这个原因是docker环境或者主机环境时区问题影响,每个设备不能同时照顾

# 其他
### 我也是修改的，没有利益关系，如有其它冲突，请告诉

### 最后谢谢之前写airnut 1s的大佬，[原贴地址](https://github.com/billhu1996/Airnut/)


