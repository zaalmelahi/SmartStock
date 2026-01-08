from django.db import models
from django.utils.translation import gettext_lazy as _
from .application import Application

class Template(models.Model):
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='templates',
        verbose_name=_('Application')
    )
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    body = models.TextField(verbose_name=_('Body'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
