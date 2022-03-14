import abc
import typing as t
import smtplib
from collections import deque
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from kavallerie.response import Response
from kavallerie.pipeline import Handler, MiddlewareFactory
from transaction.interfaces import IDataManager
from zope.interface import implementer


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
        self.server = None

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
        if self.server is None:
            server = smtplib.SMTP(self.config.host, str(self.config.port))
            server.set_debuglevel(self.config.debug)
            code, response = server.ehlo()
            if code < 200 or code >= 300:
                raise RuntimeError(
                    'Error sending EHLO to the SMTP server '
                    f'(code={code}, response={response})'
                )
            self.server = server
        return self.server

    def disconnect(self):
        if self.server is not None:
            self.server.close()
            self.server = None

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
            self.disconnect()


@implementer(IDataManager)
class MailDataManager:

    def __init__(self, courrier: Courrier, manager):
        self.courrier = courrier
        self.transaction_manager = manager

    def commit(self, txn):
        pass

    def abort(self, txn):
        self.courrier.disconnect()

    def sortKey(self):
        return str(id(self))

    def beforeCompletion(self, txn):
        pass

    afterCompletion = beforeCompletion

    def tpc_begin(self, txn, subtransaction=False):
        assert not subtransaction

    def tpc_vote(self, txn):
        self.courrier.connect()

    def tpc_finish(self, txn):
        try:
            self.courrier.exhaust()
        except Exception as exc:
            # Any exceptions here can cause database corruption.
            # Better to protect the data and potentially miss emails than
            # leave a database in an inconsistent state which requires a
            # guru to fix.
            log.exception(
                f"Failed in tpc_finish for {self.courrier.exhaust!r}")

    tpc_abort = abort


class Mailer(MiddlewareFactory):

    courrier: t.ClassVar[t.Type[Courrier]] = Courrier
    Configuration: t.ClassVar[SMTPConfiguration] = SMTPConfiguration

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Optional[t.Mapping] = None):

        def emailer_middleware(request):
            courrier = request.utilities['courrier'] = Courrier(self.config)
            tm = request.utilities.get('transaction_manager')
            if tm is not None and not tm.isDoomed():
                tm.get().join(MailDataManager(courrier, tm))

            response = handler(request)

            if tm is None and response.status < 400:
                request.utilities['courrier'].exhaust()
                del request.utilities['courrier']
            return response

        return emailer_middleware
