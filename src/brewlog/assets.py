from flask_assets import Bundle
from flask_rollup import Bundle as RollupBundle

all_css = Bundle(
    'css/app.scss', filters='node-scss,cleancss', output='dist/all.%(version)s.min.css',
)

dashboard_js = RollupBundle(
    name='home.dashboard', target_dir='dist', entrypoints=['js/dashboard.js'],
    dependencies=['js/components/forms.js'],
)
