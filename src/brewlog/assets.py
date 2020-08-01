from flask_assets import Bundle

from .utils.rollup import SimpleBundle

all_css = Bundle(
    'css/app.scss', filters='node-scss,cleancss', output='dist/all.%(version)s.min.css',
)

dashboard_js = SimpleBundle(
    name='dashboard', target_dir='dist', entrypoint='js/dashboard.js'
)
