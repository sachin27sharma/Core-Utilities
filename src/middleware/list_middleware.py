from fastapi import FastAPI
from typing import List, Callable


class MiddlewareList:
    def __init__(self):
        self.middlewares = []

    def add(self, middleware_class: Callable, *args, **kwargs):
        self.middlewares.append((middleware_class, args, kwargs))

    def apply(self, app: FastAPI):
        for middleware_class, args, kwargs in self.middlewares:
            app.add_middleware(middleware_class, *args, **kwargs)
