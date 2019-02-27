import logging
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from mail_templated import EmailMessage
from config import exceptions

logger = logging.getLogger(__name__)


class BaseEmailMessage(EmailMessage):
    template_name = None

    def __init__(self, request=None, context=None, recipients=None):
        super(BaseEmailMessage, self).__init__()

        self.request = request
        self.context = {} if context is None else context
        self.template_name = self.__class__.template_name
        self.to = recipients

    def get_context_data(self):
        ctx = {}
        context = dict(ctx, **self.context)
        if self.request:
            site = get_current_site(self.request)
            domain = context.get('domain') or (getattr(settings, 'DOMAIN', '')
                                               or site.domain)
            protocol = context.get('protocol') or ('https'
                                                   if self.request.is_secure()
                                                   else 'http')
            site_name = context.get('site_name') or (getattr(
                settings, 'SITE_NAME', '') or site.name)
            user = context.get('user') or self.request.user
        else:
            domain = context.get('domain') or getattr(settings, 'DOMAIN', '')
            protocol = context.get('protocol') or 'http'
            site_name = context.get('site_name') or getattr(
                settings, 'SITE_NAME', '')
            user = context.get('user')

        site_logo_url = context.get('site_logo_url') or getattr(
            settings, 'SITE_LOGO_URL', '')
        site_owner_name = context.get('site_owner_name') or getattr(
            settings, 'SITE_OWNER_NAME', '')
        site_owner_url = context.get('site_owner_url') or getattr(
            settings, 'SITE_OWNER_URL', '')

        context.update({
            'domain': domain,
            'protocol': protocol,
            'site_name': site_name,
            'site_logo_url': site_logo_url,
            'site_owner_name': site_owner_name,
            'site_owner_url': site_owner_url,
            'user': user
        })
        return context

    def send(self, *args, **kwargs):
        try:
            self.from_email = kwargs.pop('from_email',
                                         settings.DEFAULT_FROM_EMAIL)
            self.context = self.get_context_data()

            return super(BaseEmailMessage, self).send(*args, **kwargs)
        except Exception as error:
            logger.exception(
                f'Unable to send an {self.template_name} to {self.to}')
            raise exceptions.ServiceUnavailable()
