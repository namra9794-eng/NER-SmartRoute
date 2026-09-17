from django.contrib import admin
from .models import Alert, AlertTranslation

admin.site.register(Alert)
admin.site.register(AlertTranslation)
