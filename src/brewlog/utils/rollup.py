import glob
import hashlib
import os
import subprocess
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Mapping, Optional, Union

from flask import Flask, request


def resolve_path(*parts) -> str:
    """Join path parts and normalise resulting path.

    Returns:
        str: normalised file system path
    """
    return os.path.normpath(os.path.abspath(os.path.join(*parts)))


BundleOutput = namedtuple('BundleOutput', ['file_path', 'static_path', 'url'])


class RollupBundlerError(Exception):
    """Base exception of this package.
    """
    pass


class BundleDefinitionError(RollupBundlerError):
    """Exception raised if bundle definition is invalid.
    """
    pass


@dataclass
class Entrypoint:
    """Entrypoint information: path and name.
    """
    path: str
    name: str = ''

    def cmdline_param(self) -> str:
        """Generate command line param from name and path.

        Returns:
            str: Rollup command line param
        """
        return f'{self.name}={self.path}'


@dataclass
class Bundle:
    """Javascript bundle definition. Required arguments are ``name``, ``target_dir``
    and ``entrypoints``. If any of entrypoints has a dependency on non-installed module,
    it should be listed in ``dependencies``. These modules are used to calculate state
    of the bundle and failing to include them may result in bundle not being rebuilt
    if they change.

    Bundles should be named after Flask app endpoints for effective code splitting, eg.
    Javascript module used on page ``auth.login`` should be placed in a bundle named
    ``auth.login``. Upon bundling the result will be in file
    ``target_dir/auth.login.[hash].js``, and corresponding source map in file
    ``target_dir/auth.login.[hash].js.map``. This is required to use ``jsbundle`` in
    templates and to have working auto rebuild in development mode.

    In simplest case of single entrypoint it may be specified as string denoting path
    relative to app static folder. In any case bundle can have only one unnamed
    entrypoint and this condition is validated during bundle registration.

    Args:
        name: name of the bundle
        target_dir: where the output will be stored, relative to static directory root
        entrypoints: list of bundle entrypoints
        dependencies: list of entrypoint's dependencies that will be included in bundle

    Raises:
        BundleDefinitionError: if definition contains more than 1 unnamed entrypoint
    """
    name: str
    target_dir: str
    entrypoints: List[Union[Entrypoint, str]]
    dependencies: List[str] = field(default_factory=list)
    state: Optional[str] = field(default=None, init=False)
    output: Optional[BundleOutput] = field(default=None, init=False)

    def __post_init__(self):
        entrypoints = []
        found = 0
        for ep in self.entrypoints:
            if isinstance(ep, str):
                if found > 0:
                    raise BundleDefinitionError('Simple entrypoint already defined')
                entrypoints.append(Entrypoint(path=ep, name=self.name))
                found += 1
                continue
            if not ep.name:
                if found > 0:
                    raise BundleDefinitionError('Simple entrypoint already defined')
                ep.name = self.name
                entrypoints.append(ep)
                found += 1
        self.entrypoints = entrypoints

    def resolve_paths(self, root: str):
        """Make bundle paths absolute and normalized.

        Args:
            root: root path (application static folder path)
        """
        for ep in self.entrypoints:
            ep.path = resolve_path(root, ep.path)
        self.target_dir = resolve_path(root, self.target_dir)
        for index, dep in enumerate(self.dependencies):
            self.dependencies[index] = resolve_path(root, dep)

    def calc_state(self) -> str:
        """Calculate bundle state checksum. This is used to determine if bundle should
        be rebuild in development mode. For each input path (entrypoints and
        dependencies) file mtime is used as a base of calculation.

        Returns:
            str: bundle state checksum
        """
        src = [str(os.stat(ep.path).st_mtime_ns) for ep in self.entrypoints]
        src.extend([str(os.stat(d.path).st_mtime_ns) for d in self.dependencies])
        return hashlib.sha256('\n'.join(src).encode('utf-8')).hexdigest()

    def argv(self) -> List[str]:
        """Return list of Rollup command line params required to build the bundle.

        Returns:
            List[str]: list of command line param tokens
        """
        rv = ['-d', self.target_dir]
        for ep in self.entrypoints:
            rv.extend(ep.cmdline_param())
        return rv

    def resolve_output(self, root: str, url_path: str):
        """Determine bundle's generation output paths (both absolute file system path
        and relative to static folder) and url.

        Args:
            root: static content root directory (application static folder)
            url_path: path to static content
        """
        files = glob.glob(f'{root}/**/{self.name}.*.js')
        if len(files) == 1:
            output_path = files[0]
            path = output_path.replace(f'{root}/', '')
            url = os.path.join(url_path, path)
            self.output = BundleOutput(output_path, path, url)


@dataclass
class Rollup:
    """Rollup integration with Flask. Extension can be registered in both simple way
    and using application factory and ``init_app(app)`` pattern.
    """
    app: Optional[Flask] = None
    bundles: Mapping[str, Bundle] = field(default_factory=dict, init=False)
    argv: List[str] = field(default_factory=list, init=False)
    mode_production: bool = field(default=True, init=False)
    static_folder: Optional[str] = field(default=None, init=False)
    static_url_path: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        if self.app:
            self.init_app(self.app)

    def init_app(self, app: Flask):
        """Initialise application. This function sets up required configuration
        defaults and initial Rollup command line args. In non-production mode
        autorebuild is enabled. Template function ``jsbundle`` is registered here
        as Jinja2 global object.

        Args:
            app: application object
        """
        self.mode_production = os.environ.get('FLASK_ENV', 'production') == 'production'
        self.static_folder = app.static_folder
        self.static_url_path = app.static_url_path
        app.config.setdefault('ROLLUP_PATH', 'rollup')
        self.argv = [app.config['ROLLUP_PATH']]
        rollup_config_js = app.config.get('ROLLUP_CONFIG_JS')
        if rollup_config_js:
            self.argv.extend(['-c', rollup_config_js])
        else:
            self.argv.append('-c')

        if not self.mode_production:
            @app.before_request
            def run_rollup():
                if request.endpoint in self.bundles:
                    self.run_rollup(request.endpoint)

        @app.template_global(name='jsbundle')
        def template_func(name: str):
            bundle = self.bundles[name]
            return bundle.output.url

    def register(self, bundle: Bundle):
        """Register bundle. At this moment input paths are resolved.

        Args:
            bundle: bundle object to be registered
        """
        self.bundles[bundle.name] = bundle
        bundle.resolve_paths(self.static_folder)

    def run_rollup(self, bundle_name: str):
        """Run Rollup bundler over specified bundle is bundle state changed. Once
        Rollup finishes bundle's output is resolved (paths and url).

        Args:
            bundle_name: name of the bundle to be rebuilt
        """
        bundle = self.bundles[bundle_name]
        new_state = bundle.calc_state()
        if bundle.state != new_state:
            argv = self.argv.copy()
            argv.append(bundle.argv())
            environ = os.environ.copy()
            environ['NODE_ENV'] = environ['FLASK_ENV']
            kw = {}
            if not self.mode_production:
                kw.update({
                    'stdout': subprocess.DEVNULL,
                    'stderr': subprocess.DEVNULL,
                })
            subprocess.run(argv, check=True, env=environ, **kw)
            bundle.resolve_output(self.static_folder, self.static_url_path)
            bundle.state = new_state
