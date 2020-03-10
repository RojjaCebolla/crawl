import tornado.web
import tornado.websocket


class RequestHandler(tornado.web.RequestHandler):
    pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    pass


class StaticFileHandler(tornado.web.StaticFileHandler):
    pass
