import time

import tornado.web

import config
import handler
import rebuild
import userdb


class BuildLogHandler(handler.AdminOnlyMixin, handler.RequestHandler):
    """Handler for showing crawl build logs."""

    def get(self, version):
        getattr(self, 'xsrf_token')  # Hack to force cookie generation.
        self.render("rebuild.html", version=version)


class RebuildHandler(handler.AdminOnlyMixin, handler.RequestHandler):
    """Handler for crawl rebuilds."""

    def post(self, version):
        rebuild.trigger_rebuild(version)


class TailBuildLogHandler(handler.AdminOnlyMixin, handler.RequestHandler):
    """Handler for crawl rebuilds."""

    @tornado.web.asynchronous
    def get(self, version):
        self.proc = subprocess.Popen(
            ["tail", "-f", rebuild._get_log_path_for_version(version), "-n+1"],
            stdout=subprocess.PIPE)

        self.stream = tornado.iostream.PipeIOStream(self.proc.stdout.fileno())
        self.stream.read_until("\n", self.on_line)

    def on_line(self, data):
        self.write(data)
        self.flush()
        self.stream.read_until("\n", self.on_line)

    def on_connection_close(self, *args, **kwargs):
        self.proc.terminate()
        super(TailBuildLogHandler, self).on_connection_close(*args, **kwargs)


class AdminHandler(handler.AdminOnlyMixin, handler.RequestHandler):
    """Handler for main admin panel.

    Currently this shows the set of crawl binaries that can be rebuilt.
    """

    def get(self):
        self.render("admin.html",
                    config=config,
                    rebuild_targets=self._get_rebuild_targets())

    def _get_rebuild_targets(self):
        dedup_games = {}
        for game_id, game in config.games.items():
            if game['crawl_binary'] not in dedup_games:
                dedup_games[game['crawl_binary']] = game_id

        return {
            game_id.replace('dcss-', ''): config.games[game_id]['name']
            for game_id in dedup_games.values()
        }
