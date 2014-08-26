from brewlog.utils.routing import RouteMap, Route

routes = RouteMap('brewlog', [
    Route('/', 'main', 'views.main'),
    Route('/pages/<path:path>', 'pages-page', 'views.flatpage'),
])
