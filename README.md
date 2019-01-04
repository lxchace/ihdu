
# 数字杭电爬虫简单版
## 主要功能：登陆数字杭电，选课系统，爬取所需学期的成绩并自动计算绩点输出


```python
import requests  #模拟网页访问模块
import re  #正则表达式模块
import prettytable as pt  #输出漂亮的表格
import execjs  #载入加密JS文件
```


```python
#由于数字杭电现在采用了rsa方式加密，所以我从翻遍代码发现了这个加密的程序
def get_js():
    f = open("des.js", 'r', encoding='utf-8')  # 打开JS文件
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr


def get_des_enwd(data, firstKey, secondKey, thirdKey):
    jsstr = get_js()
    ctx = execjs.compile(jsstr)  #加载JS文件
    return (ctx.call('strEnc', data, firstKey, secondKey,
                     thirdKey))  #调用js方法  第一个参数是JS的方法名，后面的data和key是js方法的参数
```


```python
def loginhdu(xh, pwd):
    #首先访问数字杭电登录页，得到隐藏的lt和execution字段
    response = req.get('http://cas.hdu.edu.cn/cas/login')
    response.enconding = 'utf-8'
    p = r'<input type="hidden" id="lt" name="lt" value="(LT-\d{1,}-[0-9A-Za-z]{1,}-cas)" />'  #正则表达式
    lt = re.search(p, response.text).group(1)
    p = r'<input type="hidden" name="execution" value="([0-9A-Za-z]{1,})" />'
    execu = re.search(p, response.text).group(1)

    #根据取得的隐藏字段，模拟登录请求
    url = "https://cas.hdu.edu.cn/cas/login?service=https%3A%2F%2Fi.hdu.edu.cn%2Ftp_up%2F"
    data = {
        'rsa': get_des_enwd(xh + pwd + lt, '1', '2', '3'),
        'ul': len(xh),
        'pl': len(pwd),
        'lt': lt,
        'execution': execu,
        '_eventId': 'submit'
    }
    head = {
        'Host':
        'cas.hdu.edu.cn',
        'Origin':
        'http://cas.hdu.edu.cn',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36',
        'Referer':
        'https://cas.hdu.edu.cn/cas/login?service=https%3A%2F%2Fi.hdu.edu.cn%2Ftp_up%2F'
    }
    response = req.post(url, data=data, headers=head)
    p = r'<span class="tit">([\S]{1,})</span>'
    try:
        xm = re.findall(p, response.text)[3]  #得到姓名即为登陆成功
        print("您好，" + xm + "!")
        succ = input("如果您发现您的名字不对，请按[N/n]终止程序，否则按任意键继续。\n")
        if (succ == "N" or succ == "n"):
            print("登陆失败！")
            exit()
        else:
            return xm
    except:
        print("登陆失败，请检查学号密码是否正确，或者网络是否正常！")
        exit()
```


```python
def jwxt(xh, xm):
    #登陆数字杭电，进入选课系统
    url = 'http://jxgl.hdu.edu.cn/index.aspx'
    response = req.get(url)
    url = 'http://jxgl.hdu.edu.cn/xs_main.aspx?xh=' + xh
    response = req.get(url)
    p = r'欢迎您：<em><span id="xhxm">([\S]{1,})同学</span></em>'  #正则表达式
    xm_now = re.search(p, response.text).group(1)
    if xm_now == xm:
        return True
    else:
        print("登陆失败！")
        exit()
```


```python
def cxcj(xh, xm, xn, xq):
    #进入选课系统后，查询成绩
    head = {
        'Host':
        'jxgl.hdu.edu.cn',
        'Referer':
        'http://jxglteacher.hdu.edu.cn/xs_main.aspx?xh=' + xh,
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36'
    }
    url = 'http://jxglteacher.hdu.edu.cn/xscjcx_dq.aspx?xh=' + xh + '&xm=' + xm + '&gnmkdm=N121605'
    response = req.get(url, headers=head)
    #先访问查询成绩页，获取隐藏提交项
    
    if(xn!=str(0)):
        view_q = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        event_q = r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />'
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': re.search(view_q, response.text).group(1),
            '__EVENTVALIDATION': re.search(event_q, response.text).group(1),
            'ddlxn': xn,
            'ddlxq': xq,
            'btnCx': '  \262\351 \321\257 '
        }
        head['Referer'] = response.url
        response = req.post(url, headers=head, data=data)

    #获得查询结果，利用正则表达式，匹配成绩
    p=r'<td>.*?</td><td>[12]</td><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td>.*?</td><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td>.*?</td><td>.*?</td><td>.*?</td><td>.*?</td>'
    grades = re.findall(p, response.text)
    mygrades = []
    for each in grades:
        each = [x if x != '&nbsp;' else '' for x in each]
        mygrades.append(list(each))
    return mygrades
```


```python
def calpoint(g):
    #对成绩计算绩点,返回不含课外教育总绩点，含课外教育总绩点以及成绩
    for grade in g:
        if grade[-1] == '优秀':
            grade.append(5)
        elif grade[-1] == '良好':
            grade.append(4)
        elif grade[-1] == '中等':
            grade.append(3)
        elif grade[-1] == '及格':
            grade.append(2)
        elif grade[-1] == '不及格':
            grade.append(0)
        elif int(grade[-1]) >= 95:
            grade.append(5)
        elif int(grade[-1]) >= 60:
            grade.append((int(grade[-1]) - 45) / 10)
        elif int(grade[-1]) < 60:
            grade.append(0)

    credit_w = 0.0  #课外教育类课程学分
    credit_abcds = 0.0
    point_w = 0.0  #课外教育类课程绩点
    point_abcds = 0.0
    for grade in g:
        if grade[0][0] == 'W':
            credit_w = credit_w + float(grade[2])
            point_w = point_w + grade[-1] * float(grade[2])
        else:
            credit_abcds = credit_abcds + float(grade[2])
            point_abcds = point_abcds + grade[-1] * float(grade[2])
    if credit_abcds == 0:
        credit_abcds = 1
    return point_abcds / credit_abcds, (point_abcds + point_w) / (
        credit_abcds + credit_w), g
```


```python
def mypt(grades):
    #利用prettytable规范输出表格
    title = ['课程号', '课程名', '学分', '成绩', '绩点']
    tb = pt.PrettyTable()
    tb.field_names = title
    for each in grades:
        tb.add_row(each)
    return tb
```


```python
with requests.Session() as req:
#     xh = ''  #学号
#     pwd = ''  #密码
#     xn = '2017-2018'  #需要查询成绩学年
#     xq = '2'  #需要查询成绩学期
    xh = input("请输入您的学号：")
    pwd = input("请输入您的密码：")
    xm = loginhdu(xh, pwd)
    jwxt(xh, xm)
    xn = input("请输入您要查询的学年（eg.2018-2019，最近学年学期请直接输入0）：")
    xq = input("请输入您要查询的学期（1或者2，最近学年学期请直接输入0）：")
    grades = cxcj(xh, xm, xn, xq)
    a, b, grades = calpoint(grades)
    grades = mypt(grades)
    print(grades)
    print("不含课外教育总绩点：" + str(a) + "\n含课外教育总绩点：" + str(b))
```

### 示例

![avatar](data:image/png;base64,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)
