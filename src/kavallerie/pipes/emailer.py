import typing as t
import smtplib
import logging
from abc import ABC, abstractmethod
from mailbox import Mailbox, Maildir
from pathlib import Path
from io import IOBase
from collections import deque
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from kavallerie.pipeline import Handler, MiddlewareFactory
from transaction.interfaces import IDataManager
from zope.interface import implementer

from postrider import create_message
from postrider.mailer import SMTPConfiguration, Courrier


class BaseCourrier(ABC):

    emitter: str = "test@test.com"

    def __init__(self):
        self.queue = deque()

    def clear(self):
        self.queue.clear()

    def connect(self):
        return

    def disconnect(self):
        return

    def send(self, recipient, subject, text, html=None, files=None) -> str:
        mail = self.create_message(
            self.emitter, recipient, subject, text, html, files)
        self.queue.append(mail)
        return mail['Message-ID']

    @abstractmethod
    def commit_message(self, message):
        pass

    def exhaust(self):
        if not self.queue:
            return
        try:
            while self.queue:
                email = self.queue.popleft()
                self.commit_message(email)
        finally:
            self.disconnect()


class MaildirCourrier(BaseCourrier):

    def __init__(self, path: Path, emitter: str):
        self.maibox = Maildir(path)
        self.emitter = emitter
        super().__init__()

    def commit_message(self, message):
        self.mailbox.add(message)


class SMTPCourrier(Courrier):

    def __init__(self, config: SMTPConfiguration):
        self.config = config
        self.emitter = config.emitter
        self.server = None
        super().__init__()

    def commit_message(self, message):
        self.server.sendmail(
            message['From'],
            message['To'],
            message.as_string()
        )

    def disconnect(self):
        if self.server is not None:
            self.server.close()
            self.server = None


@implementer(IDataManager)
class MailDataManager:

    def __init__(self, courrier: BaseCourrier, manager):
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
        except Exception:
            # Any exceptions here can cause database corruption.
            # Better to protect the data and potentially miss emails than
            # leave a database in an inconsistent state which requires a
            # guru to fix.
            logging.exception(
                f"Failed in tpc_finish for {self.courrier.exhaust!r}")

    tpc_abort = abort


def mailer(courrier: BaseCourrier):

    def courrier(
            handler: Handler,
            globalconf: t.Optional[t.Mapping] = None):

        def emailer_middleware(request):
            request.utilities['courrier'] = courrier
            tm = request.utilities.get('transaction_manager')
            if tm is not None and not tm.isDoomed():
                tm.get().join(MailDataManager(courrier, tm))

            response = handler(request)

            if tm is None and response.status < 400:
                request.utilities['courrier'].exhaust()
                del request.utilities['courrier']
            return response

        return emailer_middleware
    return courrier
