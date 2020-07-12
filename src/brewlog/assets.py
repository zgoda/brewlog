from flask_assets import Bundle


all_css = Bundle(
    'css/app.scss', filters='node-scss,cleancss', output='dist/all.min.css',
)
