from brewlog.utils.routing import UrlMap, Rule

rules = UrlMap([
    Rule('/pages/<path:path>',
        dict(endpoint='pages-page', view_func='brewlog.views.flatpage')),
    Rule('/auth/select',
        dict(endpoint='auth-select-provider', view_func='brewlog.users.views.auth.select_provider')),
    Rule('/auth/<provider>',
        dict(endpoint='auth-login', view_func='brewlog.users.views.auth.remote_login')),
    Rule('/auth/google/callback',
        dict(endpoint='auth-callback-google', view_func='brewlog.users.views.auth.google_remote_login_callback')),
    Rule('/auth/facebook/callback',
        dict(endpoint='auth-callback-facebook', view_func='brewlog.users.views.auth.facebook_remote_login_callback')),
    Rule('/auth/local/callback',
        dict(endpoint='auth-callback-local', view_func='brewlog.users.views.auth.local_login_callback')),
    Rule('/logout',
        dict(endpoint='auth-logout', view_func='brewlog.users.views.auth.logout')),
    Rule('/profile/all',
        dict(endpoint='profile-all', view_func='brewlog.users.views.profile.profile_list')),
    Rule('/profile/<int:userid>',
        dict(endpoint='profile-details', view_func='brewlog.users.views.profile.profile', methods=['POST', 'GET'])),
    Rule('/profile/<int:userid>/breweries',
        dict(endpoint='profile-breweries', view_func='brewlog.users.views.profile.breweries')),
    Rule('/profile/<int:userid>/brews',
        dict(endpoint='profile-brews', view_func='brewlog.users.views.profile.brews')),
    Rule('/profile/<int:userid>/extemplate',
        dict(endpoint='profile-export_template_add', view_func='brewlog.users.views.profile.export_template', methods=['POST', 'GET'], defaults={'tid': None})),
    Rule('/profile/<int:userid>/extemplate/<int:tid>',
        dict(endpoint='profile-export_template', view_func='brewlog.users.views.profile.export_template', methods=['POST', 'GET'])),
    Rule('/profile/<int:userid>/labeltemplate',
        dict(endpoint='profile-label_template_add', view_func='brewlog.users.views.profile.export_template', methods=['POST', 'GET'], defaults={'tid': None})),
    Rule('/profile/<int:userid>/labeltemplate/<int:tid>',
        dict(endpoint='profile-label_template', view_func='brewlog.users.views.profile.label_template', methods=['POST', 'GET'])),
    Rule('/brewery/add',
        dict(endpoint='brewery-add', view_func='brewlog.brewing.views.brewery.brewery_add', methods=['POST', 'GET'])),
    Rule('/brewery/all',
        dict(endpoint='brewery-all', view_func='brewlog.brewing.views.brewery.brewery_all')),
    Rule('/brewery/<int:brewery_id>',
        dict(endpoint='brewery-details', view_func='brewlog.brewing.views.brewery.brewery', methods=['POST', 'GET'])),
    Rule('/brewery/<int:brewery_id>/brews',
        dict(endpoint='brewery-brews', view_func='brewlog.brewing.views.brewery.brewery_brews')),
    Rule('/brewery/<int:brewery_id>/delete',
        dict(endpoint='brewery-delete', view_func='brewlog.brewing.views.brewery.brewery_delete', methods=['POST', 'GET'])),
    Rule('/brew/<int:brew_id>/tastingnote/add',
        dict(endpoint='brew-tastingnote-add', view_func='brewlog.brewing.views.brew.brew_add_tasting_note', methods=['POST', 'GET'])),
    Rule('/brew/tastingnote/<int:note_id>/delete',
        dict(endpoint='brew-tastingnote-delete', view_func='brewlog.brewing.views.brew.brew_delete_tasting_note', methods=['POST', 'GET'])),
    Rule('/brew/tastingnote/ajaxupdate',
        dict(endpoint='brew-tastingnote-update', view_func='brewlog.brewing.views.brew.brew_update_tasting_note', methods=['POST'])),
    Rule('/brew/tastingnote/ajaxtext',
        dict(endpoint='brew-tastingnote-loadtext', view_func='brewlog.brewing.views.brew.brew_load_tasting_note_text')),
    Rule('/brew/add',
        dict(endpoint='brew-add', view_func='brewlog.brewing.views.brew.brew_add', methods=['POST', 'GET'])),
    Rule('/brew/all',
        dict(endpoint='brew-all', view_func='brewlog.brewing.views.brew.brew_all')),
    Rule('/brew/<int:brew_id>',
        dict(endpoint='brew-details', view_func='brewlog.brewing.views.brew.brew', methods=['POST', 'GET'])),
    Rule('/brew/<int:brew_id>/delete',
        dict(endpoint='brew-delete', view_func='brewlog.brewing.views.brew.brew_delete', methods=['POST', 'GET'])),
    Rule('/export/brew/<int:brew_id>/<flavour>',
        dict(endpoint='brew-export', view_func='brewlog.brewing.views.brew.brew_export')),
    Rule('/print/brew/<int:brew_id>',
        dict(endpoint='brew-print', view_func='brewlog.brewing.views.brew.brew_print')),
    Rule('/print/brew/<int:brew_id>/labels',
        dict(endpoint='brew-print-labels', view_func='brewlog.brewing.views.brew.brew_labels')),
    Rule('/',
        dict(endpoint='main', view_func='brewlog.views.main')),
])
