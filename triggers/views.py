# coding=utf-8
from __future__ import unicode_literals
from django.contrib.auth import authenticate, login, logout, user_login_failed
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, render_to_response, HttpResponseRedirect, redirect
from django.template import RequestContext
from triggers.models import Hosts, Parameters, TriggerWarrning, ZhuanXian, Video, Item, ItemLastValue, History, \
    InitPara, NetDevices, FtpServer
from zbtrigger.settings import BASE_DIR
from filecmp import cmp
from datetime import *
from django.db import connection, transaction
from django.http import HttpResponse
from django.contrib.auth.models import User
import json
import urllib2
import time
import datetime
import threading
import os
import telnetlib
import ftplib
import sys
import pynetsnmp


# login
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    print username, password
    user = authenticate(username=username, password=password)
    print user
    print request.path
    if user is not None:
        if user.is_active:
            login(request, user)
            return render(request, 'triggers/index.html')
            return red
        else:
            return render(request, 'triggers/error.html')
    else:
        return render(request, 'triggers/login.html')


# logout
def logout_view(request):
    logout(request)
    return render(request, 'triggers/logout.html')


def login_error(request):
    return render(request, 'triggers/error.html')


# 首页
@login_required(login_url='/trigger/login')
def index(request):
    return render(request, 'triggers/index.html')


# 通过zabbix server api 返回结果集（数组字典）
def request_zabbix(url, data, header_type, header_json):
    request_http = urllib2.Request(url, data)
    request_http.add_header(header_type, header_json)
    try:
        result_data = urllib2.urlopen(request_http)
        response_data = json.loads(result_data.read())
        result_data.close()
        if 'error' in response_data.keys():
            return ''
        else:
            return response_data['result']
    except urllib2.URLError, e:
        print url, e
        return ''


# 过滤参数的空格
def filter_space(*parameter):
    string = []
    for p in parameter:
        if p:
            p1 = str.strip(p.encode("utf-8"))
        else:
            p1 = ""
        string.append(p1)
    return string


# 第一步：手工添加的服务器参数初始化，获取authid
def parameter_init(request):
    p_server = Parameters.objects.all()
    server_status = []
    for parameter in p_server:
        data = json.dumps(
            dict(jsonrpc="2.0",
                 method="user.login",
                 params={
                     "user": parameter.user,
                     "password": parameter.password,
                 },
                 id=0
                 )
        )
        parameter.authid = request_zabbix(parameter.url, data, parameter.header_type, parameter.header_json)
        # print parameter.serverip, parameter.authid
        if parameter.authid != '':
            parameter.save()
            result1 = {
                'serverip': parameter.serverip,
                'status': u'成功',
            }
            server_status.append(result1)
        else:
            result2 = {
                'serverip': parameter.serverip,
                'status': u'失败',
            }
            server_status.append(result2)
    return render(request, 'triggers/parameter_init.html', {'server_status': server_status})


# 第二步：主机同步线程 后台每小时同步一次
def host_thread(request):
    start = time.time()
    p_server = Parameters.objects.all()
    # p_server = Parameters.objects.filter(company=u'北京总部')
    host1 = []
    Hosts.objects.all().delete()

    def request_thread(url, data_json, header_type, header_json, hostid, company, hostname, status):
        re = request_zabbix(url, data_json, header_type, header_json)
        if re:
            for r in re:
                req = {
                    "hostid": hostid,
                    "company": company,
                    "hostname": hostname,
                    "hostip": r['ip'],
                    "status": status
                }
                host1.append(req)

    for parameter in p_server:
        data = json.dumps(
            dict(jsonrpc="2.0",
                 method="host.get",
                 params={
                     "output": ["hostid", "name", "status"],
                     "filter": {"status": 0},
                 },
                 auth=parameter.authid,
                 id=1
                 )
        )
        host_zabbix = request_zabbix(parameter.url, data, parameter.header_type, parameter.header_json)
        t = []
        for host in host_zabbix:
            data_hostinterface = json.dumps(
                dict(jsonrpc="2.0",
                     method="hostinterface.get",
                     params={
                         "output": ["hostid", "ip"],
                         "hostids": {"hostid": host['hostid']},
                         "limit": 1
                     },
                     auth=parameter.authid,
                     id=1
                     )
            )
            t.append(threading.Thread(target=request_thread, args=(parameter.url,
                                                                   data_hostinterface,
                                                                   parameter.header_type,
                                                                   parameter.header_json,
                                                                   host['hostid'],
                                                                   parameter.company,
                                                                   host['name'],
                                                                   host['status']
                                                                   )))

        for j in range(len(t)):
            t[j].daemon = True
            t[j].start()

        for z in range(len(t)):
            t[z].join()

    for h in host1:
        # if not Hosts.objects.filter(hostip=h['hostip']):
        # print h['hostid'], h['hostip']
        h1 = Hosts(company=h['company'], hostid=h['hostid'], hostname=h['hostname'], hostip=h['hostip'],
                   status=h['status'])
        h1.save()
    end = time.time()
    print end - start
    # return render(request, 'triggers/host_init.html')


# 第三步：异常同步线程，后台每2分钟同步一次
def trigger_thread(request):
    start = time.time()
    TriggerWarrning.objects.all().delete()
    p_host = Hosts.objects.all()
    t = []
    trigger1 = []

    def request_thread(url, data, header_type, header_json, host_id, hostid, company, hostname, hostip):
        re = request_zabbix(url, data, header_type, header_json)
        if re:
            for r in re:
                req = {
                    "host_id": host_id,
                    "hostid": hostid,
                    "company": company,
                    "hostname": hostname,
                    "hostip": hostip,
                    "triggerid": r['triggerid'],
                    "lastchange": r['lastchange'],
                    "description": r['description']
                }
                trigger1.append(req)

    for host in p_host:
        parameter = Parameters.objects.get(company=host.company)
        data_trigger = json.dumps(
            dict(jsonrpc="2.0",
                 method="trigger.get",
                 params={
                     "output": ["triggerid", "description", "lastchange"],
                     "filter": {"value": 1, "status": 0},
                     "hostids": {"hostid": host.hostid},
                 },
                 auth=parameter.authid,
                 id=1
                 )
        )
        t.append(threading.Thread(target=request_thread, args=(parameter.url,
                                                               data_trigger,
                                                               parameter.header_type,
                                                               parameter.header_json,
                                                               host.id,
                                                               host.hostid,
                                                               host.company,
                                                               host.hostname,
                                                               host.hostip)))

    for j in range(len(t)):
        t[j].daemon = True
        t[j].start()

    for z in range(len(t)):
        t[z].join()

    for trigger in trigger1:
        timearray = time.localtime(float(trigger['lastchange']))
        trigger['lastchange'] = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
        if not TriggerWarrning.objects.filter(hostip=trigger['hostip'], description=trigger['description']):
            t1 = TriggerWarrning(hosts_id=trigger['host_id'],
                                 company=trigger['company'],
                                 hostname=trigger['hostname'],
                                 hostip=trigger['hostip'],
                                 triggerid=trigger['triggerid'],
                                 hostid=trigger['hostid'],
                                 description=trigger['description'],
                                 lastchange=trigger['lastchange']
                                 )
            t1.save()
    end = time.time()
    print end - start
    # return render(request, 'triggers/trigger_init.html')


# 手动同步添加设备【主要是专线和互联网信息】的主机ID，获取hostid
def item_init(request):
    item_list = Item.objects.all()
    for item in item_list:
        item.hostid = Hosts.objects.get(hostip=item.hostip, company=item.company).hostid
        item.save()
    return render(request, 'triggers/item_init.html')


# 获取专线状态
def zhuanxian_status(request):
    # zhuanxian status
    z_status = []
    z_host = ZhuanXian.objects.all()
    for host in z_host:
        z_trigger = TriggerWarrning.objects.filter(hostip=host.hostip)
        if z_trigger:
            for t in z_trigger:
                h1 = {
                    "hostname": t.hostname,
                    "description": t.description.strip('{HOST.NAME}-')
                }
                z_status.append(h1)
        else:
            h2 = {
                "hostname": host.hostname,
                "description": u'正常'
            }
            z_status.append(h2)
    return HttpResponse(json.dumps(z_status), content_type='application/json')


# 获取专线最新值
def zhuanxian_lastvalue(request):
    # zhuanxian lastvalue
    z_lastvalue = []
    v_z = ItemLastValue.objects.filter(description__contains='专线')
    for v in v_z:
        # print unicode(v.description)
        v_result = {
            'company': v.description.strip('专线'),
            'invalue': v.invalue.strip('Mbits'),
            'outvalue': v.outvalue.strip('Mbits')
        }
        z_lastvalue.append(v_result)
    return HttpResponse(json.dumps(z_lastvalue), content_type='application/json')


# 获取设备数据
def device_value(request):
    # device and abnormal
    device_data = []
    parameter_list = Parameters.objects.all()
    for p in parameter_list:
        v_num = 0  # video problem num
        trigger = TriggerWarrning.objects.filter(company=p.company)
        for t in trigger:
            if Video.objects.filter(hostip=t.hostip) and u'中断' in t.description:
                v_num += 1
        h_list = {"id": p.id,
                  "servername": p.company,
                  "serverip": p.serverip,
                  "hostnum": Hosts.objects.filter(company=p.company).count(),
                  "problemnum": trigger.count() - v_num
                  }
        device_data.append(h_list)
    return HttpResponse(json.dumps(device_data), content_type='application/json')


# 获取互联网最新值
def internet_lastvalue(request):
    # internet lastvalue
    internet_lastvalue = []
    v_i = ItemLastValue.objects.filter(description__contains='互联网')
    for v in v_i:
        v_result = {
            'company': v.description.strip('互联网'),
            'invalue': v.invalue.strip('Mbits'),
            'outvalue': v.outvalue.strip('Mbits')
        }
        # print v_result
        internet_lastvalue.append(v_result)
    return HttpResponse(json.dumps(internet_lastvalue), content_type='application/json')


# 获取视频会议状态
def video_status(request):
    v_host = Video.objects.all().order_by('hostip')
    v_active = 0  # video action num
    v_syn = 0
    for host in v_host:
        trigger = TriggerWarrning.objects.filter(hostip=host.hostip, company=host.dcname, description__contains='中断')
        if not trigger:
            v_active += 1  # video action num
    v_total = v_host.count()
    if v_active == v_total:
        v_syn = 1
    v_status = {
        "total": v_total,
        "active": v_active,
        "syn": v_syn
    }
    return HttpResponse(json.dumps(v_status), content_type='application/json')


# 获取设备数据
def device(request):
    index_result = {}
    index_list = []
    status = 0  # trigger syn status
    h_total = 0  # host number
    p_total = 0  # host problem num
    parameter_list = Parameters.objects.all()
    for p in parameter_list:
        v_num = 0  # video problem num
        trigger = TriggerWarrning.objects.filter(company=p.company)
        for t in trigger:
            if Video.objects.filter(hostip=t.hostip) and u'中断' in t.description:
                v_num += 1
        h_list = {"id": p.id,
                  "servername": p.company,
                  "serverip": p.serverip,
                  "hostnum": Hosts.objects.filter(company=p.company).count(),
                  "problemnum": trigger.count() - v_num
                  }
        h_total += int(h_list['hostnum'])
        p_total += int(h_list['problemnum'])
        index_list.append(h_list)
        for i in index_list:
            if i['problemnum'] != 0:
                status = 1
        index_result = {
            "h_total": h_total,
            "p_total": p_total,
            "status": status
        }

    return render(request, 'triggers/device.html', {'index_list': index_list,
                                                    'index_result': index_result
                                                    })


# 获取设备异常列表
def trigger_list(request, server):
    t_list = []
    trigger = TriggerWarrning.objects.filter(company=unicode(server))
    for t in trigger:
        if not Video.objects.filter(hostip=t.hostip):  # 过滤视频会议
            t1_list = {
                "triggerid": t.triggerid,
                "hostname": t.hostname,
                "hostip": t.hostip,
                "description": t.description,
                "lastchange": t.lastchange
            }
            t_list.append(t1_list)
        elif u'中断' not in t.description:
            t1_list = {
                "triggerid": t.triggerid,
                "hostname": t.hostname,
                "hostip": t.hostip,
                "description": t.description,
                "lastchange": t.lastchange
            }
            t_list.append(t1_list)
    return render(request, 'triggers/trigger_list.html', {'trigger_list': t_list, 'servername': server},
                  context_instance=RequestContext(request))


# 获取设备列表
def host_list(request, server_name):
    hostname = request.GET.get('q_hostname')
    ip = request.GET.get('q_ip')
    string = filter_space(hostname, ip)
    if string:
        host = Hosts.objects.filter(company=unicode(server_name),
                                    hostname__contains=string[0],
                                    hostip__contains=string[1]).order_by('hostip')
    else:
        host = Hosts.objects.filter(company=unicode(server_name)).order_by('hostip')
    return render_to_response('triggers/host.html',
                              {'host_list': host, 'servername': server_name,
                               'q_hostname': string[0], 'q_ip': string[1]
                               },
                              context_instance=RequestContext(request))


# 获取专线详细信息
def zhuanxian_detail(request, name):
    z_detail = ZhuanXian.objects.get(hostname=unicode(name))
    return render(request, 'triggers/zhuanxian_detail.html', {'z_tail': z_detail})


# 获取视频会议列表
def video(request):
    v_meeting = []
    v_host = Video.objects.all().order_by('hostip')
    v_active = 0  # video action num
    v_syn = 0
    for host in v_host:
        trigger = TriggerWarrning.objects.filter(hostip=host.hostip, company=host.dcname, description__contains='中断')
        if trigger:  # 如视频终端有“中断”表示没有开会
            for t in trigger:
                host.lastchange = t.lastchange
                host.description = t.description
                host.save()
        else:  # 视频终端非“中断”表示在开会
            v_active += 1  # video action num
            h2 = {
                "id": host.id,
                "company": host.company,
                "hostname": host.hostname,
                "hostip": host.hostip,
                "description": u'正在开会...'
            }
            v_meeting.append(h2)
            host.description = u'正在开会...'
            host.save()
    v_total = v_host.count()
    if v_active == v_total:
        v_syn = 1
    v_num = {
        "total": v_total,
        "active": v_active,
        'syn': v_syn
    }
    return render_to_response('triggers/video.html', {'v_host': v_host, 'v_meeting': v_meeting, 'v_num': v_num},
                              context_instance=RequestContext(request))


# 获取视频会议详细信息
def video_detail(request, h_ip):
    v_detail = Video.objects.get(hostip=h_ip)
    return render(request, 'triggers/video_detail.html', {'v_detail': v_detail})


# 同步专线及互联网带宽
def item_last(request):
    item = Item.objects.all()
    for i in item:
        parameter = Parameters.objects.get(company=i.company)
        data_item = json.dumps(
            dict(jsonrpc="2.0",
                 method="item.get",
                 params={
                     "output": ["itemid", "name", "lastvalue", "lastclock"],
                     "hostids": i.hostid,
                     "filter": {"key_": i.itemkey}
                 },
                 auth=parameter.authid,
                 id=1
                 )
        )
        data_result = request_zabbix(parameter.url, data_item, parameter.header_type, parameter.header_json)
        if data_result:
            data_list = []
            for r in data_result:
                timeclock = time.localtime(float(r['lastclock']))
                i.itemid = r['itemid']
                v = float(r['lastvalue'])
                if i.description.__contains__('互联网') or i.description.__contains__('专线'):
                    i_value = v / 1000000
                    i.lastvalue = round(i_value, 2).__str__() + 'Mbits'
                else:
                    i.lastvalue = round(v, 2).__str__()
                i.lastclock = time.strftime("%Y-%m-%d %H:%M:%S", timeclock)
                h = History(company=i.company, itemid=r['itemid'], value=i.lastvalue, clock=i.lastclock)
                data_list.append(h)
                i.save()
            History.objects.bulk_create(data_list)

    value = Item.objects.all()
    des = []
    for v in value:

        if (v.description not in des) and (v.description.__contains__('互联网') or v.description.__contains__('专线')):
            des.append(v.description)

    ItemLastValue.objects.all().delete()
    for d in des:
        in_item = Item.objects.get(description=d, itemname__contains='in')
        out_item = Item.objects.get(description=d, itemname__contains='out')
        i_value = ItemLastValue(company=in_item.company, description=d, invalue=in_item.lastvalue,
                                itemid='IN:' + in_item.itemid + '-OUT:' + out_item.itemid,
                                outvalue=out_item.lastvalue, clock=in_item.lastclock
                                )
        i_value.save()


# 获取线路速度历史数据（专线及互联网）
def line_history(request, item_description):
    global h_in, h_out
    times = request.GET.get('hours')
    if times:
        t = int(times) * 60
    else:
        t = 0
    num = 60
    if t != 0:
        num = t
    h_in_data = []
    h_out_data = []
    item = Item.objects.filter(description=item_description)
    if item:
        for i in item:
            if i.itemname.__contains__('in'):
                h_in = History.objects.filter(itemid=i.itemid).order_by('-clock')[:num]
            if i.itemname.__contains__('out'):
                h_out = History.objects.filter(itemid=i.itemid).order_by('-clock')[:num]
        for h in h_in:
            v = h.value.strip('Mbits')
            h1 = {
                'value': float(v.encode()),
                'clock': time.strftime('%H:%M', time.strptime(h.clock, '%Y-%m-%d %H:%M:%S'))
            }
            h_in_data.append(h1)
        for h in h_out:
            v = h.value.strip('Mbits')
            h2 = {
                'value': float(v.encode()),
                'clock': time.strftime('%H:%M', time.strptime(h.clock, '%Y-%m-%d %H:%M:%S'))
            }
            h_out_data.append(h2)
    if h_in_data != [] or h_out_data != []:
        return render(request, 'triggers/line_history.html', {'item_description': item_description,
                                                              'h_data_in': json.dumps(h_in_data),
                                                              'h_data_out': json.dumps(h_out_data)})
    else:
        return render(request, 'triggers/error.html')


# 获取线路状态历史数据（专线及互联网）
def line_status(request, item_description):
    global h_pingsec, h_pingloss
    times = request.GET.get('hours')
    if times:
        t = int(times) * 60
    else:
        t = 0
    num = 60
    if t != 0:
        num = t
    h_pingsec_data = []
    h_pingloss_data = []
    item = Item.objects.filter(hostname=item_description)
    if item:
        for i in item:
            if i.itemname.__contains__('sec'):
                h_pingsec = History.objects.filter(itemid=i.itemid).order_by('-clock')[:num]
            if i.itemname.__contains__('loss'):
                h_pingloss = History.objects.filter(itemid=i.itemid).order_by('-clock')[:num]
        for h in h_pingsec:
            h1 = {
                'value': float(h.value.encode()),
                'clock': time.strftime('%H:%M', time.strptime(h.clock, '%Y-%m-%d %H:%M:%S'))
            }
            h_pingsec_data.append(h1)

        for h in h_pingloss:
            h2 = {
                'value': float(h.value.encode()),
                'clock': time.strftime('%H:%M', time.strptime(h.clock, '%Y-%m-%d %H:%M:%S'))
            }
            h_pingloss_data.append(h2)
    if h_pingloss_data != [] or h_pingsec_data != []:
        return render(request, 'triggers/line_status.html', {'item_description': item_description,
                                                             'h_pingsec_data': json.dumps(h_pingsec_data),
                                                             'h_pingloss_data': json.dumps(h_pingloss_data)})
    else:
        return render(request, 'triggers/error.html')


# 线路历史数据删除
def clear_history(request):
    h_days = InitPara.objects.get(id=1).history_days
    yesterday = date.today() - datetime.timedelta(h_days)
    time_yesterday = yesterday.strftime('%Y-%m-%d %H:%M:%S')
    cursor = connection.cursor()
    cursor.execute('delete from triggers_history WHERE clock < ' + '\'' + time_yesterday + '\'')
    transaction.commit()


# 获取指定目录下的文件列表
def getFileList(path):
    p = str(path)
    if p == "":
        return []
    lists = os.listdir(p)
    files = []
    for x in lists:
        if os.path.isfile(p + '/' + x):
            files.append(x)
    return files


# localpath目录下文件上传至ftp server的targetpath目录下
def uploadFile(localpath, ip, username, password, targetpath):
    # 上传至ftp server
    result = {
        'num': 0,
        'status': 0
    }
    status = 0
    files = getFileList(localpath)
    result['num'] = files.__len__()
    if files != []:
        fn = ftplib.FTP()
        fn.set_debuglevel(0)
        fn.connect(ip)
        try:
            fn.login(username, password)
            try:
                fn.cwd(targetpath)
            except ftplib.error_perm:
                fn.mkd(targetpath)
                fn.cwd(targetpath)
            for f in files:
                fn.storbinary('STOR %s' % f, open(f, 'r'))
                print f + " upload success."
        except ftplib.error_perm:
            print "Login " + ip + " failed."
            result['status'] = 1
            # status = 1
        fn.quit()
    else:
        print localpath + " has no files!"
        result['status'] = 1
    # print result
    return result


def compareFiles(file_old, file_new):
    str_old = []
    str_new = []
    status = 0

    if not cmp(file_old, file_new):
        status = 1

    f_old = open(file_old)
    f_new = open(file_new)
    f_old_lines = f_old.readlines()
    f_new_lines = f_new.readlines()
    f_old.close()
    f_new.close()

    line_num_old = 0
    line_num_new = 0
    for line in f_old_lines:
        line_num_old += 1
        if line not in f_new_lines:
            str_old.append(line_num_old.__str__() + ':' + line)
    for line in f_new_lines:
        line_num_new += 1
        if line not in f_old_lines:
            str_new.append(line_num_new.__str__() + ':' + line)

    result = {
        'status': status,
        'str_old': str_old,
        'str_new': str_new
    }
    return result


# 网络设备配置备份
def backup_netdevice(request):
    devices = NetDevices.objects.all()
    ftpserver = FtpServer.objects.get(id=1)
    today = date.today().strftime('%Y-%m-%d')
    work_path = os.path.join(BASE_DIR + '/logs/backup')
    if not os.path.exists(work_path):
        os.mkdir(work_path, 0755)
    target_path = work_path + '/' + today
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    os.chdir(target_path)
    delay_sec = 2
    enter_key = "\r\n"
    for host in devices:
        if host.type.lower() == 'cisco':
            charset = [' --More-- ', '\x08        ', '\x08']
        if host.type.lower() == 'h3c':
            charset = ['  ---- More ----', '\x1b[16D                ', '\x1b[16D']
        file_local_name = host.ipaddress + "-" + host.devicename + ".log"
        tn = telnetlib.Telnet()
        tn.set_debuglevel(1)
        # 判断设备telnet是否可达，如果不可达输出telnet失败，并继续telnet下一台设备
        try:
            tn.open(host.ipaddress, ftpserver.port)
        except Exception as e:
            print "telnet " + host.ipaddress + " failed."
            print e
            continue
        # 传入用户名和密码
        tn.read_until("Username", 10)
        tn.write(host.username.encode('utf-8') + enter_key.encode('utf-8'))
        tn.read_until("Password", 10)
        tn.write(host.password.encode('utf-8') + enter_key.encode('utf-8'))
        # 延时，等待设备返回telnet结果
        if host.type.lower() == 'pix' or host.type.lower() == 'asa':
            tn.read_until(">", 10)
            tn.write('en'.encode('utf-8') + enter_key.encode('utf-8'))
            tn.read_until("Password", 10)
            tn.write('jlktv4'.encode('utf-8') + enter_key.encode('utf-8'))
        time.sleep(delay_sec)
        # 将设备telnet返回的结果存入变量res
        res = tn.read_very_eager()
        # 判断是否登陆成功，如果失败输出登陆失败，并继续登陆下一台设备
        if res.find(host.tag) == -1:
            print 'Login ' + host.ipaddress + ' failed.'
            continue
        else:
            print 'Login ' + host.ipaddress + ' access.'
        # 在设备中执行备份命令
        tn.write(host.command.encode('utf-8') + enter_key.encode('utf-8'))
        time.sleep(delay_sec)
        # 当有？时回车
        temp = ''

        while 1:
            res = tn.read_very_eager()
            res_new = res
            for c in range(0, len(charset), 1):
                res_new = res_new.replace(charset[c], '')
            temp += res_new
            if 'More' in res:
                tn.write(' '.encode('utf-8'))
            elif res != '' and host.tag in res:
                break
        # 延时，等待设备返回telnet结果
        time.sleep(delay_sec)
        file_local = open(file_local_name, 'w')
        file_local.write(temp)
        file_local.flush()
        tn.close()
        file_local.close()
        NetDevices.objects.filter(ipaddress=host.ipaddress).update(file_name=file_local_name, backup_status=0)
        print file_local_name + " created access."
    upload = uploadFile(target_path, ftpserver.ipaddress, ftpserver.username, ftpserver.password, today)

    # print upload
    if upload['status'] == 1:
        FtpServer.objects.filter(id=1).update(status=1, file_num=0)
    if upload['status'] == 0:
        print upload['num']
        FtpServer.objects.filter(id=1).update(status=0, file_num=upload['num'])

        # return render(request, 'triggers/backup.html')


# 网络配置文件变更状态检查
def file_change_status(request):
    today = date.today().strftime('%Y-%m-%d')
    yesterday = (date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    today_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + today
    yesterday_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + yesterday
    today_files = NetDevices.objects.all()
    for file in today_files:
        today_file = today_path + '/' + file.file_name
        yesterday_file = yesterday_path + '/' + file.file_name
        if not os.path.exists(yesterday_file):
            print yesterday_file + " is not exit."
        elif cmp(today_file, yesterday_file):
            NetDevices.objects.filter(ipaddress=file.ipaddress).update(change_status=0)
            print file.file_name + " is not changed."
        else:
            NetDevices.objects.filter(ipaddress=file.ipaddress).update(change_status=1)
            print file.file_name + " is changed."


# 网络配置文件备份状态检查
def file_backup_status(request):
    today = date.today().strftime('%Y-%m-%d')
    today_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + today
    if not os.path.exists(today_path):
        NetDevices.objects.all().update(backup_status=1)
    else:
        today_files = NetDevices.objects.all()
        for file in today_files:
            today_file = today_path + '/' + file.file_name
            if not os.path.exists(today_file):
                NetDevices.objects.filter(ipaddress=file.ipaddress).update(backup_status=1)


# 文件审计
def fileaudit(request, device_name):
    print device_name
    today = date.today().strftime('%Y-%m-%d')
    yesterday = (date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    today_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + today
    yesterday_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + yesterday

    if not os.path.exists(today_path):
        print today_path + " is not exit."
    if not os.path.exists(yesterday_path):
        print yesterday_path + " is not exit."
    # today_files = getFileList(today_path)
    today_files = NetDevices.objects.filter(devicename=device_name)
    # print today_files
    result = []
    for file in today_files:
        print file.file_name
        new_file = today_path + '/' + file.file_name
        old_file = yesterday_path + '/' + file.file_name
        if os.path.exists(old_file):
            compare_result = compareFiles(old_file, new_file)
            file_compare = {
                'file': file.file_name,
                'status': compare_result['status'],
                'str_old': compare_result['str_old'],
                'str_new': compare_result['str_new']
            }
            result.append(file_compare)
        else:
            file_compare = {
                'file': file.file_name,
                'status': 1,
                'str_old': [u'不存在'],
                'str_new': [u'正常']
            }
            result.append(file_compare)

    return render(request, 'triggers/compare.html', {'result': result})


# netmanager
def netmanager(request):
    return render(request, 'triggers/netmanager.html')


# 获取设备备份状态
def netmanager_status(request):
    # zhuanxian status
    # file_backup_status()
    today = date.today().strftime('%Y-%m-%d')
    today_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + today
    if not os.path.exists(today_path):
        NetDevices.objects.all().update(backup_status=1)
    else:
        today_files = NetDevices.objects.all()
        for file in today_files:
            today_file = today_path + '/' + file.file_name
            if not os.path.exists(today_file):
                NetDevices.objects.filter(ipaddress=file.ipaddress).update(backup_status=1)
    device_status = []
    device_host = NetDevices.objects.all()

    for device in device_host:
        d = {
            "devicename": device.devicename,
            # "description": device.devicename,
            "change_status": device.change_status,
            "backup_status": device.backup_status
        }
        device_status.append(d)
    # print device_status
    return HttpResponse(json.dumps(device_status), content_type='application/json')


# 获取FTP Server备份状态
def ftp_status(request):
    f = FtpServer.objects.get(id=1)
    f_status = {
        'status': f.status,
        'file_num': f.file_num
    }
    return HttpResponse(json.dumps(f_status), content_type='application/json')


# login
def file_view(request):
    #username = request.POST.get('username')
    #password = request.POST.get('password')
    #user =
    url = request.GET.get('next')
    #print username, password

    print url
    return HttpResponseRedirect(url)
    #user = authenticate(username=username, password=password)
    #print user
    # print request.path
    #if user is not None:
    #    if user.is_active:
    #        login(request, user)
    #        return HttpResponse(url)
    #    else:
    #        return render(request, 'triggers/error.html')
    #else:
    #    return render(request, 'triggers/login.html', {'url': url})


# 获取配置文件内容
#@permission_required('triggers.NetDevices', login_url='/trigger/netmanger/file_view')
@login_required(login_url='/trigger/login')
def file_content(request, device_name):
    user = User.objects.get(username='100273')
    print user.has_perm('triggers.NetDevices')
    today = date.today().strftime('%Y-%m-%d')
    today_path = os.path.join(BASE_DIR + '/logs/backup') + '/' + today

    if not os.path.exists(today_path):
        print today_path + " is not exit."

    filename = NetDevices.objects.get(devicename=device_name)
    today_file = today_path + '/' + filename.file_name

    file = open(today_file)
    file_lines = file.readlines()
    file.close()
    return render(request, 'triggers/file_content.html', {'content': file_lines})


#######以下为测试内容########
# backup
def backup(devices, type, device_username, device_password, delay_sec, enter_key):
    if type == 'cisco':
        command = "show running-config"
        tag = '#'
        charset = [' --More-- ', '\x08        ', '\x08']
    if type == 'h3c':
        command = "dis curr"
        tag = '>'
        charset = ['  ---- More ----', '\x1b[16D                ', '\x1b[16D']
    # 使用telnet登陆设备
    for a in range(0, len(devices), 1):
        if not os.path.exists(devices[a] + "-old.log"):
            f_name_old = devices[a] + "-old.log"
            f_old = open(f_name_old, 'w')
            f_old.close()

        f_name_new = devices[a] + "-new.log"
        f_new = open(f_name_new, 'w')
        tn = telnetlib.Telnet()
        # 设置telnet debug级别为1，对程序运行过程进行记录
        tn.set_debuglevel(1)
        print "----------------------新的Telnet开始---------------------------"
        print "telnet " + devices[a]
        # 判断设备telnet是否可达，如果不可达输出telnet失败，并继续telnet下一台设备
        try:
            tn.open(devices[a], 23)
        except Exception as e:
            print "telnet " + devices[a] + " failed."
            print e
            continue
        # 传入用户名和密码
        tn.read_until("Username", 10)
        tn.write(device_username.encode('utf-8') + enter_key.encode('utf-8'))
        tn.read_until("Password", 10)
        tn.write(device_password.encode('utf-8') + enter_key.encode('utf-8'))
        # 延时，等待设备返回telnet结果
        time.sleep(delay_sec)
        # 将设备telnet返回的结果存入变量res
        res = tn.read_very_eager().replace('\r\n', '').replace(': ', '')

        # 判断是否登陆成功，如果失败输出登陆失败，并继续登陆下一台设备
        if res.find(tag) == -1:
            print 'login ' + devices[a] + ' failed.'
            continue
        else:
            print 'login ' + devices[a] + ' access.'
        # 打印当前返回的telnet结果
        print "1" + res
        # 将换行写入缓存
        # f.write(enter_key)
        # 将设备ip地址和telnet返回的内容写入缓存
        f_new.write("IP:" + devices[a] + enter_key + res)
        # 在设备中执行备份命令
        tn.write(command.encode('utf-8') + enter_key.encode('utf-8'))
        time.sleep(1)
        # 当有？时回车
        temp = ''
        while 1:
            res = tn.read_very_eager()
            res_new = res
            for c in range(0, len(charset), 1):
                res_new = res_new.replace(charset[c], '')
            temp += res_new
            if 'More' in res:
                tn.write(' '.encode('utf-8'))
            elif res != '' and tag in res:
                break
        # 延时，等待设备返回telnet结果
        time.sleep(delay_sec)
        # 将执行备份命令后返回的内容写入缓存
        f_new.write(temp + enter_key)
        # 将缓存中的数据写入创建的日志文件中
        f_new.flush()
        tn.close()
        print "-------------------- Telnet 结束-------------------------------"
        # 关闭telnet返回结果的日志文件
        f_new.close()


# diff
def compare(request):
    # 延时2秒
    delay_sec = 2
    # 回车换行符
    enter_key = u'\r\n'
    devices = ['10.68.253.5']
    type = 'h3c'

    dirs = os.path.join(BASE_DIR, 'triggers\static\\')
    os.chdir(dirs)
    backup(devices, type, 'admin', 'jlktv4', delay_sec, enter_key)
    result = []
    for a in range(0, len(devices), 1):
        file_old = devices[a] + "-old.log"
        file_new = devices[a] + "-new.log"
        # 
        if open(file_old).read() == '':
            open(file_old, 'w').write(open(file_new).read())

        file_old_path = dirs + file_old
        file_new_path = dirs + file_new
        out_old = dirs + 'out_old.txt'
        out_new = dirs + 'out_new.txt'

        status = 0

        if not cmp(file_old_path, file_new_path):
            status = 1

        f1 = open(file_old_path)
        f2 = open(file_new_path)
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
        f1.close()
        f2.close()

        f1_out = open(out_old, 'w')
        f2_out = open(out_new, 'w')
        line_num1 = 0
        for i in f1_lines:
            line_num1 += 1
            if i not in f2_lines:
                f1_out.write(line_num1.__str__() + ':' + i)
        line_num2 = 0
        for i in f2_lines:
            line_num2 += 1
            if i not in f1_lines:
                f2_out.write(line_num2.__str__() + ':' + i)
        f1_out.close()
        f2_out.close()

        outfile_old = open(out_old, 'r')
        outfile_new = open(out_new, 'r')
        str_old = []
        str_new = []
        for i in outfile_old:
            str_old.append(i.strip('\n'))
        for i in outfile_new:
            str_new.append(i.strip('\n'))

        result_file = {
            'file_old': file_old,
            'file_new': file_new,
            'status': status,
            'str_old': str_old,
            'str_new': str_new
        }
        result.append(result_file)
    return render(request, 'triggers/compare.html', {'result': result})


def ajax(request):
    return render(request, 'triggers/ajax.html')


def add(request, a, b):
    print a, b
    if request.is_ajax():
        ajax_string = 'ajax request: '
    else:
        ajax_string = 'not ajax request: '
    c = int(a) + int(b)
    r = HttpResponse(ajax_string + str(c))
    print r
    return r


def add1(request):
    if request.is_ajax():
        ajax_string = 'ajax request: '
    else:
        ajax_string = 'not ajax request: '
    a = request.GET['a1']
    b = request.GET['b1']
    a = int(a)
    b = int(b)
    return HttpResponse(ajax_string + str(a + b))


def ajax_list(request):
    a = range(10)
    print a
    return HttpResponse(json.dumps(a), content_type='application/json')


def ajax_dict(request):
    name_dict = [{'twz': 'Love python and Django', 'zqxt': 'I am teaching Django'},
                 {'twz': 'Love python and Django2', 'zqxt': 'I am teaching Django2'}]
    return HttpResponse(json.dumps(name_dict), content_type='application/json')


def getweb(request):
    parameter = Parameters.objects.get(serverip='10.68.7.104')

    data = json.dumps(
        dict(jsonrpc="2.0",
             method="httptest.get",
             params={
                 "output": "extend",
                 "httptestids ": "1",
             },
             auth=parameter.authid,
             id=1
             )
    )
    web_zabbix = request_zabbix(parameter.url, data, parameter.header_type, parameter.header_json)
    print web_zabbix
    return u'ok'
