from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    verbose_name = "Рассылка"
    verbose_name_plural = "Рассылки"
    list_display = ("email", "date")
