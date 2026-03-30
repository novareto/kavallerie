import typing as t
import logging
from wrapt import ObjectProxy
from authsources.identity import User
from authsources.source import Source
from authsources.protocols import Challenge, Preflight, Getter
from authsources.authenticator import Authenticator
from kavallerie.meta import Request


logger = logging.getLogger("kavallerie.auth")


class ResolvedUser(ObjectProxy):
    source_id: str | None

    def __init__(self, user: User, source_id: str | None = None):
        super().__init__(user)
        self.source_id = source_id


class AuthenticationInfo(t.TypedDict):
    source_id: str
    user_id: str


class BaseAuthenticator(Authenticator):

    sources: dict[str, Source]

    def __init__(self, sources: t.Mapping[str, Source] | None = None):
        self.sources = dict(sources) if sources is not None else {}

    def challenge(
            self, request: Request, credentials: dict
    ) -> ResolvedUser | None:
        for source_id, source in self.sources.items():
            if action := source.get(Challenge):
                user = action.challenge(credentials)
                if user is not None:
                    return ResolvedUser(user, source_id=source_id)
        return None

    def identify(self, request: Request) -> ResolvedUser | None:
        for source_id, source in self.sources.items():
            if action := source.get(Preflight):
                logger.info(f'Preflight found: {source.title}')
                user = action.preflight(request)
                if user is not None:
                    logger.info(
                        f'Preflight user found by {source.title}: {user}.')
                    return ResolvedUser(user, source_id=source_id)
                logger.info('Authentication preflight unsuccessful.')

        logger.info('Authentication initiated.')
        if (info := self.get_stored_info(request)) is not None:
            source = self.sources[info['source_id']]
            if action := source.get(Getter):
                user = action.get(info['user_id'])
                if user is not None:
                    logger.info(
                        f"Source {info['source_id']} found: {user}")
                    return ResolvedUser(user, source_id=info['user_id'])

        return None

    def get_stored_info(self, request) -> AuthenticationInfo:
        pass

    def forget(self, request) -> None:
        pass

    def remember(self, request, source_id: str, user: User) -> None:
        pass


class HTTPSessionAuthenticator(BaseAuthenticator):

    user_key: str = "user"

    def __init__(self, *,
                 user_key: str = "user",
                 sources: t.Mapping[str, Source] | None = None):
        self.user_key = user_key
        super().__init__(sources=sources)

    def get_stored_info(self, request: Request) -> AuthenticationInfo:
        session = request.utilities['http_session']
        return session.get(self.user_key, None)

    def forget(self, request: Request) -> None:
        session = request.utilities['http_session']
        session.clear()
        request.user = None

    def remember(
            self, request: Request, source_id: str, user: User) -> None:
        session = request.utilities['http_session']
        session[self.user_key] = AuthenticationInfo(
            user_id=user.id,
            source_id=source_id
        )
        request.user = ResolvedUser(user, source_id=source_id)
