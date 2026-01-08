from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from ..utils.encrypted_fields import EncryptedTextField, EncryptedCharField

class ApplicationConfiguration(models.Model):
    """Configuration model to hold botpress and system configuration details"""
    name = models.CharField(max_length=255, verbose_name=_('Name'), blank=True, null=True)
    botpress_url = models.CharField(max_length=500, verbose_name=_('BotPlatform URL'))
    botpress_username = models.CharField(max_length=255, verbose_name=_('BotPlatform Username'))
    botpress_password = EncryptedCharField(max_length=255, verbose_name=_('BotPlatform Password'))
    token_expires_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Token Expires At'))
    botpress_token = EncryptedTextField(max_length=1500, blank=True, null=True, verbose_name=_('BotPlatform_Token'))
    system_url = models.CharField(max_length=500, verbose_name=_('System URL'), blank=True, null=True)
    system_auth_info = EncryptedTextField(max_length=1500, blank=True, null=True, verbose_name=_('System Auth Info'))
    url = models.CharField(max_length=500, verbose_name=_('URL'))
    token = EncryptedCharField(max_length=500, verbose_name=_('Token'), blank=True, null=True)
    use_voice_message = models.BooleanField(default=False, verbose_name=_("Use Voice Message"))
    url_voice = models.CharField(max_length=500, verbose_name=_('URL Voice'), blank=True, null=True)
    use_accounting_agent = models.BooleanField(default=False, verbose_name=_("Use Accounting Agent"))
    
    # Flow AI Integration
    flow_ai = models.BooleanField(default=False, verbose_name=_("Enable Flow AI"))
    flow_url = models.CharField(max_length=500, verbose_name=_('Flow URL'), blank=True, null=True)
    flow_id = models.CharField(max_length=255, verbose_name=_('Flow ID'), blank=True, null=True)
    flow_token = EncryptedCharField(max_length=255, verbose_name=_('Flow Token'), blank=True, null=True)


    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.name if self.name else f"Config - {str(self.id)}"
    
    @property
    def decrypted_system_auth_info(self):
        """Get decrypted system auth info for programmatic use"""
        import json
        from ..utils.encrypted_fields import EncryptedTextField
        
        field = EncryptedTextField()
        decrypted_value = field.get_decrypted_value(self.system_auth_info)
        
        # If it's already a dict, return as is
        if isinstance(decrypted_value, dict):
            return decrypted_value
            
        # If it's a string, try to parse as JSON
        if isinstance(decrypted_value, str):
            try:
                return json.loads(decrypted_value)
            except (json.JSONDecodeError, TypeError):
                return decrypted_value
                
        return decrypted_value
    
    @property 
    def decrypted_botpress_password(self):
        """Get decrypted botpress password for programmatic use"""
        from ..utils.encrypted_fields import EncryptedCharField
        field = EncryptedCharField()
        return field.get_decrypted_value(self.botpress_password)
    
    @property
    def decrypted_botpress_token(self):
        """Get decrypted botpress token for programmatic use"""
        from ..utils.encrypted_fields import EncryptedTextField
        field = EncryptedTextField()
        return field.get_decrypted_value(self.botpress_token)
    
    @property
    def decrypted_token(self):
        """Get decrypted token for programmatic use"""
        from ..utils.encrypted_fields import EncryptedCharField
        field = EncryptedCharField()
        return field.get_decrypted_value(self.token)
    
    @property
    def decrypted_flow_token(self):
        """Get decrypted flow token for programmatic use"""
        from ..utils.encrypted_fields import EncryptedCharField
        field = EncryptedCharField()
        return field.get_decrypted_value(self.flow_token)
    
    def is_token_valid(self):
        """Check if the stored token is still valid."""
        return self.decrypted_botpress_token and self.token_expires_at and timezone.now() < self.token_expires_at

    class Meta:
        verbose_name = _('Application Configuration')
        verbose_name_plural = _('Application Configurations')
        ordering = ['-created_at']
