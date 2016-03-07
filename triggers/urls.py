from django.conf.urls import url
from . import views
from zbtrigger import settings
# from zbtrigger.settings import STATICFILES_DIRS
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^netmanager/file_view/$', views.file_view, name='file_view'),

    url(r'^parameter_init/$', views.parameter_init, name='parameter_init'),
    url(r'^item_init/$', views.item_init, name='item_init'),
    url(r'^internet_lastvalue/$', views.internet_lastvalue, name='internet_lastvalue'),
    url(r'^zhuanxian_lastvalue/$', views.zhuanxian_lastvalue, name='zhuanxian_lastvalue'),
    url(r'^zhuanxian_status/$', views.zhuanxian_status, name='zhuanxian_status'),
    url(r'^device_value/$', views.device_value, name='device_value'),
    url(r'^video_status/$', views.video_status, name='video_status'),
    url(r'^video/$', views.video, name='video'),
    url(r'^line_history/(?P<item_description>.+)/$', views.line_history, name='line_history'),
    url(r'^line_status/(?P<item_description>.+)/$', views.line_status, name='line_status'),
    url(r'^host_list/(?P<server_name>.+)/$', views.host_list, name='host_list'),
    url(r'^zhuanxian_detail/(?P<name>.+)/$', views.zhuanxian_detail, name='zhuanxian_detail'),
    url(r'^trigger_list/(?P<server>.+)/$', views.trigger_list, name='trigger_list'),
    url(r'^backup/$', views.backup_netdevice, name='backup_netdevice'),
    url(r'^audit/$', views.fileaudit, name='fileaudit'),
    url(r'^netmanager/$', views.netmanager, name='netmanager'),
    url(r'^netmanager_status/$', views.netmanager_status, name='netmanager_status'),
    url(r'^file_status/$', views.file_change_status, name='file_change_status'),
    url(r'^ftp_status/$', views.ftp_status, name='ftp_status'),
    # url(r'^netmanager/(?P<device_name>.+)/$', views.fileaudit, name='fileaudit'),
    url(r'^netmanager/(?P<device_name>.+)/$', views.file_content, name='file_content'),
    url(r'^error/$', views.login_error, name='login_error'),

    # test url
    url(r'^compare/$', views.compare, name='compare'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^add/(?P<a>(\d+))/(?P<b>(\d+))/$', views.add, name='add'),
    url(r'^add1/$', views.add1, name='add1'),
    url(r'^ajax_list/$', views.ajax_list, name='ajax_list'),
    url(r'^ajax_dict/$', views.ajax_dict, name='ajax_dict'),
    url(r'^web/$', views.getweb, name='getweb'),
]
