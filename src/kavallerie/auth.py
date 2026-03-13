import typing as t
import logging
from authsources.abc.identity import User
from authsources.abc.source import Source
from authsources.abc.actions import Challenge, Preflight, Getter
from authsources.abc import Authenticator
from kavallerie.meta import Request


logger = logging.getLogger("kavallerie.auth")


class AuthenticationInfo(t.TypedDict):
    source_id: str
    user_id: str


class BaseAuthenticator(Authenticator):

    sources: dict[str, Source]

    def __init__(self, sources: t.Mapping[str, Source] | None = None):
        self.sources = dict(sources) if sources is not None else {}

    def challenge(
            self, request: Request, credentials: dict
    ) -> tuple[str, User] | tuple[None, None]:
        for source_id, source in self.sources.items():
            if action := source.get(Challenge):
                user = action.challenge(credentials)
                if user is not None:
                    return source_id, user
        return None, None

    def identify(self, request: Request) -> User | None:
        for source in self.sources.values():
            if action := source.get(Preflight):
                logger.info(f'Preflight found: {source.title}')
                user = action.preflight(request)
                if user is not None:
                    logger.info(
                        f'Preflight user found by {source.title}: {user}.')
                    return user
                logger.info('Authentication preflight unsuccessful.')

        logger.info('Authentication initiated.')
        if (info := self.get_stored_info(request)) is not None:
            source = self.sources[info['source_id']]
            if action := source.get(Getter):
                user = action.get(info['user_id'])
                if user is not None:
                    logger.info(
                        f"Source {info['source_id']} found: {user}")
                    return user

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
        request.user = user
