from flask_assets import Bundle

from .utils.rollup import Bundle as RollupBundle, Entrypoint

all_css = Bundle(
    'css/app.scss', filters='node-scss,cleancss', output='dist/all.%(version)s.min.css',
)

dashboard_js = RollupBundle(
    name='home.dashboard', target_dir='dist',
    entrypoints=[Entrypoint('js/dashboard.js', name='home.dashboard')],
)
