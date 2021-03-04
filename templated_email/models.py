from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField

from .fields import AutoSlugField


class SavedEmail(models.Model):
    uuid = models.UUIDField(default=uuid4)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class MailTemplate(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    slug = AutoSlugField(_("Slug"), populate_from="name",
                         editable=True,
                         unique=True,
                         overwrite_on_add=True,)
    tempalte = RichTextField(
        verbose_name=_('tempalte'), blank=True, null=True,
        help_text=_('The content of the mail. Context variable can be '
                    'used.'))
