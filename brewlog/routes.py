from brewlog.utils.routing import RouteMap, Route, RouteCluster

routes = RouteMap('brewlog', [
    Route('/', 'main', 'views.main'),
    Route('/pages/<path:path>', 'pages-page', 'views.flatpage'),
    RouteCluster(endpoint_prefix='auth-', submount='/auth', view_module='users.views.auth', rules=[
        Route('/select', 'select-provider', 'select_provider'),
        Route('/<provider>', 'login', 'remote_login'),
        Route('/google/callback', 'callback-gogle', 'google_remote_login_callback'),
        Route('/facebook/callback', 'callback-facebook', 'facebook_remote_login_callback'),
        Route('/local/callback', 'callback-local', 'local_login_callback'),
        Route('/logout', 'logout', 'logout'),
    ]),
    RouteCluster(endpoint_prefix='profile-', submount='/profile', view_module='users.views.profile', rules=[
        Route('/all', 'all', 'profile_list'),
        Route('/<int:userid>', 'details', 'profile', methods=['POST', 'GET']),
        Route('/<int:userid>/breweries', 'breweries', 'breweries'),
        Route('/<int:userid>/brews', 'brews', 'brews'),
        Route('/<int:userid>/extemplate', 'export_template_add', 'export_template', methods=['POST', 'GET'], defaults={'tid': None}),
        Route('/<int:userid>/extemplate/<int:tid>', 'export_template', 'export_template', methods=['POST', 'GET']),
        Route('/<int:userid>/lbtemplate', 'label_template_add', 'label_template',  methods=['POST', 'GET'], defaults={'tid': None}),
        Route('/<int:userid>/lbtemplate/<int:tid>', 'label_template', 'label_template', methods=['POST', 'GET']),
    ]),
    RouteCluster(endpoint_prefix='brewery-', submount='/brewery', view_module='brewing.views.brewery', rules=[
        Route('/add', 'add', 'brewery_add', methods=['POST', 'GET']),
        Route('/all', 'all', 'brewery_all'),
        Route('/<int:brewery_id>', 'details', 'brewery', methods=['POST', 'GET']),
        Route('/<int:brewery_id>/brews', 'brews', 'brewery_brews'),
        Route('/<int:brewery_id>/delete', 'delete', 'brewery_delete', methods=['POST', 'GET']),
    ]),
    RouteCluster(endpoint_prefix='brew-', submount='/brew', view_module='brewing.views.brew', rules=[
        Route('/<int:brew_id>/tastingnote/add', 'tastingnote-add', 'brew_add_tasting_note', methods=['POST', 'GET']),
        Route('/tastingnote/<int:note_id>/delete', 'tastingnote-delete', 'brew_delete_tasting_note', methods=['POST', 'GET']),
        Route('/tastingnote/ajaxupdate', 'tastingnote-update', 'brew_update_tasting_note', methods=['POST']),
        Route('/tastingnote/ajaxtext', 'tastingnote-loadtext', 'brew_load_tasting_note_text'),
        Route('/add', 'add', 'brew_add', methods=['POST', 'GET']),
        Route('/all', 'all', 'brew_all'),
        Route('/<int:brew_id>', 'details', 'brew', methods=['POST', 'GET']),
        Route('/<int:brew_id>/delete', 'delete', 'brew_delete', methods=['POST', 'GET']),
        Route('/<int:brew_id>/export/<flavour>', 'export', 'brew_export'),
        Route('/<int:brew_id>/print', 'print', 'brew_print'),
        Route('/<int:brew_id>/labels', 'print-labels', 'brew_labels'),
    ]),
])
