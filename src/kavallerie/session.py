import itsdangerous
import typing as t
from http_session.meta import Store
from http_session.cookie import SameSite, HashAlgorithm, SignedCookieManager
from kavallerie.pipeline import MiddlewareFactory


class HTTPSession(MiddlewareFactory):

    id = 'http-session'

    class Configuration(t.NamedTuple):
        store: Store
        secret: str
        samesite: SameSite = SameSite.lax
        httponly: bool = True
        digest: str = HashAlgorithm.sha1.name
        TTL: int = 300
        cookie_name: str = 'sid'
        secure: bool = True
        salt: t.Optional[str] = None

    def __post_init__(self):
        self.manager = SignedCookieManager(
            self.config.store,
            self.config.secret,
            salt=self.config.salt,
            digest=self.config.digest,
            TTL=self.config.TTL,
            cookie_name=self.config.cookie_name,
        )

    def __call__(self, app, globalconf):

        def get_id(cookies):
            signed_sid = cookies.get(self.manager.cookie_name)
            if signed_sid is not None:
                try:
                    sid = self.manager.verify_id(signed_sid)
                    return str(sid, 'utf-8')
                except itsdangerous.exc.SignatureExpired:
                    # Session expired. We generate a new one.
                    pass
                except itsdangerous.exc.BadTimeSignature:
                    # Discrepancy in time signature.
                    # Invalid, generate a new one
                    pass

        def http_session_middleware(request):
            session = request.utilities.get('http_session')
            if session is None:
                sid = get_id(request.cookies)
                if sid is None:
                    new = True
                    sid = self.manager.generate_id()
                else:
                    new = False

                session = self.manager.session_factory(
                    sid, self.manager.store, new=new
                )
                request.utilities['http_session'] = session

            response = app(request)
            if session.modified or not session.new:
                if response.status < 400:
                    tm = request.utilities.get('transaction_manager')
                    if tm is None or not tm.isDoomed():
                        session.persist()
            domain = request.environ['HTTP_HOST'].split(':', 1)[0]
            cookie = self.manager.cookie(
                session.sid,
                request.script_name or '/',
                domain,
                secure=self.config.secure,
                samesite=self.config.samesite,
                httponly=self.config.httponly
            )
            response.cookies[self.manager.cookie_name] = cookie
            return response

        return http_session_middleware
