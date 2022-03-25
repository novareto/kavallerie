import importscan
import itertools
import typing as t
import importlib
import logging
import types
from collections import namedtuple, defaultdict
from importlib.metadata import entry_points
from kavallerie.app import Application
from kavallerie.registries import Blueprint
from kavallerie.utils import unique


Logger = logging.getLogger(__name__)
Registry = t.TypeVar('Registry')
Blueprints = t.Mapping[str, t.Union[Blueprint, t.Tuple[Blueprint]]]
Hook = t.Callable[['Plugin', Application], t.NoReturn]


class Plugin:

    name: str
    dependencies: t.Iterable[str]
    modules: t.Optional[t.Iterable[types.ModuleType]] = None
    blueprints: t.Optional[t.NamedTuple] = None

    _hooks: t.Dict[str, Hook]

    def __init__(
            self,
            name: str,
            modules: t.Optional[t.Iterable[str]] = None,
            blueprints: t.Optional[Blueprints] = None,
            dependencies: t.Optional[t.Iterable[str]] = None
    ):
        self.name = name
        if modules is not None:
            modules = tuple((importlib.import_module(m) for m in modules))
        self.modules = modules
        if dependencies is None:
            self.dependencies = tuple()
        else:
            self.dependencies = tuple(dependencies)
        self._hooks = defaultdict(list)
        if blueprints:
            self.blueprints = namedtuple(
                'Blueprints', blueprints.keys())(*blueprints.values())

    @unique
    def __lineage__(self) -> t.Tuple:

        def unfiltered_lineage():
            if not self.dependencies:
                return
            for dependency in self.dependencies:
                yield from dependency.__lineage__
                yield dependency

        def filtering():
            seen = set()
            for parent in unfiltered_lineage():
                if parent not in seen:
                    seen.add(parent)
                    yield parent
            if self not in seen:
                yield self
            del seen
        return tuple(filtering())

    def __repr__(self):
        return f'<Plugin {self.name!r}>'

    def before_install(self, func: Hook) -> Hook:
        self._hooks['before_install'].append(func)
        return func

    def after_install(self, func: Hook) -> Hook:
        self._hooks['after_install'].append(func)
        return func

    def before_uninstall(self, func: Hook) -> Hook:
        self._hooks['before_uninstall'].append(func)
        return func

    def after_uninstall(self, func: Hook) -> Hook:
        self._hooks['after_uninstall'].append(func)
        return func

    def uninstall(self, app: Application) -> Application:
        raise NotImplementedError('Uninstall is not yet implemented.')

    def install(self, app: Application) -> Application:
        installed = getattr(app, '__installed_plugins__', None)
        if installed is None:
            installed = app.__installed_plugins__ = set()
        elif self.name in installed:
            Logger.debug(f'{self.name!r} already installed: skip.')
            return

        for dep in self.dependencies:
            dep.install(app)

        try:
            if 'before_install' in self._hooks:
                for hook in self._hooks['before_install']:
                    hook(self, app)
            if self.modules is not None:
                for module in self.modules:
                    importscan.scan(module)
            if self.blueprints:
                for name, blueprints in self.blueprints._asdict().items():
                    if isinstance(blueprints, Blueprint):
                        blueprints = [blueprints]
                    target = getattr(app, name, None)
                    if target is None:
                        raise LookupError(
                            f'Unknown target registry {name} on {app}.')
                    for blueprint in blueprints:
                        blueprint.apply(target)
            if 'after_install' in self._hooks:
                for hook in self._hooks['after_install']:
                    hook(self, app)
        except Exception:
            Logger.error(
                f"An error occured while installing plugin {self.name}.",
                exc_info=True
            )
            raise
        else:
            installed.add(self.name)
            Logger.info(f"Plugin {self.name} installed with success.")
        return app

    __call__ = install



class Plugins:

    _store: t.Mapping[str, Plugin]
    ordered: t.Iterable[str]

    def __init__(self, candidates: t.Iterable[Plugin]):
        self._store = dict(
            (candidate.name, candidate) for candidate in candidates
        )

    @classmethod
    def from_entrypoints(cls, key='kavallerie.plugins'):
        def entrypoints_plugins():
            eps = entry_points()
            if (plugin_definitions := eps.get(key)) is not None:
                for definition in plugin_definitions:
                    loaded = definition.load()
                    Logger.debug(
                        f"Loading plugin {loaded.name}."
                    )
                    yield loaded

        return cls(entrypoints_plugins())

    def install_by_name(self, app, *names):
        to_install = frozenset(names)
        available = frozenset(self._store.keys())
        missing = to_install - available

        if missing:
            raise LookupError(f'Missing plugins: {", ".join(missing)!r}.')

        for name in names:
            self._store[name].install(app)

    def __call__(self, app, *plugins: Plugin):
        for plugin in plugins:
            plugin.install(app)
