from dbbackup.models import DestinationServer, JobConfig, Backup, DB_TYPES, RUN_EVERY
from django.forms import ModelForm
from django import forms


# class BackupForm(ModelForm):
#     class Meta:
#         model = Backup
#         exclude = '__all__'


class DestinationServerForm(ModelForm):
    class Meta:
        model = DestinationServer
        fields = '__all__'


class JobConfigForm(forms.Form):
    hostname = forms.IPAddressField(error_messages={'required': 'Please enter the hostname'},
                                    required=True, max_length=16)
    # widget=forms.TextInput(
    # attrs={'class': 'form-control', 'placeholder': '192.168.0.25'}))
    db_type = forms.ChoiceField(error_messages={'required': 'Please enter the database type'},
                                required=True, choices=DB_TYPES)
    # , attrs={'class': 'form-control'}))
    # , 'placeholder': 'MySQL'
    db_name = forms.CharField(error_messages={'required': 'Please enter the database name'},
                              required=True, max_length=100)
    # widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': 'umbrella'}))
    db_username = forms.CharField(error_messages={'required': 'Please enter the database username'},
                                  required=True, max_length=100)
    # , widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': 'theYogam'}))
    # db_password = forms.PasswordInput(attrs={'type': 'hidden'})
    db_password = forms.CharField(error_messages={'required': 'Please enter the database password'},
                                  required=True, max_length=100, widget=forms.PasswordInput)
    # attrs={'type': 'hidden'}
    #     attrs={'class': 'form-control', 'placeholder': '$!@#ka3'}))
    run_every = forms.IntegerField(error_messages={'required': 'Please enter the run every period'},
                                   required=True, widget=forms.Select(choices=RUN_EVERY))
    # widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': '06 hours'}))
    # class Meta:
    #     model = JobConfig
    #     exclude = ['start_time, destination_server_list']
