# check compatibility
import py4web

assert py4web.check_compatible("0.1.20190709.1")

# by importing db you expose it to the _dashboard/dbadmin
from .models import db

# by importing controllers you expose the actions defined in it
from . import controllers
from . import super_admin
from . import filter_manager
from . import connector_manager
from . import route_manager
from . import stats
from . import interceptor_manager
# optional parameters
__version__ = "1.0.0.0"
__author__ = "John Bannister <eudorajab1@gmail.com>"
__license__ = "MIT"
