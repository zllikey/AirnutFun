# 空气果 Fun Home Assistant 插件

## 接入方式

1. 在路由器自定义域名（DNS劫持，或其他名字）中设置***apn2.airnut.com***指向自己的Home Assistant内网地址，比如我的是***10.0.0.10***，具体方法建议自行搜索。
2. 用[Easylink app](https://www.mxchip.com/easylink/)连接好WiFi后(空气果亮绿灯即连接成功)，双击退出WiFi连接模式。
3. 通过hacs安装，或者复制文件到custom_components
4. 进行如下配置

```
#这个是必须有的
airnut:
  #夜间是否更新
  is_night_update: False
  #夜间开始时间
  night_start_hour: 0001-01-01 23:00:00
  #夜间结束时间
  night_end_hour: 0001-01-01 06:00:00
 #天气城市代码
  weathe_code: 101280800
  
#ip为空气果内网的ip地址，空气果1s共四项数据，分别写四个类型的传感器
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

#如果有第二个空气果，可以在下面继续，以此类推
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

```
#里面的城市天气代码需要改成你所在的城市代码
#代码请到这里寻找
https://help.bj.cn/Weathera/20200304/320AD84ECBB0C14FBCF3518941E56179.html
http://api.help.bj.cn/api/CityCode.XLS
#天气每隔10分钟更新一次，可谓聊胜于无

## 其他
我也是修改的，没有利益关系，如有其它冲突，请告诉

最后谢谢之前写airnut 1s的大佬，[原贴地址](https://github.com/billhu1996/Airnut/)


