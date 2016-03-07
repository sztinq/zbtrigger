# coding=utf-8
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.template import RequestContext, loader, Context, Template
from datetime import datetime
from triggers.models import Hosts, Parameters, TriggerWarrning, ZhuanXian
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import json
import urllib2
import time
import threading
import operator

### 通过zabbix server api 返回结果集（数组字典）
def request_zabbix(url, data, header_type, header_json):
    request_http = urllib2.Request(url, data)
    request_http.add_header(header_type, header_json)
    result_data = urllib2.urlopen(request_http)
    response_data = json.loads(result_data.read())
    result_data.close()
    print response_data
    return response_data['result']
### 触发器页面
def home(request):
    parameter_list = Parameters.objects.all()
    parameter = Parameters.objects.get(serverip='10.1.18.30')
    trigger_list = []
    data_host = json.dumps(
        dict(jsonrpc="2.0",
             method="host.get",
             params={
                 "output": ["hostid", "name"],
                 "filter": {"status": 0},
             },
             auth=parameter.authid,
             id=1
             )
    )
    host_zabbix = request_zabbix(parameter.url, data_host, parameter.header_type, parameter.header_json)

    for host in host_zabbix:
        #print host
        data_trigger = json.dumps(
            dict(jsonrpc="2.0",
                 method="trigger.get",
                 params={
                     "output": ["triggerid", "description", "lastchange"],
                     "filter": {"value": 1, "status": 0},
                     "hostids": {"hostid": host['hostid']},
                 },
                 auth=parameter.authid,
                 id=1
                 )
        )
        trigger_zabbix = request_zabbix(parameter.url, data_trigger, parameter.header_type, parameter.header_json)

        for trigger in trigger_zabbix:
            #print trigger
            timearray = time.localtime(float(trigger['lastchange']))
            trigger['lastchange'] = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
            trigger = dict(host.items() + trigger.items())
            #print trigger
            #print trigger['triggerid']
            #print parameter.company
            h = Hosts.objects.get(hostid=trigger['hostid'])
            if not TriggerWarrning.objects.filter(triggerid=trigger['triggerid']):
                print trigger['triggerid'] + " is not exist."
                t1 = TriggerWarrning(hosts_id=h.id, company=parameter.company, hostname=trigger['name'],
                                     triggerid=trigger['triggerid'], hostid=trigger['hostid'],
                                     description=trigger['description'], lastchange=trigger['lastchange']
                                     )
                t1.save()
            trigger_list.append(trigger)
    trigger_sorted = sorted(trigger_list, key=lambda trigger_list: trigger_list['lastchange'])
    # print trigger_sorted
    #return render(request, 'triggers/home.html', {'parameter_list': parameter_list, 'trigger_list': trigger_sorted})
    return render(request, 'triggers/home.html', {'parameter_list': parameter_list, 'trigger_list': TriggerWarrning.objects.all().order_by('lastchange')})

### 首页
def index(request):
    index_list = []
    status = 0
    h_num = 0
    p_num = 0
    parameter_list = Parameters.objects.all()
    for p in parameter_list:
        host_list = {"id": p.id,
                     "servername": p.company,
                     "serverip": p.serverip,
                     "hostnum": Hosts.objects.filter(company=p.company).count(),
                     "problemnum": TriggerWarrning.objects.filter(company=p.company).count()
                     }
        h_num += int(host_list['hostnum'])
        p_num += int(host_list['problemnum'])
        index_list.append(host_list)
        for i in index_list:
            if i['problemnum'] != 0:
                status = 1
    return render(request, 'triggers/index.html', {'index_list': index_list, 'h_num': h_num, 'p_num': p_num, 'status': status})

###Trigger_list
def trigger_list(request, server_trigger):
    trigger = TriggerWarrning.objects.filter(company=server_trigger).order_by('lastchange')
    return render(request, 'triggers/trigger.html', {'trigger_list': trigger, 'servername': server_trigger},
                  context_instance=RequestContext(request))

###Host_list
def host_list(request, server_host):
    host = Hosts.objects.filter(company=server_host).order_by('hostip')
    return render_to_response('triggers/host.html', {'host_list': host, 'servername': server_host},
                              context_instance=RequestContext(request))
### 初始化zabbix服务器参数
def parameter_init(request):
    p_server = Parameters.objects.all()
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
        parameter.save()
        print parameter.serverip, parameter.authid
    return render(request, 'triggers/parameter_init.html')


###监控主机表初始化及更新
def host_init(request):
    p_server = Parameters.objects.all()
    for parameter in p_server:
        #Hosts.objects.filter(company=parameter.company).delete()
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
        print host_zabbix
        Hosts.objects.filter(company=parameter.company).delete()
        for host in host_zabbix:
            #print host['hostid']
            data_hostinterface = json.dumps(
                dict(jsonrpc="2.0",
                    method="hostinterface.get",
                    params={
                        "output": ["hostid", "ip"],
                        "hostids": {"hostid": host['hostid']},
                    },
                    auth=parameter.authid,
                    id=1
                )
            )
            host_ip = request_zabbix(parameter.url, data_hostinterface, parameter.header_type, parameter.header_json)
            #print host_ip
            for h in host_ip:
                ip = h['ip']
            h1 = Hosts(company=parameter.company, hostid=host['hostid'], hostname=host['name'], hostip=ip,
                       status=host['status'])
            #print h1.company, h1.hostname, h1.hostip
            h1.save()

    """
    print server_ip
    parameter = get_object_or_404(Parameters, serverip=server_ip)
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
    print host_zabbix

    Hosts.objects.filter(company=parameter.company).delete()
    for host in host_zabbix:
        print host['hostid']
        data_hostinterface = json.dumps(
            dict(jsonrpc="2.0",
                 method="hostinterface.get",
                 params={
                     "output": ["hostid", "ip"],
                     "hostids": {"hostid": host['hostid']},
                 },
                 auth=parameter.authid,
                 id=1
                 )
        )
        host_ip = request_zabbix(parameter.url, data_hostinterface, parameter.header_type, parameter.header_json)
        for h in host_ip:
            ip = h['ip']
        h1 = Hosts(company=parameter.company, hostid=host['hostid'], hostname=host['name'], hostip=ip,
                       status=host['status'])
        h1.save()
        #if not Hosts.objects.filter(hostid=host['hostid']):
        #    print host['hostid'] + " is not exist."
        #    h1 = Hosts(company=parameter.company, hostid=host['hostid'], hostname=host['name'], hostip=ip,
        #               status=host['status'])
        #    h1.save()

    for host in Hosts.objects.all():
        # print host.hostid
        data_host = json.dumps(
            dict(jsonrpc="2.0",
                 method="host.exists",
                 params={"hostid": [host.hostid]},
                 auth=parameter.authid,
                 id=1
                 )
        )
        host_exist = request_zabbix(parameter.url, data_host, parameter.header_type, parameter.header_json)
        if not host_exist:
            print host.hostid + " is not in zabbix"
            host.delete()
    """
    #return HttpResponse("Hosts init OK!")
    #return render(request, 'triggers/host_init.html')
### Host_Thread
def host_thread(request):
    start = time.time()
    p_server = Parameters.objects.all()
    host1 = []
    Hosts.objects.all().delete()

    def request_thread(url, data, header_type, header_json, hostid, company, hostname, status):
        re = request_zabbix(url, data, header_type, header_json)
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
        Hosts.objects.filter(company=parameter.company).delete()
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
        print host_zabbix
        Hosts.objects.filter(company=parameter.company).delete()
        t = []
        for host in host_zabbix:
            #print host['hostid']
            data_hostinterface = json.dumps(
                dict(jsonrpc="2.0",
                    method="hostinterface.get",
                    params={
                        "output": ["hostid", "ip"],
                        "hostids": {"hostid": host['hostid']},
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
            h1 = Hosts(company=h['company'], hostid=h['hostid'], hostname=h['hostname'], hostip=h['hostip'],
                       status=h['status'])
            h1.save()
    end = time.time()
    print end-start
    #return render(request, 'triggers/host_init.html')

### TriggerWaning init
def trigger_init(request):
    #p_server = Parameters.objects.all()
    TriggerWarrning.objects.all().delete()
    p_host = Hosts.objects.all()
    start = time.time()
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
        trigger_zabbix = request_zabbix(parameter.url, data_trigger, parameter.header_type, parameter.header_json)
        #TriggerWarrning.objects.filter(company=parameter.company).delete()
        if trigger_zabbix:
            print trigger_zabbix
            for trigger in trigger_zabbix:
                #print trigger
                timearray = time.localtime(float(trigger['lastchange']))
                trigger['lastchange'] = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
                t1 = TriggerWarrning(hosts_id=host.id, company=parameter.company, hostname=host.hostname,
                                     triggerid=trigger['triggerid'], hostid=host.hostid,
                                     description=trigger['description'], lastchange=trigger['lastchange']
                                     )
                t1.save()
    end = time.time()
    print end-start
    #return render(request, 'triggers/trigger_init.html')

### trigger thread
def trigger_thread(request):
    start = time.time()
    TriggerWarrning.objects.all().delete()
    p_host = Hosts.objects.all()
    t = []
    trigger1 = []
    def request_thread(url, data, header_type, header_json, host_id, hostid, company, hostname, hostip):
        re = request_zabbix(url, data, header_type, header_json)
        if re != []:
            print re
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
    print end-start
    #return render(request, 'triggers/trigger_init.html')

### zhuanxian status

def zhuanxian(request):
    problem_num = 0
    z_problem = []
    z_host = ZhuanXian.objects.all()
    for host in z_host:
        trigger = TriggerWarrning.objects.filter(hostip=host.hostip)
        if trigger:
                problem_num += 1
                for t in trigger:
                    h1 = {
                        "id": host.id,
                        "hostid": t.hostid,
                        "hostname": t.hostname,
                        "hostip": t.hostip,
                        "description": t.description,
                        "lastchange": t.lastchange
                    }
                    z_problem.append(h1)
                host.description = u'故障'
        else:
            host.description = u'正常'
        host.save()
    z_total = z_host.count()
    z_num ={
        "total": z_total,
        "problem_num": problem_num
    }
    return render_to_response('triggers/zhuanxian.html', {'z_status': z_host, 'z_problem': z_problem, 'z_num': z_num },
                              context_instance=RequestContext(request))

def zhuanxian_detail(request, h_ip):
    z_detail = ZhuanXian.objects.get(hostip=h_ip)
    return render(request, 'triggers/zhuanxian_detail.html', {'z_tail': z_detail})
