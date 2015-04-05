from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect

class LoginRequiredMiddleware(object):
    """Middleware to redirect to the login page if the user isn't authenticated

    After successful authentication the user is redirected back to the page he
    initially wanted to access.
    """
    def process_request(self, request):
        # allow access to the login url
        if request.path == settings.LOGIN_URL:
            return
        # redirect to the login url if the user isn't authenticated
        if not request.user.is_authenticated():
            if request.path not in (settings.LOGIN_URL,
                                    settings.LOGIN_REDIRECT_URL):
                return HttpResponseRedirect('%s?%s=%s' % (settings.LOGIN_URL,
                                                          REDIRECT_FIELD_NAME,
                                                          request.path))
            else:
                return HttpResponseRedirect(settings.LOGIN_URL)
