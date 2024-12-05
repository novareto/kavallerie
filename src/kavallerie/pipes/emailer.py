import typing as t
import logging
from abc import ABC, abstractmethod
from mailbox import Maildir
from pathlib import Path
from io import IOBase
from collections import deque
from kavallerie.pipeline import Handler, MiddlewareFactory
from transaction.interfaces import IDataManager
from zope.interface import implementer

from postrider import create_message
from postrider.mailer import SMTPConfiguration, Courrier


class BaseCourrier(ABC):

    emitter: str = "test@test.com"

    def __init__(self, emitter: str):
        self.emitter = emitter
        self.queue = deque()

    def clear(self):
        self.queue.clear()

    def connect(self):
        return

    def disconnect(self):
        return

    def send(self,
             recipients: str | list[str],
             subject: str,
             text: str,
             html: str | None = None,
             files: list[str | Path | IOBase] | None = None
             ) -> str:
        if not isinstance(recipients, list):
            recipients = [recipients]
        mail = create_message(
            self.emitter, recipients, subject, text, html, files)
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

    def __init__(self, emitter: str, path: Path):
        self.maibox = Maildir(path)
        super().__init__(emitter)

    def commit_message(self, message):
        self.mailbox.add(message)


class SMTPCourrier(Courrier, BaseCourrier):

    def __init__(self, emitter: str, config: SMTPConfiguration):
        self.server = None
        BaseCourrier.__init__(self, emitter)
        Courrier.__init__(self, config)

    def connect(self):
        if self.server is None:
            self.server = super().connect()

    def commit_message(self, message):
        self.connect()
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


def Mailer(courrier: BaseCourrier):

    def courrier_pipe(
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
    return courrier_pipe
