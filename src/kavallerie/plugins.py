try:
    import networkx
    import importscan
except ImportError:
    raise RuntimeError('Plugins require `networkx`.')

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

    def on_install(self, func: Hook) -> Hook:
        self._hooks['on_install'].append(func)
        return func

    def on_uninstall(self, func: Hook) -> Hook:
        self._hooks['on_uninstall'].append(func)
        return func

    def install(self, app: Application):
        installed = getattr(app, '__installed_plugins__', None)
        if installed is None:
            installed = app.__installed_plugins__ = set()
        elif self.name in installed:
            print('already installed, skip')
            return
        try:
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
            if 'on_install' in self._hooks:
                for hook in self._hooks['on_install']:
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


class Plugins:

    logger: logging.Logger
    _store: t.Mapping[str, Plugin]
    ordered: t.Iterable[str]

    def __init__(self, candidates: t.Iterable[Plugin]):
        stack = {}
        plugins = {}
        for candidate in candidates:
            for plugin in candidate.__lineage__:
                existing = plugins.get(plugin.name)
                if existing is None:
                    plugins[plugin.name] = plugin
                elif existing is not plugin:
                    raise KeyError(
                        f'Trying to register {plugin!r} as {plugin.name}.'
                        f'This name is already taken by {existing!r}.'
                    )
                stack[plugin.name] = [
                    dep.name for dep in plugin.dependencies]

        graph = networkx.DiGraph(stack)
        if not networkx.is_directed_acyclic_graph(graph):
            raise LookupError(
                'Registered plugins create a circular dependency graph.')

        self._store = plugins
        self.ordered = tuple(reversed(
            tuple(networkx.topological_sort(graph))
        ))

    @classmethod
    def from_entrypoints(cls, key='kavallerie.plugins'):
        def entrypoints_plugins():
            eps = entry_points()
            if (plugin_definitions := eps.get(key)) is not None:
                for definition in plugin_definitions:
                    yield definition.load()
        return cls(entrypoints_plugins())

    def apply(self, app, *names):
        to_install = frozenset(names)
        available = frozenset(self.ordered)
        missing = to_install - available

        if missing:
            raise LookupError(f'Missing plugins: {", ".join(missing)!r}.')

        plugins = {
            plugin.name: plugin for plugin in itertools.chain(*(
                self._store[name].__lineage__ for name in names))
        }
        Logger.info(
            f'Plugins needs installing: {", ".join(plugins.keys())}')
        print(self.ordered)
        for name in self.ordered:
            if name in plugins:
                plugins[name].install(app)
