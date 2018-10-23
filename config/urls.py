from os.path import join
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.views.decorators.cache import never_cache
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    from django.contrib.staticfiles.storage import staticfiles_storage
    from django.views.generic.base import RedirectView
    # favicon_url = staticfiles_storage.url('favicon/')
    favicon_url = join(str(settings.ROOT_DIR), 'lime_test/static/favicon/')
    urlpatterns += [
        url(r'^favicon\.ico$', serve, {'document_root': favicon_url, 'path': 'favicon.ico'}),
        url(r'^apple-touch-icon\.png$', serve, {'document_root': favicon_url, 'path': 'apple-touch-icon.png'}),
        url(r'^favicon-32x32\.png$', serve, {'document_root': favicon_url, 'path': 'favicon-32x32.png'}),
        url(r'^favicon-16x16\.png$', serve, {'document_root': favicon_url, 'path': 'favicon-16x16.png'}),
        url(r'^manifest\.json$', serve, {'document_root': favicon_url, 'path': 'manifest.json'}),
        url(r'^safari-pinned-tab\.svg$', serve, {'document_root': favicon_url, 'path': 'safari-pinned-tab.svg'}),

        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
