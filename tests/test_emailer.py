from smtpdfix import SMTPDFix
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.pipes.emailer import Mailer


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

    request = Request('/', app=None, environ=environ)
    mailer = Mailer(emitter='test@example.com', port=9999)

    pipeline = mailer(handler)
    with SMTPDFix(mailer.config.host, mailer.config.port) as smtpd:
        pipeline(request)
    assert len(smtpd.messages) == 1

    pipeline = mailer(fail_handler)
    with SMTPDFix(mailer.config.host, mailer.config.port) as smtpd:
        pipeline(request)
    assert len(smtpd.messages) == 0
