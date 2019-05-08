
# coding: utf-8

# # 数字杭电爬虫简单版
# ## 主要功能：登陆数字杭电，选课系统，爬取所需学期的成绩并自动计算绩点输出

# In[ ]:


import requests  #模拟网页访问模块
import re  #正则表达式模块
import prettytable as pt  #输出漂亮的表格
import execjs  #载入加密JS文件


# In[ ]:


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


# In[ ]:


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


# In[ ]:


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


# In[ ]:


def cxcj(xh, xm):
    #进入选课系统后，查询所有成绩
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
    
    
    view_q = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
    event_q = r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />'
    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': re.search(view_q, response.text).group(1),
        '__EVENTVALIDATION': re.search(event_q, response.text).group(1),
        'ddlxn': '',
        'ddlxq': '',
        'btnCx': '  \262\351 \321\257 '
    }
    head['Referer'] = response.url
    response = req.post(url, headers=head, data=data)

    #获得查询结果，利用正则表达式，匹配成绩
    p=r'<td>(.*?)</td><td>([12])</td><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td>.*?</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td>.*?</td><td>.*?</td><td>.*?</td><td>.*?</td>'
    grades = re.findall(p, response.text)
    mygrades = []
    for each in grades:
        each = [x if x != '&nbsp;' else '' for x in each]
        mygrades.append(list(each))
    return mygrades


# In[ ]:


def xqcj(grades,xn,xq):
    #筛选所需要学期成绩
    final_grades = []
    for each in grades:
        if xn in [each[0],''] and xq in [each[1],'']:
            final_grades.append(each)
    return final_grades


# In[ ]:


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
        if grade[2][0] == 'W':
            credit_w = credit_w + float(grade[4])
            point_w = point_w + grade[-1] * float(grade[4])
        else:
            credit_abcds = credit_abcds + float(grade[4])
            point_abcds = point_abcds + grade[-1] * float(grade[4])
    if credit_abcds == 0:
        credit_abcds = 1
    return point_abcds / credit_abcds, (point_abcds + point_w) / (
        credit_abcds + credit_w), g


# In[ ]:


def mypt(grades):
    #利用prettytable规范输出表格
    title = ['学年','学期','课程号', '课程名', '学分', '平时成绩', '期中成绩', '期末成绩', '实验成绩', '成绩', '绩点']
    tb = pt.PrettyTable()
    tb.field_names = title
    for each in grades:
        tb.add_row(each)
    return tb


# In[ ]:


with requests.Session() as req:
    #xh = ''  #学号
    #pwd = ''  #密码
    #xn = '2016-2017'  #需要查询成绩学年
    #xq = '1'  #需要查询成绩学期
    xh = input("请输入您的学号：")
    pwd = input("请输入您的密码：")
    xm = loginhdu(xh, pwd)
    jwxt(xh, xm)
    xn = input("请输入您要查询的学年（eg.2018-2019，所有学年请直接回车）：")
    xq = input("请输入您要查询的学期（1或者2，所有学期请直接回车）：")
    grades = cxcj(xh, xm)
    grades = xqcj(grades,xn,xq)
    #print(grades)
    a, b, grades = calpoint(grades)
    grades = mypt(grades)
    print(grades)
    print("不含课外教育总绩点：" + str(a) + "\n含课外教育总绩点：" + str(b))


# ### 示例

# ![avatar](example.png)
