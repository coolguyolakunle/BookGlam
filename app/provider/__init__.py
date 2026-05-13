from flask import Blueprint

provider = Blueprint('provider', __name__)

from app.provider import routes  # noqa
