import tornado.web
import tornado.websocket

import auth
import userdb


class AuthRequiredMixin():
    """Mixin for RequestHandlers requiring user login."""

    def get_current_user(self):
        cookie = self.get_cookie('login', '').replace('%20', ' ')
        username, ok = auth.check_login_cookie(cookie)
        if not ok:
            raise tornado.web.HTTPError(401)
        return userdb.get_user_info(username)


class AdminOnlyMixin(AuthRequiredMixin):
    """Mixin for RequestHandlers accessible to administrators only."""

    def get_current_user(self):
        user = super(AdminOnlyMixin, self).get_current_user()
        if not user.is_admin:
            raise tornado.web.HTTPError(403)
        return user


class RequestHandler(tornado.web.RequestHandler):
    pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    pass


class StaticFileHandler(tornado.web.StaticFileHandler):
    pass
