#!/usr/bin/python

'''@base_data

This file stores user sessions into the redis-server.

    - http://flask.pocoo.org/snippets/75/
    - https://github.com/mrichman/flask-redis/blob/master/redissession.py

'''

import pickle
import redis
from datetime import timedelta
from uuid import uuid4
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, prefix='session:'):
        # local variables
        host = 'localhost'
        port = 6379
        db_num = 0

        pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db_num
        )

        redis_instance = redis.StrictRedis(connection_pool=pool)

        # class variables
        self.redis = redis_instance
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)

        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)

        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)

        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(
                    app.session_cookie_name,
                    domain=domain
                )
            return

        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)

        val = self.serializer.dumps(dict(session))
        self.redis.setex(
            self.prefix + session.sid,
            val,
            int(redis_exp.total_seconds())
        )

        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=cookie_exp,
            httponly=True,
            domain=domain
        )