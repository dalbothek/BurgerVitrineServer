# -*- coding: utf8 -*-
import os.path as path


class Resource(object):
    PATH = None

    def __init__(self, name):
        if name == "latest":
            name = JARResource.latest(0)
        self.name = name

    def path(self):
        return path.join(self.PATH, self.name)

    def exists(self):
        return path.exists(self.path())

    def generate(self):
        raise NotImplementedError()

    def _generate(self):
        with open(self.path(), "w") as f:
            f.write(self.generate())

    def generate_if_needed(self):
        if not self.exists():
            self._generate()

    def read(self):
        self.generate_if_needed()
        with open(self.path(), "r") as f:
            return f.read()

    def render(self):
        return self.read()

    def render_error(self, error):
        return str(error)


class GenerationException(Exception):
    def __init__(self, message=None):
        if msg is None:
            msg = "An error occurred when generating the requested resource"
        super(NotFoundException, self).__init__(msg)


class NotFoundException(Exception):
    def __init__(self):
        super(NotFoundException, self).__init__(
            "The requested resource was not found."
        )


class JARResource(Resource):
    PATH = "jar"

    def generate(self):
        raise NotFoundException()

    @classmethod
    def latest(cls, i):
        return "1.4.5"


class JSONResource(Resource):
    PATH = "json"

    def generate(self):
        return "[\"success\", \"%s\"]" % self.name


class HTMLResource(Resource):
    PATH = "html"

    def generate(self):
        return "<h1>Success</h1><h3>%s</h3>" % self.name
