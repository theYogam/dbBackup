from django.conf.urls import patterns, include, url
from dbbackup.views import ChangeJobConfig, Home, JobConfigList, BackupList, test_db_connection,\
    test_destination_server_connection  # , JobConfigView
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^jobConfigurationList$', JobConfigList.as_view(), name='jobconfig_list'),
    url(r'^jobConfig$', ChangeJobConfig.as_view(), name='change_jobconfig'),
    url(r'^jobConfig/(?P<object_id>[-\w]+)$', ChangeJobConfig.as_view(), name='change_jobconfig'),
    url(r'^backupList$', BackupList.as_view(), name='backup_list'),
    url(r'^backupList/(?P<object_id>[-\w]+)$', BackupList.as_view(), name='backup_list'),
    url(r'^dbServerValidation$', test_db_connection, name='test_db_connection'),
    url(r'^destinationServerValidation$', test_destination_server_connection, name='test_destination_server_connection'),

)


