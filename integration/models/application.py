from django.db import models
from django.utils.translation import gettext_lazy as _
from .application_configuration import ApplicationConfiguration

class Application(models.Model):
    WHATSAPP_PROVIDER_CHOICES = [
        ('meta', _('Meta API')),
        ('wppconnect', _('WPPConnect')),
    ]
    enabled = models.BooleanField(default=True,verbose_name=_('Enabled'))
    name = models.CharField(max_length=255, unique=True,verbose_name=_('Name'))
    bot_id = models.CharField(max_length=255,verbose_name=_('Bot ID'))
    user_id=models.CharField(max_length=255,verbose_name=_('User ID'),blank=True, null=True)
    webhook_key = models.CharField(max_length=255, unique=True,verbose_name=_('Webhook Key'))
    whatsapp_provider_type = models.CharField(
        max_length=50,choices=WHATSAPP_PROVIDER_CHOICES, verbose_name=_('WhatsApp Provider Type'),blank=True, null=True
    )
    session = models.CharField(max_length=255,verbose_name=_('Session'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Phone Number"))
    auto_replay_group = models.BooleanField(default=True, verbose_name=_("Auto Replay In Group"))
    apply_authorized_contact = models.BooleanField(default=False, verbose_name=_("Apply Authorized Contact"))
    app_id=models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Application_ID"))
    configuration = models.ForeignKey(
        ApplicationConfiguration, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name=_('Configuration')
    )

    def __str__(self):
        return self.name
    def is_token_valid(self):
        """Check if the stored token is still valid."""
        if not self.configuration:
            return False
        return self.configuration.is_token_valid()
    
    @property
    def decrypted_system_auth_info(self):
        """Get decrypted system auth info for programmatic use"""
        if not self.configuration:
            return None
        return self.configuration.decrypted_system_auth_info
    
    @property 
    def decrypted_botpress_password(self):
        """Get decrypted botpress password for programmatic use"""
        if not self.configuration:
            return None
        return self.configuration.decrypted_botpress_password
    
    @property
    def decrypted_botpress_token(self):
        """Get decrypted botpress token for programmatic use"""
        if not self.configuration:
            return None
        return self.configuration.decrypted_botpress_token
    
    @property
    def decrypted_token(self):
        """Get decrypted token for programmatic use"""
        if not self.configuration:
            return None
        return self.configuration.decrypted_token
    
    # Properties to maintain backward compatibility
    @property
    def botpress_url(self):
        return self.configuration.botpress_url if self.configuration else ''
    
    @property
    def botpress_username(self):
        return self.configuration.botpress_username if self.configuration else ''
    
    @property
    def botpress_password(self):
        return self.configuration.botpress_password if self.configuration else ''
    
    @property
    def botpress_token(self):
        return self.configuration.botpress_token if self.configuration else ''
    
    @property
    def token_expires_at(self):
        return self.configuration.token_expires_at if self.configuration else None
    
    @property
    def system_url(self):
        return self.configuration.system_url if self.configuration else ''
    
    @property
    def system_auth_info(self):
        return self.configuration.system_auth_info if self.configuration else ''
    
    @property
    def url(self):
        return self.configuration.url if self.configuration else ''
    
    @property
    def token(self):
        return self.configuration.token if self.configuration else ''
    
    @property
    def use_voice_message(self):
        return self.configuration.use_voice_message if self.configuration else False
    
    @property
    def url_voice(self):
        return self.configuration.url_voice if self.configuration else ''
    
    @property
    def use_accounting_agent(self):
        return self.configuration.use_accounting_agent if self.configuration else False
    
    @property
    def flow_ai(self):
        return self.configuration.flow_ai if self.configuration else False
    
    @property
    def flow_url(self):
        return self.configuration.flow_url if self.configuration else ''
    
    @property
    def flow_id(self):
        return self.configuration.flow_id if self.configuration else ''
    
    @property
    def flow_token(self):
        return self.configuration.flow_token if self.configuration else ''
    
    @property
    def decrypted_flow_token(self):
        """Get decrypted flow token for programmatic use"""
        if not self.configuration:
            return None
        return self.configuration.decrypted_flow_token
    
    # Setters for backward compatibility
    @botpress_token.setter
    def botpress_token(self, value):
        if self.configuration:
            self.configuration.botpress_token = value
            self.configuration.save()
    
    @token_expires_at.setter
    def token_expires_at(self, value):
        if self.configuration:
            self.configuration.token_expires_at = value
            self.configuration.save()
    
    @token.setter
    def token(self, value):
        if self.configuration:
            self.configuration.token = value
            self.configuration.save()
    
    
    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        ordering = ['name']
