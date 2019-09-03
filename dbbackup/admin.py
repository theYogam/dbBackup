from django.contrib import admin
from dbbackup.models import JobConfig, DestinationServer, Backup


class DestinationServerAdmin(admin.ModelAdmin):
    list_display = ('ip', 'username', 'password')
    fields = ('ip', 'username', 'password')
    # prepopulated_fields = {"slug": ("ip",)}
    # fieldsets = (
    #     (None, {
    #         'fields': ('ip',)
    #     }),
    #     ('credentials', {
    #         # 'class': ('collapse',),
    #         'fields': ('username', 'password')
    #     })
    # )


class JobConfigAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'db_type', 'db_name', 'db_username', 'db_password', 'run_every')
    fields = ('hostname', 'db_type', 'db_name', 'db_username', 'db_password', 'run_every')
    # prepopulated_fields = {"slug": ("job_name",)}
    # fieldsets = (
    #     (None, {
    #         'fields': ('hostname', 'db_type', 'db_name')
    #     }),
    #     ('credentials', {
    #         # 'class': ('collapse',),
    #         'fields': ('db_username', 'db_password')
    #     })
    # )


class BackupAdmin(admin.ModelAdmin):
    list_display = ('job_config', 'start_time', 'status')
    fields = ('job_config', 'start_time', 'status')
    # fieldsets = (
    #     (None, {
    #         # 'class': ('collapse',),
    #         'fields': ('job_config',)
    #     }),
    #     ('runtime_infos', {
    #         'class': ('wide', 'extrapretty'),
    #         'fields': ('start_time', 'status',)
    #     })
    #
    # )


admin.site.register(DestinationServer, DestinationServerAdmin)
admin.site.register(JobConfig, JobConfigAdmin)
admin.site.register(Backup, BackupAdmin)

