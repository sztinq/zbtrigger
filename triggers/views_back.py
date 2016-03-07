from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.template import RequestContext, loader, Context, Template
from datetime import datetime
from triggers.models import Hosts, Parameters, Triggers, Problems

import json
import urllib2
import time
import operator


# Create your views here.

# def test(request) :
#    return render(request, 'triggers/test.html', {'current_time': datetime.now()})
def home(request):
    parameter_list = Parameters.objects.all()
    parameter = Parameters.objects.get(serverip='10.1.18.30')
    trigger_list = []
    data_host = json.dumps(
    dict(jsonrpc="2.0",
             method="host.get",
             params={
                 "output": ["hostid", "name"],
             },
             filter={"status": 0},
             auth=parameter.authid,
             id=1
             )
    )
    request_host = urllib2.Request(parameter.url, data_host)
    request_host.add_header(parameter.header_type, parameter.header_json)
    result_host = urllib2.urlopen(request_host)
    response_host = json.loads(result_host.read())
    result_host.close()
    for host in response_host['result']:
        data_trigger = json.dumps(
            dict(jsonrpc="2.0",
                 method="trigger.get",
                 params={
                     "output": [
                         "triggerid",
                         "description",
                         "lastchange"
                     ],
                     "filter": {
                         "value": 1,
                         "status": 0
                     },
                     "hostids": {
                         "hostid": host['hostid']
                     },
                 },
                 auth=parameter.authid,
                 id=1
                 )
        )
        request_trigger = urllib2.Request(parameter.url, data_trigger)
        request_trigger.add_header(parameter.header_type, parameter.header_json)
        result_trigger = urllib2.urlopen(request_trigger)
        response_trigger = json.loads(result_trigger.read())
        result_trigger.close()
        for trigger in response_trigger['result']:
            timearray = time.localtime(float(trigger['lastchange']))
            trigger['lastchange'] = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
            trigger = dict(host.items() + trigger.items())
            print trigger
            trigger_list.append(trigger)
    trigger_sorted = sorted(trigger_list, key=lambda trigger_list: trigger_list['lastchange'])
    # print trigger_sorted
    return render(request, 'triggers/home.html', {'parameter_list': parameter_list, 'trigger_list': trigger_sorted})



def index(request):
    return render(request, 'triggers/index.html')


def parameter_init(request, server_ip):
    #parameter = Parameters.objects.get(serverip='10.1.18.30')
    print server_ip
    parameter = get_object_or_404(Parameters, serverip=server_ip)
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
    request_parameter = urllib2.Request(parameter.url, data)
    request_parameter.add_header(parameter.header_type, parameter.header_json)
    result_parameter = urllib2.urlopen(request_parameter)
    response_parameter = json.loads(result_parameter.read())
    result_parameter.close()
    print response_parameter['result']
    parameter.authid = response_parameter['result']
    parameter.save()
    return render(request, 'triggers/parameter.html')