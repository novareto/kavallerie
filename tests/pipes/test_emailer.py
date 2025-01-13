from smtpdfix import SMTPDFix
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.pipes.emailer import Mailer, SMTPCourrier, SMTPConfiguration
from kavallerie.pipes.transaction import Transaction


def test_emailer(environ):

    def handler(request):
        request.utilities['courrier'].send(
            'john@doe.com', 'My subject', 'My emailer'
        )
        return Response(201)

    def fail_handler(request):
        request.utilities['courrier'].send(
            'john@doe.com', 'My subject', 'My emailer'
        )
        return Response(400)

    config = SMTPConfiguration(port=9999)
    mailer = Mailer(SMTPCourrier('test@example.com', config))

    request = Request(None, environ=environ)
    pipeline = mailer(handler)
    with SMTPDFix(config.host, config.port) as smtpd:
        pipeline(request)
    assert len(smtpd.messages) == 1

    request = Request(None, environ=environ)
    pipeline = mailer(fail_handler)
    with SMTPDFix(config.host, config.port) as smtpd:
        pipeline(request)
    assert len(smtpd.messages) == 0


def test_emailer_with_transaction(environ):

    def handler(request):
        request.utilities['courrier'].send(
            'john@doe.com', 'My subject', 'My emailer'
        )
        return Response(201)

    def aborting_handler(request):
        request.utilities['courrier'].send(
            'john@doe.com', 'My subject', 'My emailer'
        )
        request.utilities['transaction_manager'].doom()
        return Response(200)

    config = SMTPConfiguration(port=9999)
    mailer = Mailer(SMTPCourrier('test@example.com', config))
    transaction = Transaction()

    request = Request(None, environ=environ)
    pipeline = transaction(mailer(handler))
    with SMTPDFix(config.host, config.port) as smtpd:
        pipeline(request)
    assert len(smtpd.messages) == 1

    request = Request(None, environ=environ)
    pipeline = transaction(mailer(aborting_handler))
    with SMTPDFix(config.host, config.port) as smtpd:
        pipeline(request)
    assert len(smtpd.messages) == 0
