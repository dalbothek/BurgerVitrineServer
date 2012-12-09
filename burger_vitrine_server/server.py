# -*- coding: utf8 -*-
import flask

import burger_vitrine_server.resources as resources


RESOURCE_TYPES = dict((resource.PATH, resource) for resource in [
    resources.JSONResource,
    resources.HTMLResource
])

app = flask.Flask(__name__)
run = app.run


@app.route("/")
def home():
    return "Home"


@app.route("/about")
def home():
    return "About"


@app.route("/doc")
def home():
    return "Documentation"


@app.route("/<resource_type>/<resource>")
def resource_direct(resource_type, resource):
    if resource_type not in RESOURCE_TYPES:
        return flask.abort(400, "Invalid resource type")
    return display_resource(RESOURCE_TYPES[resource_type](resource))


@app.route("/<resource>")
def resource_guess(resource):
    if resource.endswith(".json"):
        return display_resource(resources.JSONResource(resource[:-5]))
    accept = flask.request.environ.get("HTTP_ACCEPT", "text/html")
    if "application/json" in accept:  # TODO: Actually parse the accept header
        return display_resource(resources.JSONResource(resource))
    return display_resource(resources.HTMLResource(resource))


def display_resource(resource):
    try:
        return resource.render()
    except resources.NotFoundException as e:
        return flask.abort(404, resource.render_error(e))
    except Exception as e:
        return flask.abort(500, resource.render_error(e))
