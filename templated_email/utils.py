from functools import partial
from email.utils import unquote
from email.mime.image import MIMEImage

from django.core.mail import make_msgid
from django.utils.module_loading import import_string
from django.conf import settings
from django.template import engines
from django.template import loader
from django.template.backends.django import Template as DjangoTemplate
try:
    from django.template.backends.jinja2 import Template as Jinja2Template
except ImportError:
    # Most likely Jinja2 isn't installed, in that case just create a class since
    # we always want it to be false anyway.
    class Jinja2Template:
        pass

from render_block.django import django_render_block
from render_block.exceptions import UnsupportedEngine

import six


def _get_klass_from_config(config_variable, default):
    klass_path = getattr(settings, config_variable, default)
    if isinstance(klass_path, six.string_types):
        klass_path = import_string(klass_path)

    return klass_path


get_emailmessage_klass = partial(
    _get_klass_from_config,
    'TEMPLATED_EMAIL_EMAIL_MESSAGE_CLASS',
    'django.core.mail.EmailMessage'
)

get_emailmultialternatives_klass = partial(
    _get_klass_from_config,
    'TEMPLATED_EMAIL_EMAIL_MULTIALTERNATIVES_CLASS',
    'django.core.mail.EmailMultiAlternatives',
)


class InlineImage(object):

    def __init__(self, filename, content, subtype=None, domain=None):
        self.filename = filename
        self._content = content
        self.subtype = subtype
        self.domain = domain
        self._content_id = None

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content_id = None
        self._content = value

    def attach_to_message(self, message):
        if not self._content_id:
            self.generate_cid()
        image = MIMEImage(self.content, self.subtype)
        image.add_header('Content-Disposition', 'inline', filename=self.filename)
        image.add_header('Content-ID', self._content_id)
        message.attach(image)

    def generate_cid(self):
        self._content_id = make_msgid('img', self.domain)

    def __str__(self):
        if not self._content_id:
            self.generate_cid()
        return 'cid:' + unquote(self._content_id)


def render_field_block_to_string(template_name, block_name, context=None, request=None):
    """
    Loads the given template_name and renders the given block with the given
    dictionary as context. Returns a string.

        template_name
            The name of the template to load and render. If it's a list of
            template names, Django uses select_template() instead of
            get_template() to find the template.
    """

    # Like render_to_string, template_name can be a string or a list/tuple.
    try:
        if isinstance(template_name, (tuple, list)):
            t = loader.select_template(template_name)
        else:
            t = loader.get_template(template_name)
    except:
        # Handle the case if the temolate_name was a slug (not a file)
        from templated_email.models import MailTemplate
        template_name = template_name[0].split(".")[0].split("/")[-1]
        django_engine = engines["django"]
        email_template = MailTemplate.objects.get(slug=template_name).tempalte
        t = django_engine.from_string(email_template)

    # Create the context instance.
    context = context or {}

    # The Django backend.
    if isinstance(t, DjangoTemplate):
        return django_render_block(t, block_name, context, request)

    elif isinstance(t, Jinja2Template):
        from render_block.jinja2 import jinja2_render_block
        return jinja2_render_block(t, block_name, context)

    else:
        raise UnsupportedEngine(
            'Can only render blocks from the Django template backend.')
