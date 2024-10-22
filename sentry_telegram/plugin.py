# coding: utf-8
import logging, json
from collections import defaultdict

from django import forms
from django.utils.translation import gettext_lazy as _

from sentry.plugins.bases import notify
from sentry.http import safe_urlopen
from sentry.utils.safe import safe_execute

from . import __version__, __doc__ as package_doc


TELEGRAM_MAX_MESSAGE_LENGTH = 4096  # https://core.telegram.org/bots/api#sendmessage:~:text=be%20sent%2C%201%2D-,4096,-characters%20after%20entities
EVENT_TITLE_MAX_LENGTH = 500


class TelegramNotificationsOptionsForm(notify.NotificationConfigurationForm):
    config = forms.JSONField(
        initial={
            "uat": {
                "api_origin": "https://api.telegram.org",
                "api_token": "",
                "receiver": "",
                "message_template": "*[Sentry]* {project_name} {tag[level]}: *{title}*\n```\n{message}```\n{url}"
            },
            "staging": {
                "api_origin": "https://api.telegram.org",
                "api_token": "",
                "receiver": "",
                "message_template": "*[Sentry]* {project_name} {tag[level]}: *{title}*\n```\n{message}```\n{url}"
            },
            "prod": {
                "api_origin": "https://api.telegram.org",
                "api_token": "",
                "receiver": "",
                "message_template": "*[Sentry]* {project_name} {tag[level]}: *{title}*\n```\n{message}```\n{url}"
            }
        }
    )
    #  api_origin = forms.CharField(
        #  label=_('Telegram API origin'),
        #  widget=forms.TextInput(attrs={'placeholder': 'https://api.telegram.org'}),
        #  initial='https://api.telegram.org'
    #  )
    #  api_token = forms.CharField(
        #  label=_('BotAPI token'),
        #  widget=forms.TextInput(attrs={'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}),
        #  help_text=_('Read more: https://core.telegram.org/bots/api#authorizing-your-bot'),
    #  )
    #  receivers = forms.CharField(
        #  label=_('Receivers'),
        #  widget=forms.Textarea(attrs={'class': 'span6'}),
        #  help_text=_('Enter receivers IDs (one per line). Personal messages, group chats and channels also available. '
                    #  'If you want to specify a thread ID, separate it with "/" (e.g. "12345/12").'),
    #  )
    #  message_template = forms.CharField(
        #  label=_('Message template'),
        #  widget=forms.Textarea(attrs={'class': 'span4'}),
        #  help_text=_('Set in standard python\'s {}-format convention, available names are: '
                    #  '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}'),
        #  initial='*[Sentry]* {project_name} {tag[level]}: *{title}*\n```\n{message}```\n{url}'
    #  )


class TelegramNotificationsPlugin(notify.NotificationPlugin):
    title = 'Telegram Notifications'
    slug = 'sentry_telegram'
    description = package_doc
    version = __version__
    author = 'Viacheslav Butorov'
    author_url = 'https://github.com/butorov/sentry-telegram'
    resource_links = [
        ('Bug Tracker', 'https://github.com/butorov/sentry-telegram/issues'),
        ('Source', 'https://github.com/butorov/sentry-telegram'),
    ]

    conf_key = 'sentry_telegram'
    conf_title = title
    tg_config = None

    project_conf_form = TelegramNotificationsOptionsForm

    logger = logging.getLogger('sentry.plugins.sentry_telegram')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('config', project) 

    def get_config(self, project, **kwargs):
        return [
            {
                'name': 'config',
                'label': 'Configuration for Telegram Notification',
                'type': 'textarea',
                'help': 'Read more: https://core.telegram.org/bots/api#authorizing-your-bot',
                'placeholder': """{
                    "uat": {
                        "api_origin": "",
                        "api_token": "",
                        "receiver": "",
                        "message_template": "",
                    },
                    "staging": {
                        "api_origin": "",
                        "api_token": "",
                        "receiver": "",
                        "message_template": "",
                    },
                    "prod": {
                        "api_origin": "",
                        "api_token": "",
                        "receiver": "",
                        "message_template": "",
                    },
                }""",
                'validators': [],
                'required': True,
                'default': """{
                    "uat": {
                        "api_origin": "",
                        "api_token": "",
                        "receiver": "",
                        "message_template": "",
                    },
                    "staging": {
                        "api_origin": "",
                        "api_token": "",
                        "receiver": "",
                        "message_template": "",
                    },
                    "prod": {
                        "api_origin": "",
                        "api_token": "",
                        "receiver": "",
                        "message_template": "",
                    },
                } """
            }
        ]
        #  return [
            #  {
                #  'name': 'api_origin',
                #  'label': 'Telegram API origin',
                #  'type': 'text',
                #  'placeholder': 'https://api.telegram.org',
                #  'validators': [],
                #  'required': True,
                #  'default': 'https://api.telegram.org'
            #  },
            #  {
                #  'name': 'api_token',
                #  'label': 'BotAPI token',
                #  'type': 'text',
                #  'help': 'Read more: https://core.telegram.org/bots/api#authorizing-your-bot',
                #  'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                #  'validators': [],
                #  'required': True,
            #  },
            #  {
                #  'name': 'receivers',
                #  'label': 'Receivers',
                #  'type': 'textarea',
                #  'help': 'Enter receivers IDs (one per line). Personal messages, group chats and channels also available. '
                        #  'If you want to specify a thread ID, separate it with "/" (e.g. "12345/12").',
                #  'validators': [],
                #  'required': True,
            #  },
            #  {
                #  'name': 'message_template',
                #  'label': 'Message Template',
                #  'type': 'textarea',
                #  'help': 'Set in standard python\'s {}-format convention, available names are: '
                        #  '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}. Undefined tags will be shown as [NA]',
                #  'validators': [],
                #  'required': True,
                #  'default': '*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
            #  },
        #  ]

    def compile_message_text(self, message_template: str, message_params: dict, event_message: str) -> str:
        """
        Compiles message text from template and event message.
        Truncates the original event message (`event.message`) to fit Telegram message length limit.
        """
        # TODO: add tests
        truncate_warning_text = '... (truncated)'
        truncate_warning_length = len(truncate_warning_text)

        truncated = False
        while True:
            message_text = message_template.format(**message_params, message=event_message)
            message_text_size = len(message_text)

            if truncated or message_text_size <= TELEGRAM_MAX_MESSAGE_LENGTH:
                break
            else:
                truncate_size = (message_text_size - TELEGRAM_MAX_MESSAGE_LENGTH) + truncate_warning_length
                event_message = event_message[:-truncate_size] + truncate_warning_text
                truncated = True

        return message_text

    def extract_tags(self, event):
        event_tags = defaultdict(lambda: '[NA]')
        event_tags.update({k: v for k, v in event.tags})
        return event_tags

    def build_message(self, group, event):
        event_tags = self.extract_tags(event) 

        message_params = {
            'title': event.title[:EVENT_TITLE_MAX_LENGTH],
            'tag': event_tags,
            'project_name': group.project.name,
            'url': group.get_absolute_url(),
        }
        text = self.compile_message_text(
            self.get_message_template(),
            message_params,
            event.message,
        )

        return {
            'text': text,
            'parse_mode': 'Markdown',
        }

    def build_url(self):
        return '%s/bot%s/sendMessage' % (self.tg_config['api_origin'], self.tg_config['api_token'])

    def get_message_template(self):
        return self.tg_config['message_template']

    def get_tg_config(self, project, event):
        event_tags = self.extract_tags(event)
        tg_configs = self.get_option('config', project)
        tg_configs = json.loads(tg_configs)
        environment = event_tags.get('environment', 'deployment')
        tg_config = tg_configs[environment]
        if tg_config is None:
            self.logger.debug(f'TG config for environment {environment} is empty')
        return tg_config

    def send_message(self, url, payload, receiver: list[str, str]):
        payload['chat_id'] = receiver
        self.logger.debug('Sending message to %s' % receiver)
        response = safe_urlopen(
            method='POST',
            url=url,
            json=payload,
        )
        self.logger.debug('Response code: %s, content: %s' % (response.status_code, response.content))
        if response.status_code > 299:
            raise ConnectionError(response.content)

    def notify_users(self, group, event, fail_silently=False, **kwargs):
        self.logger.debug('Received notification for event: %s' % event)
        tg_config = self.get_tg_config(group.project, event)
        if tg_config is None:
            return
        api_origin = tg_config.get('api_origin', None)
        api_token = tg_config.get('api_token', None)
        receiver = tg_config.get('receiver', None)
        message_template = tg_config.get('message_template', None)

        if api_origin is None or api_origin == "":
            raise ValueError('API Origin is empty')

        if api_token is None or api_token == "":
            raise ValueError('API Token is empty')

        if receiver is None or receiver == "":
            raise ValueError('Receiver is empty')

        if message_template is None or message_template == "":
            raise ValueError('Message Template is empty')

        self.tg_config = tg_config

        payload = self.build_message(group, event)
        self.logger.debug('Built payload: %s' % payload)
        url = self.build_url()
        self.logger.debug('Built url: %s' % url)
        safe_execute(self.send_message, url, payload, receiver)
