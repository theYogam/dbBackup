from django.contrib import admin
from dbbackup.models import JobConfig, DestinationServer, Backup


class DestinationServerAdmin(admin.ModelAdmin):
    """
    comment
    """
    list_display = ('ip', 'username', 'password')
    fields = ('ip', 'username', 'password')


class JobConfigAdmin(admin.ModelAdmin):
    """
    comment
    """
    list_display = ('hostname', 'db_type', 'db_name', 'db_username', 'db_password', 'run_every')
    fields = ('hostname', 'db_type', 'db_name', 'db_username', 'db_password', 'run_every')


class BackupAdmin(admin.ModelAdmin):
    """
    comment
    """
    list_display = ('job_config', 'status', 'relative_file_path', 'file_size', 'file_size_hr', 'error_messages')
    fields = ('job_config', 'status', 'relative_file_path', 'file_size', 'file_size_hr', 'error_messages')


admin.site.register(DestinationServer, DestinationServerAdmin)
admin.site.register(JobConfig, JobConfigAdmin)
admin.site.register(Backup, BackupAdmin)

