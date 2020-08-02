import glob
import hashlib
import os
import subprocess
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Optional

from flask import Flask, current_app, request


def resolve_path(root: str, path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(root, path)))


BundleOutput = namedtuple('BundleOutput', ['file_path', 'static_path', 'url'])


def bundle_url(name: str) -> str:
    pass


@dataclass
class Entrypoint:
    path: str
    name: str = ''

    def cmdline_param(self) -> List[str]:
        if self.name:
            return [f'{self.name}={self.path}']
        else:
            return ['-i', self.path]


@dataclass
class Bundle:
    name: str
    target_dir: str
    entrypoints: List[Entrypoint]
    dependencies: List[str] = field(default_factory=list)
    output: Optional[BundleOutput] = None

    def resolve_paths(self, root: str):
        for ep in self.entrypoints:
            ep.path = resolve_path(root, ep.path)
        self.target_dir = resolve_path(root, self.target_dir)
        for index, dep in enumerate(self.dependencies):
            self.dependencies[index] = resolve_path(root, dep)

    def hash_src(self) -> List[str]:
        src = []
        for ep in self.entrypoints:
            src.extend([
                ep.name, ep.path, str(os.stat(ep.path).st_mtime_ns)
            ])
        for dep in self.dependencies:
            src.extend([
                dep, str(os.stat(dep).st_mtime_ns)
            ])
        return src

    def calc_hash(self):
        hash_src = '\n'.join(self.hash_src())
        return hashlib.sha256(hash_src.encode('utf-8')).hexdigest()[:10]

    def argv(self):
        rv = []
        for ep in self.entrypoints:
            rv.extend(ep.cmdline_param())
        return rv

    def resolve_output(self, root: str, url_path: str):
        files = glob.glob(f'{root}/**/{self.name}.*.js')
        if len(files) == 1:
            output_path = files[0]
            path = output_path.replace(f'{root}/', '')
            url = os.path.join(url_path, path)
            self.output = BundleOutput(output_path, path, url)


class Rollup:

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.bundles = {}
        self.argv = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        app.config.setdefault('ROLLUP_PATH', 'rollup')
        self.argv = [app.config['ROLLUP_PATH']]
        rollup_config_js = app.config.get('ROLLUP_CONFIG_JS')
        if rollup_config_js:
            self.argv.extend(['-c', rollup_config_js])
        else:
            self.argv.append('-c')
        if os.environ.get('FLASK_ENV', 'production') != 'production':
            @app.before_request
            def run_rollup():
                self.run_rollup()
        app.extensions['rollup'] = self

        @app.template_global(name='jsbundle')
        def template_func(name: str):
            for b_name, bundle in self.bundles.items():
                if b_name == name:
                    return bundle.output.url

    def register(self, bundle: Bundle):
        self.bundles[bundle.name] = bundle
        app = self.app or current_app
        bundle.resolve_paths(app.static_folder)

    def run_rollup(self):
        if request.endpoint in self.bundles.keys():
            bundle = self.bundles[request.endpoint]
            argv = self.argv.copy()
            argv.extend(bundle.argv())
            environ = os.environ.copy()
            environ['NODE_ENV'] = environ['FLASK_ENV']
            subprocess.run(
                argv, check=True, env=environ,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            app = self.app or current_app
            bundle.resolve_output(app.static_folder, app.static_url_path)
