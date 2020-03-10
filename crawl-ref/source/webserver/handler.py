import tornado.web
import tornado.websocket

import auth
import config
import userdb


class _CheckAuthMixin(object):

    def get_current_user(self):
        cookie = self.get_cookie('login', '').replace('%20', ' ')
        username, ok = auth.check_login_cookie(cookie)
        if not ok:
            raise tornado.web.HTTPError(401)
        return userdb.get_user_info(username)


class _AutoLoginMixin(object):
    """Automatically logs in as the user set in config.autologin."""

    def get_current_user(self):
        autologin = getattr(config, "autologin", None)
        if autologin:
            auth.log_in_as_user(self, autologin)
        user = userdb.get_user_info(autologin) if autologin else None
        return user or super(_AutoLoginMixin, self).get_current_user()


class AuthRequiredMixin(_AutoLoginMixin, _CheckAuthMixin):
    """Mixin for RequestHandlers requiring user login."""
    pass


class AdminOnlyMixin(AuthRequiredMixin):
    """Mixin for RequestHandlers accessible to administrators only."""

    def get_current_user(self):
        user = super(AdminOnlyMixin, self).get_current_user()
        if not user.is_admin:
            raise tornado.web.HTTPError(403)
        return user


class RequestHandler(_AutoLoginMixin, tornado.web.RequestHandler):
    pass


class WebSocketHandler(_AutoLoginMixin, tornado.websocket.WebSocketHandler):
    pass


class StaticFileHandler(_AutoLoginMixin, tornado.web.StaticFileHandler):
    pass
