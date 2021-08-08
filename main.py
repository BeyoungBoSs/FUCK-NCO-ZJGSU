import json
import uuid
import re
import requests
import datetime
import time

header = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}

with open('user.json', encoding='utf-8') as f:
    users = json.load(f)

for user in users:
    if user['name'] == '你的学号' :
        print('请设置你的学号和密码，在user.json文件中')
        exit()
    s = requests.session()
    s.post('https://nco.zjgsu.edu.cn/login', data=user, headers=header)
    res = s.get('https://nco.zjgsu.edu.cn/', headers=header)
    content = str(res.content, encoding='utf-8')
    if re.search('当天已报送!', content):
        print(datetime.datetime.now().strftime('%Y-%m-%d'), '报送情况： *主动报送*')
        continue
    data = {}
    for item in re.findall(R'<input.+?>', content):
        key = re.search(R'name="(.+?)"', item).group(1)
        value = re.search(R'value="(.*?)"', item).group(1)
        check = re.search(R'checked', item)
        if key not in data.keys():
            data[key] = value
        elif check is not None:
            data[key] = value
    for item in re.findall(R'<textarea.+?>', content):
        key = re.search(R'name="(.+?)"', item).group(1)
        data[key] = ''
    # 为了安全起见，这里还是推荐加上大致的地址和uuid值，虽然经过测试，不填写也可以正常使用
    # ---------------安全线-------------#
    data['uuid'] = str(uuid.uuid1())
    data['locationInfo'] = '浙江省杭州市'
    # ---------------安全线-------------#
    res = s.post('https://nco.zjgsu.edu.cn/', data=data, headers=header)
    timeString=datetime.datetime.now().strftime('%Y-%m-%d')
    result=''
    if re.search('报送成功', str(res.content, encoding='utf-8')) is not None:
        result='报送情况：报送成功'
    elif re.search('当天填报已结束', str(res.content, encoding='utf-8')) is None:
        result='当天填报已结束'
    else:
        result='报送情况：报送失败'
    print(timeString+' '+result)
    #取得推送公众号个人token,支持‘虾推啥’和server酱（又名‘方糖’）
    token = user['token']
    if token != '':
        requests.get('http://wx.xtuis.cn/' + token + '.send?text='+result)
        requests.get('https://sctapi.ftqq.com/' + token + '.send?title='+result)
    time.sleep(5)