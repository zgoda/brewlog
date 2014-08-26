from brewlog.utils.routing import RouteMap, Route, RouteCluster

routes = RouteMap('brewlog', [
    Route('/', 'main', 'views.main'),
    Route('/pages/<path:path>', 'pages-page', 'views.flatpage'),
    RouteCluster(endpoint_prefix='auth-', submount='/auth', view_module='users.views.auth', rules=[
        Route('/select', 'select-provider', 'select_provider'),
        Route('/<provider>', 'login', 'remote_login'),
        Route('/google/callback', 'callback-google', 'google_remote_login_callback'),
        Route('/facebook/callback', 'callback-facebook', 'facebook_remote_login_callback'),
        Route('/github/callback', 'callback-github', 'github_remote_login_callback'),
        Route('/local/callback', 'callback-local', 'local_login_callback'),
        Route('/logout', 'logout', 'logout'),
    ]),
    RouteCluster(endpoint_prefix='profile-', submount='/profile', view_module='users.views.profile', rules=[
        Route('/all', 'all', 'profile_list'),
        Route('/<int:userid>', 'details', 'profile', methods=['POST', 'GET']),
        Route('/<int:userid>/delete', 'delete', 'profile_delete', methods=['POST', 'GET']),
        Route('/<int:userid>/breweries', 'breweries', 'breweries'),
        Route('/<int:userid>/brews', 'brews', 'brews'),
        Route('/<int:userid>/extemplate', 'export_template_add', 'export_template', methods=['POST', 'GET'], defaults={'tid': None}),  # NOQA
        Route('/<int:userid>/extemplate/<int:tid>', 'export_template', 'export_template', methods=['POST', 'GET']),
        Route('/<int:userid>/lbtemplate', 'label_template_add', 'label_template', methods=['POST', 'GET'], defaults={'tid': None}),  # NOQA
        Route('/<int:userid>/lbtemplate/<int:tid>', 'label_template', 'label_template', methods=['POST', 'GET']),
        Route('/<int:userid>/rcal', 'remote_calendar_add', 'remote_calendar', methods=['POST', 'GET'], defaults={'cid': None}),  # NOQA
        Route('/<int:userid>/rcal/<int:cid>', 'remote_calendar', 'remote_calendar', methods=['POST', 'GET']),
    ]),
    RouteCluster(endpoint_prefix='tastingnote-', submount='/tastingnote', view_module='tasting.views', rules=[
        Route('/all', 'all', 'all'),
        Route('/<int:brew_id>/add', 'add', 'brew_add_tasting_note', methods=['POST', 'GET']),
        Route('/<int:note_id>/delete', 'delete', 'brew_delete_tasting_note', methods=['POST', 'GET']),
        Route('/ajaxupdate', 'update', 'brew_update_tasting_note', methods=['POST']),
        Route('/ajaxtext', 'loadtext', 'brew_load_tasting_note_text'),
    ]),
])
