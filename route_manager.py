from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, Field, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *
from .models import MTROUTE_TYPES, MOROUTE_TYPES
from . common import jasmin
from .utils import cols_split

def index():
    response.flash='Welcome to the rotuing manager'
    return dict()

@action('show_mt_route/<order>', method = ['GET','POST'])
@action.uses(db, flash, session, 'record_content.html')
def show_mt_route(order):
    if not order:
        flash.set('Please select a route to show')
        redirect(URL('manage_mt_routes'))
    title = 'Show MT route for order %s' % order
    qry = db(db.mtroute.mt_order == order).select().first()
    if qry:
        form = Form(db.mtroute, qry.id, dbio=False, formstyle=FormStyleBulma)
    return dict(caller = "../manage_mt_routes", title= title, content=form)

@action('remove_mt_route/<order>', method = ['GET','POST'])
@action.uses(db, flash, session, 'record_content.html')
def remove_mtroute(order):
    route = order
    res = jasmin.mtrouter(['remove',route])
    flash.set('Removed Route %s' % route)
    db(db.mtroute.mt_order == route).delete()
    redirect(URL('manage_mt_routes'))
    
@action('mt_static/<route_type>', method=['GET', 'POST'])
@action.uses(db, session, flash, 'record_content.html')
def mt_static(route_type=None):
    if not route_type:
        flash.set('You need to select a route type')
        redirect(URL('manage_mt_routes'))
    title= 'New Static MT Route'
    form = Form([
        Field('connector','reference connector',requires=IS_IN_DB(db,'connector.id','connector.name'),
                comment='SMPP or HTTP connector needs to be available'),
        Field('mt_order', 'string', length=10, label='Route order',comment='Routes will be assesd in descending order based on filters and matches'),
        Field('mt_filters', 'list:reference mt_filter', requires=IS_IN_DB(db, db.mt_filter._id, db.mt_filter.fid, multiple=True),label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
        Field('mt_rate','string',length = 10, label='Rate', comment='Decimal rate value for the connector. All messages going over this connector will be charged at the rate specified'),
        ],
        dbio=False,
        formstyle=FormStyleBulma)
    if form.accepted:
        f = form.vars['connector']
        form.vars['mt_connectors'] = [f]
        form.vars['mt_type'] = route_type
        print('Connector ', form.vars['mt_connectors'])
        con = db.connector[f].name
        cons = 'smppc('+con+')'
        order = form.vars['mt_order']
        ff=''
        for f in form.vars['mt_filters']:
            ff += db.mt_filter[f].fid
            ff+=';'
        filters = ff
        rate = form.vars['mt_rate']
        have_one = db(db.mtroute.mt_order == form.vars['mt_order']).select().first()
        if not have_one:    
            resp = jasmin.mtrouter(['StaticMTRoute',order, cons, filters,rate])
            if not resp:
                db.mtroute.insert(**db.mtroute._filter_fields(form.vars))
                flash.set('Added new Static MT route with order %s' % order)
                redirect(URL('manage_mt_routes'))
            else:
                flash.set('Problem adding route to Jamin. %s' % resp)
                redirect(URL('manage_mt_routes'))
        else:
            flash.set('Already have a MT connecor for order %s' % order)
            redirect(URL('manage_mt_routes'))
    return dict(content=form, title=title, caller='../manage_mt_routes')

@action('mt_default/<route_type>', method=['GET', 'POST'])
@action.uses(db, session, flash, 'record_content.html')
def mt_default(route_type=None):
    if not route_type:
        flash.set('You need to select a route type')
        redirect(URL('manage_mt_routes'))
    t = route_type
    title= 'New Default Route'
    form = Form([
                Field('mt_connectors', 'reference connector', requires=IS_IN_DB(db,'connector.id','connector.name'), label='SMPP Connector', comment='SMPP connector needs to be available'),
                Field('mt_rate','string',length = 10, label='Rate', comment='Decimal rate value for the connector. All messages going over this connector will be charged at the rate specified'),
                ],
                dbio=False, 
                formstyle=FormStyleBulma)
    if form.accepted:
        con = db.connector[form.vars['mt_connectors']].name
        cons = 'smppc('+con+')'
        order = '0'
        rate=form.vars['mt_rate']
        connectors = [form.vars['mt_connectors']]
        print('Connectors', connectors)
        resp= jasmin.mtrouter(['DefaultRoute', cons, rate])
        print('resp', resp)
        if not resp:
            id = db.mtroute.update_or_insert(db.mtroute.mt_order == 0,
                                            mt_order = 0,
                                            mt_type = t,
                                            mt_connectors = connectors,
                                            mt_rate = form.vars['mt_rate'])
            
            if id:
                flash.set('Added new %s with order %s' % (t, '0'))
            else:
                flash.set('Updated %s with order %s' % (t, '0'))
        else:
            flash.set('Problems adding route %s' % resp)
        redirect(URL('manage_mt_routes'))
    return dict(content=form, title=title, caller='../manage_mt_routes')

@action('mt_random/<route_type>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 'record_content.html')
def mt_random(route_type):
    if not route_type:
        flash.set('You need to select a route type')
        redirect(URL('manage_mt_routes'))
    else:
        t = route_type
        title= 'New Round Robin Route'
        form = Form([
        Field('mt_order', 'string', requires=IS_NOT_EMPTY(), length=10, label='Route order',comment='Routes will be assesd in descending order based on filters and matches'),
        Field('mt_connectors','list:reference connector',requires=IS_IN_DB(db,'connector.id','connector.name', multiple=True),
                comment='SMPP or HTTP connector needs to be available. Minimum 2 connectors required'),
        Field('mt_filters', 'list:reference mt_filter', requires=IS_IN_DB(db, db.mt_filter._id, db.mt_filter.fid, multiple=True),label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
        Field('mt_rate','string',length = 10, label='Rate', comment='Decimal rate value for the connector. All messages going over this connector will be charged at the rate specified'),
        ],dbio=False, formstyle=FormStyleBulma)
        if form.accepted:
            if len(form.vars['mt_connectors']) > 1:
                order = form.vars['order']
                ff=''
                for f in form.vars['mt_filters']:
                        ff += db.mt_filter[f].fid
                        ff+=';'
                filters = ff
                cc=''
                for f in form.vars['mt_connectors']:
                    cc += 'smppc('+ db.connector[f].name+');'
                cons = cc
                order = form.vars['mt_order']
                rate = form.vars['mt_rate']
                form.vars['mt_type'] = t
                have_one = db(db.mtroute.mt_order == form.vars['mt_order']).select().first()
                if not have_one:    
                    resp= jasmin.mtrouter(['RandomRoundrobinMTRoute',order,cons[:-1], filters[:-1],rate])
                    if not resp:
                        db.mtroute.insert(**db.mtroute._filter_fields(form.vars))
                        flash.set('Added new Round Robin MT route with order %s' % order)
                        redirect(URL('manage_mt_routes'))
                    else:
                        flash.set('Problem adding route to Jasmin. %s' % resp)
                        redirect(URL('manage_mt_routes'))
                else:
                    flash.set('Already have a MT connecor for order %s' % order)
                    redirect(URL('manage_mt_routes'))
            else:
                flash.set('You need to select at least 2 connectors for round robin route')
        elif form.errors:
            flash.set('Form has errors %s' % form.errors)
    return dict(content=form, title=title, caller='../manage_mt_routes')
    
@action('mt_failover/<route_type>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 'record_content.html')
def mt_failover(route_type):
    if not route_type:
        flash.set('You need to select a route type')
        redirec(URL('manage_mt_routes'))
    t = route_type
    title= 'New MT Failover Route'
    
    form = Form([Field('mt_order', 'string', length=10, label='Route order', requires=IS_NOT_EMPTY(), comment='Routes will be assesd in descending order based on filters and matches'),
                Field('mt_connectors','list:reference connector',requires=IS_IN_DB(db,'connector.id','connector.name', multiple=True),
                comment='SMPP or HTTP connector needs to be available. Minimum 2 connecrors required'),
                Field('mt_filters', 'list:reference mt_filter', requires=IS_IN_DB(db, db.mt_filter._id, db.mt_filter.fid, multiple=True),label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
                Field('mt_rate','string',length = 10, label='Rate', comment='Decimal rate value for the connector. All messages going over this connector will be charged at the rate specified'),
                ], dbio=False, formstyle=FormStyleBulma)
    if form.accepted:
        if len(form.vars['mt_connectors']) > 1:
            form.vars['mt_type'] = t
            order = form.vars['order']
            ff=''
            for f in form.vars['mt_filters']:
                    ff += db.mt_filter[f].fid
                    ff+=';'
            filters = ff
            cc=''
            for f in form.vars['mt_connectors']:
                cc += 'smppc('+db.connector[f].name+');'
            cons = cc
            order = form.vars['mt_order']
            rate = form.vars['mt_rate']
            have_one = db(db.mtroute.mt_order == form.vars['mt_order']).select().first()
            if not have_one:    
                resp= jasmin.mtrouter(['FailoverMTRoute',order, cons[:-1], filters[:-1],rate])
                if not resp:
                    db.mtroute.insert(**db.mtroute._filter_fields(form.vars))
                    flash.set('Added new MT Failover route with order %s' % order)
                    redirect(URL('manage_mt_routes'))
                else:    
                    flash.set('Problems adding route %s' % resp)
                redirect(URL('manage_mt_routes'))
            else:
                flash.set('Already have a MT connecor for order %s' % order)
                redirect(URL('manage_mt_routes'))
        else:
            flash.set('You need to select more than one connector for this type of route')
    elif form.errors:
        flash.set('ERRORS: %s' % form.errors)
    
    return dict(content=form, title=title, caller='../manage_mt_routes')
    
@action('manage_mt_routes', method=['GET', 'POST'])
@action.uses(db, session, flash, 'mt_routes_list.html')
def manage_mt_routes():
    form = Form([
        Field('r_tpe',label='Mt Route Type', requires=IS_IN_SET(MTROUTE_TYPES))
        ],
        formstyle=FormStyleBulma)
    
    if form.accepted:
        if form.vars['r_tpe'] =='DefaultRoute':
            redirect(URL('mt_default', 'DefaultRoute'))
            flash.set('Add a new Default Route')
        elif form.vars['r_tpe'] =='StaticMTRoute':
            redirect(URL('mt_static', 'StaticMtRoute'))
            flash.set=('Static MT Route')
        elif form.vars['r_tpe'] =='RandomRoundrobinMTRoute':
            redirect(URL('mt_random', 'RandomRoundrobinMTRoute'))
            flash.set('Random Round Robin Route')
        else:
            redirect(URL('mt_failover', 'FailoverMTRoute'))
            flash.set('FailoverMTRoute')
    routes=mt_routes()
    ##JAB need to check if route in the db here
    return dict(form=form, routes=routes)

def mt_routes():
    routes = []
    rows = jasmin.list_it('mtrouter')
    lines=rows
    if not rows:
        return routes
    tt = cols_split(lines[2:-2])
    n = len(rows[0])
    filters = ''
    connectors= ''
    for t in tt:
        route={}
        if len(t) == 4 or len(t) == 5: # default route
            if t[2] == '0':
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate=t[2]+t[3],
                    r_connectors=t[4],
                    r_filters='',
                    )
            else:
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate = t[2],
                    r_connectors = t[3],
                    r_filters='',
                    )
        elif len(t) >= 7 and t[1][0] == 'R': #Random route can have many connectors and filters
            if t[2] == '0':
                i = 4
            else:
                i = 3
            filters=""
            connectors = ""
            while i < len(t) and t[i][0] == 's':
                connectors += t[i]
                connectors += "   "
                i +=1
            while i < len(t):
                filters+= t[i]
                filters+="   "
                i +=1
            if t[2] == '0':
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate=t[2]+t[3],
                    r_connectors=connectors,
                    r_filters=filters,
                    )
            else:
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate = t[2],
                    r_connectors = connectors,
                    r_filters=filters,
                    )
            
        elif len(t) >= 7 and t[1][0] == 'F': #Failover route can have many connectors and filters
            if t[2] == '0':
                i = 4
            else:
                i = 3
            filters=''
            connectors = ''
            while i < len(t) and t[i][0] == 's':
                connectors += t[i]
                connectors += "   "
                i +=1
            while i < len(t):
                filters+= t[i]
                filters+= "   "
                i +=1
            if t[2] == '0':
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate=t[2]+t[3],
                    r_connectors=connectors,
                    r_filters=filters,
                    )
            else:
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate = t[2],
                    r_connectors = connectors,
                    r_filters=filters,
                    )

        elif len(t) >= 6 and t[1][0] == 'S': #Static route can have many filters
            if t[2] == '0':
                i = 5
            else:
                i = 4
            filters=''
            while i < len(t):
                filters += t[i]
                filters += "   "
                i +=1
            if t[2] == '0':
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate=t[2]+t[3],
                    r_connectors=t[4],
                    r_filters=filters,
                    )
            else:
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_rate = t[2],
                    r_connectors = t[3],
                    r_filters=filters,
                    )
        if route:
            routes.append(route)
        else:
            pass
        test=1
    return routes

def route_exists(order):
    query = db.moroute.mo_order == order
    ret = db(query).select().first()
    return ret

@action('mo_create/<route_type>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 'record_content.html')
def mo_create(route_type):
    resp=None
    cons = ''
    filters = ''
    if not route_type:
        flash.set('You need to select a route type to create')
        redirect(URL('manage_mo_routes'))
    if route_type == 'DefaultRoute':
        title= 'New Default MO Route'
        form = Form([Field('mo_connectors','reference connector',label = 'SMPP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'connector.id','connector.name')),comment='SMPP connector needs to be available'),
                    Field('mo_http_cons','reference http_cons',label = 'HTTP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'http_cons.id','http_cons.hcon_cid')),comment='SMPP connector needs to be available')
        ], dbio=False, formstyle=FormStyleBulma)
        if form.accepted:
            if route_exists(0):
                flash.set('Route with order 0 already exists')
                redirect(URL('manage_mo_routes'))
            if not form.vars['mo_connectors'] and not form.vars['mo_http_cons']:
                flash.set('please select either HTTP or SMPP connector')
                redirect(URL('mo_create', 'DefaultRoute'))
            if form.vars['mo_connectors'] and form.vars['mo_http_cons']:
                flash.set('please select either HTTP or SMPP connector not both')
                redirect(URL('mo_create', 'DefaultRoute'))
            if form.vars['mo_connectors']:
                con = db.connector[form.vars['mo_connectors']].name
                cons='smpps('+con+')'
            else:
                con = db.http_cons[form.vars['mo_http_cons']].hcon_cid
                cons='http('+con+')'
            form.vars['mo_type'] = route_type
            form.vars['mo_order'] = '0'
            resp= jasmin.morouter(['DefaultRoute', cons])
            if not resp:
                id = db.moroute.insert(**db.moroute._filter_fields(form.vars))
                if id:
                    flash.set('New Default MO route added with order %s' % form.vars['mo_order'])
                    redirect(URL('manage_mo_routes'))
                else:
                    flash.set('New Default MO route with order %s NOT ADDED TO DB' % form.vars['mo_order'])
            else:
                flash.set('ERROR: %s ' % resp)
        elif form.errors:
            flash.set('Form has erros: %s' % form.errors)    
    elif route_type == 'StaticMORoute':
        title= 'New Static MO Route'
        form = Form([Field('mo_order', 'string', length=10, label='Route order',comment='Routes will be assesd in descending order based on filters and matches'),
                    Field('mo_connectors','reference connector',label = 'SMPP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'connector.id','connector.name')),comment='SMPP connector needs to be available'),
                    Field('mo_http_cons','reference http_cons',label = 'HTTP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'http_cons.id','http_cons.hcon_cid')),comment='HTTP connector needs to be available'),
                    Field('mo_filters', 'list:reference mt_filter', requires=IS_IN_DB(db, db.mt_filter._id, db.mt_filter.fid, multiple=True), label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
        ], dbio=False, formstyle=FormStyleBulma)
        if form.accepted:
            if route_exists(form.vars['mo_order']):
                flash.set('MO Route with order %s already exists' % form.vars['mo_order'])
                redirect(URL('manage_mo_routes'))
            if not form.vars['mo_connectors'] and not form.vars['mo_http_cons']:
                flash.set('please select either HTTP or SMPP connector')
                redirect(URL('mo_create', 'StaticMORoute'))
            if form.vars['mo_connectors'] and form.vars['mo_http_cons']:
                flash.set('Please select either HTTP or SMPP connector not both')
                redirect(URL('mo_create', 'StaticMORoute'))
            if form.vars['mo_connectors']:
                con = db.connector[form.vars['mo_connectors']].name
                cons='smpps('+con+')'
            else:
                con = db.http_cons[form.vars['mo_http_cons']].hcon_cid
                cons='http('+con+')'
            ff=''
            for f in form.vars['mo_filters']:
                ff += db.mt_filter[f].fid
                ff+=';'
            filters = ff
            order = form.vars['mo_order']
            form.vars['mo_type'] = route_type
            
            resp= jasmin.morouter(['StaticMORoute', order, cons, filters[:-1]])
            if not resp:
                id = db.moroute.insert(**db.moroute._filter_fields(form.vars))
                if id:
                    flash.set('New Static MO route added with order %s' % form.vars['mo_order'])
                    redirect(URL('manage_mo_routes'))
                else:
                    flash.set('New Static MO route with order %s NOT ADDED TO DB' % form.vars['mo_order'])
            else:
                flash.set('ERROR: %s ' % resp)
        elif form.errors:
            flash.set('Form has erros: %s' % form.errors)
            redirect(URL('mo_create', 'StaticMORoute'))
        
    elif route_type == 'RandomRoundrobinMORoute':
        title= 'New Random Roundrobin MO Route'
        form = Form([Field('mo_order', 'string', length=10, label='Route order',comment='Routes will be assesd in descending order based on filters and matches'),
                    Field('mo_connectors','list:reference connector',label = 'SMPP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'connector.id','connector.name', multiple=True)),comment='SMPP connector needs to be available'),
                    Field('mo_http_cons','list:reference http_cons',label = 'HTTP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'http_cons.id','http_cons.hcon_cid',multiple=True)),comment='HTTP connector needs to be available'),
                    Field('mo_filters', 'list:reference mt_filter', requires=IS_IN_DB(db,'mt_filter.id','mt_filter.fid',multiple=True), label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
        ], dbio=False, formstyle=FormStyleBulma)
        if form.accepted:
            if route_exists(form.vars['mo_order']):
                flash.set('MO Route with order %s already exists' % form.vars['mo_order'])
                redirect(URL('manage_mo_routes'))
            if not form.vars['mo_connectors'] and not form.vars['mo_http_cons']:
                flash.set('please select either HTTP or SMPP connector')
                redirect(URL('mo_create', 'StaticMORoute'))
            if form.vars['mo_connectors'] and form.vars['mo_http_cons']:
                flash.set('Please select either HTTP or SMPP connector not both')
                redirect(URL('mo_create', 'RandomRoundrobinMORoute'))
            cc=''
            if form.vars['mo_connectors']:
                for f in form.vars['mo_connectors']:
                    cc += 'smpps('+db.connector[f].name+');'
            else:        
                for f in form.vars['mo_http_cons']:
                    cc += 'http('+db.http_cons[f].hcon_cid+');'
            cons = cc
            ff=''
            for f in form.vars['mo_filters']:
                ff += db.mt_filter[f].fid
                ff+=';'
            filters = ff
            form.vars['mo_type'] = route_type
            order = form.vars['mo_order']
            resp= jasmin.morouter(['RandomRoundrobinMORoute', order, cons[:-1], filters[:-1]])
            if not resp:
                id = db.moroute.insert(**db.moroute._filter_fields(form.vars))
                if id:
                    flash.set('New Random Roundrobin MO route added with order %s' % form.vars['mo_order'])
                    redirect(URL('manage_mo_routes'))
                else:
                    flash.set('New Random Roundrobin MO route with order %s NOT ADDED TO DB' % form.vars['mo_order'])
            else:
                flash.set('ERROR: %s ' % resp)
        elif form.errors:
            flash.set('Form has erros: %s' % form.errors)
            redirect(URL('mo_create', 'RandomRoundrobinMORoute'))
        
    elif route_type=='FailoverMORoute':
        title= 'New Failover MO Route'
        form = Form([Field('mo_order', 'string', length=10, label='Route order',comment='Routes will be assesd in descending order based on filters and matches'),
                    Field('mo_connectors','list:reference connector',label = 'SMPP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'connector.id','connector.name', multiple=True)),comment='SMPP connector needs to be available'),
                    Field('mo_http_cons','list:reference http_cons',label = 'HTTP connector',  requires=IS_EMPTY_OR(IS_IN_DB(db,'http_cons.id','http_cons.hcon_cid',multiple=True)),comment='HTTP connector needs to be available'),
                    Field('mo_filters', 'list:reference mt_filter', requires=IS_IN_DB(db,'mt_filter.id','mt_filter.fid',multiple=True), label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
        ], dbio=False, formstyle=FormStyleBulma)
        if form.accepted:
            if not form.vars['mo_connectors'] and not form.vars['mo_http_cons']:
                flash.set('please select either HTTP or SMPP connector')
                redirect(URL('mo_create', 'StaticMORoute'))
            if form.vars['mo_connectors'] and form.vars['mo_http_cons']:
                flash.set('Please select either HTTP or SMPP connector not both')
                redirect(URL('mo_create', 'FailoverMORoute'))
            cc=''
            cc=''
            if form.vars['mo_connectors']:
                for f in form.vars['mo_connectors']:
                    cc += 'smpps('+db.connector[f].name+');'
            else:        
                for f in form.vars['mo_http_cons']:
                    cc += 'http('+db.http_cons[f].hcon_cid+');'
            cons = cc
            ff=''
            for f in form.vars['mo_filters']:
                ff += db.mt_filter[f].fid
                ff+=';'
            filters = ff
            form.vars['mo_type'] = route_type
            order = form.vars['mo_order']
            resp= jasmin.morouter(['FailoverMORoute', order, cons[:-1], filters[:-1]])
            if not resp:
                id = db.moroute.insert(**db.moroute._filter_fields(form.vars))
                if id:
                    flash.set('New Failorver MO route added with order %s' % form.vars['mo_order'])
                    redirect(URL('manage_mo_routes'))
                else:
                    flash.set('New Failorver MO route with order %s NOT ADDED TO DB' % form.vars['mo_order'])    
            else:
                flash.set('ERROR: %s ' % resp)
        elif form.errors:
            flash.set('Form has erros: %s' % form.errors)
            redirect(URL('mo_create', 'FailoverMORoute'))        
    else:
        flash.set('No such type of MO route detected')
    return dict(content=form, title=title, caller='../manage_mo_routes')

@action('remove_moroute/<route_order>', method=['GET', 'POST'])
@action.uses(db,session,auth,flash)
def remove_moroute(route_order):
    route = route_order
    t = jasmin.morouter(['remove', route])
    flash.set("Removed MO Route with order %s" % route)
    query = db.moroute.mo_order == route
    db(query).delete()
    redirect(URL('manage_mo_routes'))
    
def mo_routes():
    routes = []
    rows = jasmin.list_it('morouter')
    if not rows:
        return routes #we dont have any mo routes
    else:    
        lines=rows
        tt = cols_split(lines[2:-2])
        n = len(rows[0])
        routes = []
        route={}
        filters = ''
        connectors= ''
        for t in tt:
            route={}
            if len(t) == 3: # default route
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_connectors=t[2],
                    r_filters=''
                    )
            elif len(t) > 3 and t[1][0] == 'R': #Random route can have many connectors and filters
                i = 2
                filters=''
                connectors = ''
                while i < len(t) and t[i][0] == 's':
                    connectors += t[i]
                    i +=1
                while i < len(t) and t[i][0] == 'h':
                    connectors += t[i]
                    i +=1
                while i < len(t):
                    filters+= t[i]
                    i +=1
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_connectors=connectors,
                    r_filters=filters,
                    )
            elif len(t) > 3 and t[1][0] == 'F': #Failover route can have many connectors and filters
                i = 2
                filters=''
                connectors = ''
                while i < len(t) and t[i][0] == 's':
                    connectors += t[i]
                    i +=1
                while i < len(t) and t[i][0] == 'h':
                    connectors += t[i]
                    i +=1
                while i < len(t):
                    filters+= t[i]
                    i +=1
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_connectors=connectors,
                    r_filters=filters,
                    )
            elif len(t) > 3 and t[1][0] == 'S': #Static route can have many filters
                i = 4

                filters=''
                while i < len(t):
                    filters += t[i]
                    i +=1
                route.update(
                    r_order=t[0][1:],
                    r_type=t[1],
                    r_connectors=t[2],
                    r_filters=filters,
                    )
            else:
                i = 1
            routes.append(route)
    return routes

@action('manage_mo_routes', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 'list_moroutes.html')
def manage_mo_routes():
    form = Form([
                Field('r_tpe',label='Mo Route Type', requires=IS_IN_SET(MOROUTE_TYPES))
                ], dbio=False, formstyle = FormStyleBulma)
    if form.accepted:
        redirect(URL('mo_create', form.vars['r_tpe']))
    routes=mo_routes()
    return dict(form=form, routes=routes)

