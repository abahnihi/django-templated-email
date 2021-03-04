from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import MailTemplate

if "wagtail.admin" in settings.INSTALLED_APPS:
    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.contrib.modeladmin.options import (
        ModelAdmin,
        ModelAdminGroup,
        modeladmin_register,
    )

    


    class MailTemplateAdmin(ModelAdmin):
        model = MailTemplate
        menu_label = _("MailTemplate")
        list_display = (
            "name",
            "slug",
        )
        search_fields = (
            "name",
            "slug",
        )
        panels = [
            FieldPanel("name"),
            FieldPanel("slug"),
            FieldPanel("tempalte"),
        ]


    class MailTemplateAdminGroup(ModelAdminGroup):
        """
        ModelAdminGroup to be register to wagtail admin
        """

        menu_label = _("Email Template")
        items = (MailTemplateAdmin,)


    modeladmin_register(MailTemplateAdminGroup)

if "django.contrib.admin" in settings.INSTALLED_APPS:
    from django.contrib import admin

    @admin.register(MailTemplate)
    class MailTemplateAdmin(admin.ModelAdmin):
        list_display = ['name', 'slug']
