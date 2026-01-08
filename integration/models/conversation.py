from django.db import models
from django.utils.translation import gettext_lazy as _
from .application import Application

class Conversation(models.Model):
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        verbose_name=_('Application')
    )
    session_id = models.CharField(
        max_length=255, 
        db_index=True, 
        verbose_name=_('Session ID')
    )
    user_identifier = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('User Identifier')
    )
    started_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Started At')
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user_identifier} ({self.session_id})"


class Message(models.Model):
    DIRECTION_CHOICES = [
        ('incoming', _('Incoming')),
        ('outgoing', _('Outgoing')),
    ]

    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages', 
        verbose_name=_('Conversation')
    )
    direction = models.CharField(
        max_length=20, 
        choices=DIRECTION_CHOICES, 
        verbose_name=_('Direction')
    )
    content = models.TextField(verbose_name=_('Content'))
    metadata = models.JSONField(
        blank=True, 
        null=True, 
        verbose_name=_('Metadata')
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.direction}: {self.content[:50]}"
