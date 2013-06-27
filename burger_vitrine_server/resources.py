# -*- coding: utf8 -*-
"""
This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""

import os
import os.path as path
import re
import pkg_resources
import subprocess

import flask


class Resource(object):
    PATH = None
    SUFIX = None
    MIME = "text/plain"

    def __init__(self, name):
        self.name = self.handle_keywords(name)

    def path(self):
        filename = (self.name if self.SUFIX is None else
                    "%s.%s" % (self.name, self.SUFIX))
        return path.join(resources_path(), self.PATH, filename)

    def handle_keywords(self, name):
        """Allows git-like relative resource addresses

        Format: (latest|release|prerelease|snapshot)(\^|~\d+)?
        """
        try:
            for keyword, release_type in JARResource.RELEASE_TYPES.iteritems():
                if name == keyword:
                    return JARResource.latest(release_type=release_type)
                match = re.search("^%s\\^$" % keyword, name)
                if match is not None:
                    return JARResource.latest(i=1, release_type=release_type)
                match = re.search("^%s\\~(\\d+)$" % keyword, name)
                if match is not None:
                    return JARResource.latest(i=int(match.group(1)),
                                              release_type=release_type)
        except NotFoundException:
            raise NotFoundException(name)
        return name

    @classmethod
    def dir(cls):
        return path.join(resources_path(), cls.PATH)

    def exists(self):
        return path.exists(self.path())

    def generate(self):
        raise NotImplementedError()

    def _generate(self):
        if not path.exists(self.dir()):
            os.mkdir(self.dir())
        content = self.generate()
        with open(self.path(), "w") as f:
            f.write(content)

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
    def __init__(self, msg=None):
        if msg is None:
            msg = "An error occurred while generating the requested resource"
        super(GenerationException, self).__init__(msg)


class NotFoundException(Exception):
    def __init__(self, resource=None):
        if resource is None:
            msg = "The requested resource was not found."
        else:
            msg = "The resource '%s' was not found." % resource
        super(NotFoundException, self).__init__(msg)


class JARResource(Resource):
    PATH = "jar"
    SUFIX = "jar"

    RELEASE = 1
    PRE_RELEASE = 2
    SNAPSHOT = 3

    RELEASE_TYPES = {"latest": None,
                     "release": RELEASE,
                     "snapshot": SNAPSHOT,
                     "prerelease": PRE_RELEASE,
                     "HEAD": None}

    _list = None

    def generate(self):
        raise NotFoundException()

    @classmethod
    def latest(cls, i=0, release_type=None):
        if i >= len(cls.list()):
            return NotFoundException()
        return [jar for jar in cls.list()
                if jar[1] == release_type or release_type is None][-(i + 1)][0]

    @classmethod
    def list(cls):
        if cls._list is None:
            cls.refresh_list()
        return cls._list

    @classmethod
    def refresh_list(cls):
        cls._list = [
            (jar[:-4], cls.release_type(jar[:-4]))
            for jar
            in sorted(
                os.listdir(cls.dir()),
                key=lambda jar:path.getmtime(path.join(cls.dir(), jar))
            )
            if jar.endswith('.jar')
        ]

    @classmethod
    def release_type(cls, jar):
        if "pre" in jar or "rc" in jar:
            return cls.PRE_RELEASE
        elif "w" in jar:
            return cls.SNAPSHOT
        else:
            return cls.RELEASE


class DiffResource(Resource):
    def handle_keywords(self, name):
        return "...".join(super(DiffResource, self).handle_keywords(part)
                          for part in name.split("..."))


class JSONResource(DiffResource):
    PATH = "json"
    SUFIX = "json"
    MIME = "application/json"

    def generate(self):
        if "..." in self.name:
            parts = self.name.split("...")
            if len(parts) > 2:
                raise NotFoundException()
            return self.generate_hamburglar(*parts)
        else:
            return self.generate_burger()

    def generate_burger(self):
        jar = JARResource(self.name)
        if not jar.exists():
            raise NotFoundException()
        return execute_bundled_script(("Burger", "munch.py"), (jar.path(),))

    def generate_hamburglar(self, left, right):
        if left == right:
            raise NotFoundException()
        left, right = JSONResource(left), JSONResource(right)
        left.generate_if_needed()
        right.generate_if_needed()
        return execute_bundled_script(("Hamburglar", "hamburglar.py"),
                                      (left.path(), right.path()))


class HTMLResource(DiffResource):
    PATH = "html"
    SUFIX = "html"
    MIME = "text/html"

    def generate(self):
        json = JSONResource(self.name)
        json.generate_if_needed()
        return execute_bundled_script(("BurgerVitrine", "vitrine.py"),
                                      ("-b", "-r /static"),
                                      open(json.path(), "r"))

    def render(self):
        return flask.render_template("burger.html", title=self.name,
                                     body=super(HTMLResource, self).render())


class BlocksResource(Resource):
    PATH = "blocks"
    SUFIX = "png"
    MIME = "image/png"

    def generate(self):
        jar = JARResource(self.name)
        if not jar.exists():
            raise NotFoundException()
        json = JSONResource(self.name)
        json.generate_if_needed()
        return execute_bundled_script(("BurgerVitrine", "vitrine.py"),
                                      ("-t", jar.path()),
                                      open(json.path(), "r"))


class ItemsResource(Resource):
    PATH = "items"
    SUFIX = "png"
    MIME = "image/png"

    def generate(self):
        jar = JARResource(self.name)
        if not jar.exists():
            raise NotFoundException()
        json = JSONResource(self.name)
        json.generate_if_needed()
        return execute_bundled_script(("BurgerVitrine", "vitrine.py"),
                                      ("-i", jar.path()),
                                      open(json.path(), "r"))


def execute_bundled_script(script_path, args, stdin=None):
    script = pkg_resources.resource_filename(__name__,
                                             path.join("lib", *script_path))
    python = flask.current_app.config.get("PYTHON", "/usr/bin/python")
    try:
        return subprocess.check_output((python, script) + args,
                                       stdin=stdin)
    except subprocess.CalledProcessError as e:
        raise GenerationException(e.output.strip())


def resources_path():
    return flask.current_app.resources_path
