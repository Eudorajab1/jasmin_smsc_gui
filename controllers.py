"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash


@action("index", method=['GET', 'POST'])
@action.uses(db, session, auth, flash, "index.html")
def index():
    tot_imos = 0
    tot_imts = 0
    tot_grps = 0
    tot_users = 0
    tot_filters = 0
    tot_smppcons = 0
    tot_httpcons = 0
    tot_mtroutes = 0
    tot_moroutes = 0
    tot_gateways = 0
    tot_imos = db(db.j_imo).count()
    tot_imts = db(db.j_imt).count()
    tot_grps = db(db.j_group).count()
    tot_users = db(db.j_user).count()
    tot_filters = db(db.mt_filter).count()
    tot_smppcons = db(db.connector).count()
    tot_httpcons = db(db.http_cons).count()
    tot_mtroutes = db(db.mtroute).count()
    tot_moroutes = db(db.moroute).count()
    return dict(tot_imos = tot_imos,
                tot_imts = tot_imts,
                tot_grps = tot_grps,
                tot_users = tot_users,
                tot_filters = tot_filters,
                tot_smppcons = tot_smppcons,
                tot_httpcons = tot_httpcons,
                tot_mtroutes = tot_mtroutes,
                tot_moroutes = tot_moroutes,
                )

    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    return dict(message=message)
