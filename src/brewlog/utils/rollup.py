import hashlib
import os
import subprocess
from dataclasses import dataclass
from typing import List, Mapping, Optional

from flask import Flask, current_app, request


def resolve_paths(root: str, leafs: List[str]) -> List[str]:
    return [os.path.join(root, e) for e in leafs]


def leaf_name(digest: str = None, *parts) -> str:
    path = os.path.join(*parts)
    if digest:
        root, ext = os.path.splitext(path)
        return f'{root}.{digest}{ext}'
    return path


@dataclass
class Bundle:
    name: str
    target_dir: str

    def hash_src(self) -> List[str]:
        return []

    def calc_hash(self):
        hash_src = '\n'.join(self.hash_src())
        return hashlib.sha256(hash_src.encode('utf-8')).hexdigest()[:10]


@dataclass
class SimpleBundle(Bundle):
    entrypoint: str
    output_path: Optional[str] = None

    def hash_src(self) -> List[str]:
        src = super().hash_src()
        src.extend([
            self.entrypoint,
            str(os.stat(self.entrypoint).st_mtime_ns),
        ])
        return src

    def set_output(self, paths: List[str]):
        self.output_path = paths[0]

    @property
    def entrypoints(self) -> List[str]:
        return {'': self.entrypoint}


@dataclass
class ChunkedBundle(Bundle):
    entrypoints: Mapping[str, str]
    output_paths: Optional[List[str]] = None

    def hash_src(self) -> List[str]:
        src = super().hash_src()
        for target, path in self.entrypoints.items():
            src.extend([
                target, path, str(os.stat(path).st_mtime_ns)
            ])
        return src

    def set_oputput(self, paths: List[str]):
        self.output_paths = paths


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
                endpoint_name = request.endpoint.split('.')[-1]
                if endpoint_name in self.bundles.keys():
                    subprocess.run(self.argv, check=True)

    def register(self, bundle: Bundle):
        self.bundles[bundle.name] = bundle
        app = self.app or current_app
        root = app.static_folder
        outputs = [
            resolve_paths(
                root,
                [leaf_name(bundle.target_dir, e) for e in bundle.entrypoints.values()]
            )
        ]
        bundle.set_output(outputs)
