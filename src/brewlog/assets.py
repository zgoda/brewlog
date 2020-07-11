from flask_assets import Bundle


cirrus_css = Bundle(
    'vendor/cirrus/src/core/*', 'vendor/cirrus/src/ext/*', 'vendor/cirrus/src/utils/*',
    filters='node-scss', output='dist/cirrus.css',
)

all_css = Bundle(
    cirrus_css, 'css/app.css',
    'vendor/fontawesome/css/all.css', 'vendor/autocomplete/autocomplete.css',
    filters='cleancss', output='dist/all.min.css',
)
