from flask_assets import Bundle
from webassets.filter import register_filter
from webassets_rollup import Rollup

register_filter(Rollup)

all_css = Bundle(
    'css/app.scss', filters='node-scss,cleancss', output='dist/all.%(version)s.min.css',
)

dashboard_js = Bundle(
    'js/dashboard.js', filters='rollup', output='dist/dashboard.min.js',
)
