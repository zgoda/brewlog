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
    RouteCluster(endpoint_prefix='brew-', submount='/brew', view_module='brew.views', rules=[
        Route('/add', 'add', 'brew_add', methods=['POST', 'GET']),
        Route('/all', 'all', 'brew_all'),
        Route('/<int:brew_id>', 'details', 'brew', methods=['POST', 'GET']),
        # fermentation steps
        Route('/<int:brew_id>/fermentationstep/add', 'fermentationstep_add', 'fermentation_step_add', methods=['POST', 'GET']),  # NOQA
        Route('/fermentationstep/<int:fstep_id>', 'fermentation_step', 'fermentation_step', methods=['GET', 'POST']),
        Route('/fermentationstep/<int:fstep_id>/delete', 'fermentationstep_delete', 'fermentation_step_delete', methods=['GET', 'POST']),  # NOQA
        # events
        Route('/<int:brew_id>/event/add', 'brewevent_add', 'brew_event_add', methods=['POST']),
        Route('/event/<int:event_id>', 'brew_event', 'brew_event', methods=['GET', 'POST']),
        Route('/event/<int:event_id>/delete', 'brewevent_delete', 'brew_event_delete', methods=['GET', 'POST']),
        # operations on brew item
        Route('/<int:brew_id>/delete', 'delete', 'brew_delete', methods=['POST', 'GET']),
        Route('/<int:brew_id>/export/<flavour>', 'export', 'brew_export'),
        Route('/<int:brew_id>/print', 'print', 'brew_print'),
        Route('/<int:brew_id>/labels', 'print-labels', 'brew_labels'),
    ]),
    RouteCluster(endpoint_prefix='tastingnote-', submount='/tastingnote', view_module='tasting.views', rules=[
        Route('/all', 'all', 'all'),
        Route('/<int:brew_id>/add', 'add', 'brew_add_tasting_note', methods=['POST', 'GET']),
        Route('/<int:note_id>/delete', 'delete', 'brew_delete_tasting_note', methods=['POST', 'GET']),
        Route('/ajaxupdate', 'update', 'brew_update_tasting_note', methods=['POST']),
        Route('/ajaxtext', 'loadtext', 'brew_load_tasting_note_text'),
    ]),
])
