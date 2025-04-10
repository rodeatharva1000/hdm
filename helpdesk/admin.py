from django.contrib import admin
from . import models

admin.site.register(models.Feedback)
admin.site.register(models.Product)

@admin.register(models.Help)
class HelpAdmin(admin.ModelAdmin):
    list_display = ['help_type', 'reply', 'help', 'user']
    ordering = ['-urgency_score']