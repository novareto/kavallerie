import abc
import typing as t
import smtplib
from collections import deque
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from kavallerie.response import Response
from kavallerie.pipeline import Handler, MiddlewareFactory


class SMTPConfiguration(t.NamedTuple):
    emitter: str
    port: int = 25
    host: str = "localhost"
    user: str = None
    password: str = None
    debug: bool = False


class Courrier:

    def __init__(self, config: SMTPConfiguration):
        self.config = config
        self.queue = deque()

    @staticmethod
    def format_email(origin, target, subject, text, html=None):
        msg = MIMEMultipart("alternative")
        msg["From"] = origin
        msg["To"] = target
        msg["Subject"] = subject
        msg['Message-ID'] = make_msgid()
        msg.set_charset("utf-8")

        part1 = MIMEText(text, "plain")
        part1.set_charset("utf-8")
        msg.attach(part1)

        if html is not None:
            part2 = MIMEText(html, "html")
            part2.set_charset("utf-8")
            msg.attach(part2)

        return msg

    def connect(self):
        server = smtplib.SMTP(self.config.host, str(self.config.port))
        server.set_debuglevel(self.config.debug)
        code, response = server.ehlo()
        if code < 200 or code >= 300:
            raise RuntimeError(
                'Error sending EHLO to the SMTP server '
                f'(code={code}, response={response})'
            )
        return server

    def clear(self):
        self.queue.clear()

    def send(self, recipient, subject, text, html=None) -> str:
        mail = self.format_email(
            self.config.emitter, recipient, subject, text, html)
        self.queue.append(mail)
        return mail['Message-ID']

    def exhaust(self):
        if not self.queue:
            return

        server = self.connect()

        # If we can encrypt this session, do it
        if server.has_extn("STARTTLS"):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection
        if self.config.user:
            server.login(self.config.user, self.config.password)
        try:
            while self.queue:
                email = self.queue.popleft()
                server.sendmail(
                    email['From'], email['To'], email.as_string())
        finally:
            server.close()


class Mailer(MiddlewareFactory):

    courrier: t.ClassVar[t.Type[Courrier]] = Courrier
    Configuration: t.ClassVar[SMTPConfiguration] = SMTPConfiguration

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Optional[t.Mapping] = None):

        def emailer_middleware(request):
            request.utilities['courrier'] = Courrier(self.config)
            response = handler(request)
            if response.status < 400:
                tm = request.utilities.get('transaction_manager')
                if tm is None or not tm.isDoomed():
                    request.utilities['courrier'].exhaust()

            del request.utilities['courrier']
            return response

        return emailer_middleware
