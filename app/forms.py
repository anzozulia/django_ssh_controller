import os
import uuid
import telebot

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Server, AlertSettings, Settings
from app.monitor.sysdrivers import SSH

class LoginForm(AuthenticationForm):
    username = forms.CharField(required=True, label="", help_text="")
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label="", help_text="")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Логин'
        self.fields['username'].widget.attrs['name'] = 'email'
        self.fields['username'].widget.attrs['type'] = 'email'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['password'].widget.attrs['name'] = 'password'
        self.fields['password'].widget.attrs['type'] = 'password'
        self.fields['password'].widget.attrs['value'] = ''


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = (
            'hostname',
            'user',
            'port',
            'ssh_key',
            'check_interval',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        

    def clean(self):
        form_data = super().clean()
        hostname = form_data.get('hostname')
        port = form_data.get('port')
        user = form_data.get('user')
        ssh_key = form_data.get('ssh_key')

        response = os.system("ping -c 1 -w 1 " + hostname)

        if response != 0:
            self.add_error("hostname", _('Hostname is invalid or host not responding.'))
        if port < 1 or port > 65535:
            self.add_error("port", _('Port is invalid.'))
        if not ssh_key:
            return form_data
        else:
            ssh_key.name = f'{str(uuid.uuid4().hex)}'
            key = f'/tmp/{ssh_key.name}'
            with open(key, 'wb') as tempfile:
                tempfile.write(ssh_key.read())

            try:
                ssh_client = SSH(
                    host=hostname,
                    username=user,
                    port=port,
                    key=key,
                )
                ssh_client.connect()
            except:
                self.add_error("hostname", _('SSH login attempt failed, check parameters.'))
                
        return form_data
    

class ServerSettingsForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = (
            'hostname',
            'user',
            'port',
            'ssh_key',
            'check_interval',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        self.fields['hostname'].widget.attrs['readonly'] = True

    def clean(self):
        form_data = super().clean()
        hostname = form_data.get('hostname')
        port = form_data.get('port')
        user = form_data.get('user')
        ssh_key = form_data.get('ssh_key')

        response = os.system("ping -c 1 -w 1 " + hostname)

        # if response != 0:
        #     self.add_error("hostname", _('Hostname is invalid or host not responding.'))
        # if port < 1 or port > 65535:
        #     self.add_error("port", _('Port is invalid.'))
        # if ssh_key:
        #     ssh_key.name = f'{str(uuid.uuid4().hex)}'
        #     key = f'/tmp/{ssh_key.name}'
        #     with open(key, 'wb') as tempfile:
        #         tempfile.write(ssh_key.read())
        # else:
        #     key = self.instance.ssh_key.path
        # try:
        #     ssh_client = SSH(
        #         host=hostname,
        #         username=user,
        #         port=port,
        #         key=key,
        #     )
        #     ssh_client.connect()
        # except:
        #     self.add_error("hostname", _('SSH login attempt failed, check parameters.'))
                
        return form_data


class AlertSettingsForm(forms.ModelForm):
    class Meta:
        model = AlertSettings
        fields = (
            'server',
            'metric',
            'type',
            'condition',
            'value',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['server'].widget = forms.HiddenInput()


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = (
            'tg_bot_token',
            'tg_chat_id',
            'tg_alerts',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'tg_alerts':
                self.fields[field].widget.attrs['class'] = 'form-control'


    def clean(self):
        form_data = super().clean()
        tg_bot_token = form_data.get('tg_bot_token')
        tg_chat_id = form_data.get('tg_chat_id')

        if tg_bot_token:
            try:
                telebot.TeleBot(tg_bot_token).get_me()
                if tg_chat_id:
                    try:
                        telebot.TeleBot(tg_bot_token).get_chat(tg_chat_id)
                    except:
                        self.add_error("tg_chat_id", _('TG chat ID is invalid.'))
            except:
                self.add_error("tg_bot_token", _('TG bot token is invalid.'))
                
        return form_data