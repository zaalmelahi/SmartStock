from django import forms
from .models import Application, ApplicationConfiguration

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'enabled', 'name', 'bot_id', 'user_id', 'webhook_key', 
            'whatsapp_provider_type', 'session', 'phone', 
            'auto_replay_group', 'apply_authorized_contact', 
            'app_id', 
            'configuration',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bot_id': forms.TextInput(attrs={'class': 'form-control'}),
            'user_id': forms.TextInput(attrs={'class': 'form-control'}),
            'webhook_key': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_provider_type': forms.Select(attrs={'class': 'form-select'}),
            'session': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'app_id': forms.TextInput(attrs={'class': 'form-control'}),
            'configuration': forms.Select(attrs={'class': 'form-select'}),
        }

class ApplicationConfigurationForm(forms.ModelForm):
    class Meta:
        model = ApplicationConfiguration
        fields = [
            'name', 'botpress_url', 'botpress_username', 'botpress_password',
            'system_url', 'system_auth_info', 'url', 'token',
            'use_voice_message', 'url_voice', 'use_accounting_agent',
            'flow_ai', 'flow_url', 'flow_id', 'flow_token'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'botpress_url': forms.TextInput(attrs={'class': 'form-control'}),
            'botpress_username': forms.TextInput(attrs={'class': 'form-control'}),
            'botpress_password': forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
            'system_url': forms.TextInput(attrs={'class': 'form-control'}),
            'system_auth_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'token': forms.TextInput(attrs={'class': 'form-control'}),
            'url_voice': forms.TextInput(attrs={'class': 'form-control'}),
            'use_voice_message': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_accounting_agent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'flow_ai': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'flow_url': forms.TextInput(attrs={'class': 'form-control'}),
            'flow_id': forms.TextInput(attrs={'class': 'form-control'}),
            'flow_token': forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
        }
