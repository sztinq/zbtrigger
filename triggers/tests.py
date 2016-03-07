from django.test import TestCase

# Create your tests here.
p = [{u'interfaceid': u'1', u'hostid': u'10084', u'ip': u'10.1.18.30'}]
for i in p:
    print i['ip']


import os, sys
sys.path.append('.')
def application(environ, start_response):
    status = '200 OK'
    output = 'See you at terokarvinen.com!\n'
    response_headers = [('Content-type', 'text/plain'),
        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]