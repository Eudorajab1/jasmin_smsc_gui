from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, Field, session, jasmin, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *
from . common import jasmin
from .utils import cols_split

@action('start_smpp_connector/<cid>')
@action.uses(db, flash, session)
def start_smpp_connector(cid):
    if not cid:
        flash.set('You need to select a connector to start')
        redirect(URL('manage_smpp_connectors'))
    con = cid
    t = jasmin.connector(['start',con])
    flash.set ("Started Connector %s" % con)
    redirect(URL('manage_smpp_connectors'))

@action('stop_smpp_connector/<cid>')
@action.uses(db, flash, session)
def stop_smpp_connector(cid):
    if not cid:
        flash.set('You need to select a connector to stop')
        redirect(URL('manage_smpp_connectors'))
    con = cid
    t = jasmin.connector(['stop',con])
    flash.set('Stopped connector %s' % cid)
    redirect(URL('manage_smpp_connectors'))

@action('edit_smpp_connector/<cid>', method=['GET', 'POST'])
@action.uses(db, flash, session, 'record_content.html')
def edit_smpp_connector(cid):
    if not cid:
        flash.set('No connector selected you need to select a connector')
        redirect(URL('manage_smpp_connecors'))
    con = cid
    back= ''
    title="Edit SMPP connector %s" % con
    query = db.connector.name == con
    cc = db(query).select().first()
    db.connector.id.readable=db.connector.id.writable=False
    db.connector.name.readable=db.connector.name.writable=False
    db.connector.name.default = con
    db.connector.c_logfile.default = '/var/log/jasmin/default-%s.log' % con
    back=''
    if cc: # we already have a record 
        print('Inside have one')
        form = Form(db.connector, cc, deletable=False, formstyle=FormStyleBulma)
    else:
        print('inside new one')
        form = Form(db.connector, deletable=False, formstyle=FormStyleBulma)
    if form.accepted:
        ret = jasmin.connector(['update',con,\
                               form.vars['c_ripf'],form.vars['c_con_fail_delay'],form.vars['c_dlr_expiry'],\
                               form.vars['c_coding'],form.vars['c_logrotate'],form.vars['c_submit_throughput'],\
                               form.vars['c_elink_interval'],form.vars['c_bind_to'],form.vars['c_port'],form.vars['c_con_fail_retry'],\
                               form.vars['c_password'],form.vars['c_src_addr'],form.vars['c_bind_npi'],form.vars['c_addr_range'],\
                               form.vars['c_dst_ton'],form.vars['c_res_to'],form.vars['c_def_msg_id'],form.vars['c_priority'],\
                               form.vars['c_con_loss_retry'],form.vars['c_username'],form.vars['c_dst_npi'],form.vars['c_validity'],\
                               form.vars['c_requeue_delay'],form.vars['c_host'],form.vars['c_src_npi'],form.vars['c_trx_to'],form.vars['c_logfile'],\
                               form.vars['c_ssl'],form.vars['c_loglevel'],form.vars['c_bind'],form.vars['c_proto_id'],form.vars['c_dlr_msgid'],\
                               form.vars['c_con_loss_delay'],form.vars['c_bind_ton'],form.vars['c_pdu_red_to'],form.vars['c_src_ton'],])
        if not ret:
            flash.set("Successfully updated connector %s" % con)
            redirect(URL('manage_smpp_connectors'))
        else:
            flash.set(ret)
    elif form.errors:
        flash.set('Form has errors')
    else:
        flash.set('Please refer to the Jasmin User Guide when updating values')
    return dict(content=form, back=back, title=title, caller='../manage_smpp_connectors')

@action('show_smpp_connector/<cid>', method = ['GET','POST'])
@action.uses(db, flash, session, 'show_record.html')
def show_smpp_connector(cid):
    flash.set('Inside show smpp connector %s' % cid)
    import re
    if not cid:
        flash.set('Please select a connector to show')
    con = cid
    tt = jasmin.connector(['show',con])
    connectors = []
    for t in tt[1:-1]:
        connector = []
        r = str.split(t)
        l = len(r)
        if l ==2:
            fld = r[0]
            val = r[1]
            connector.append(fld)
            connector.append(val)
            connectors.append(connector)
        else:
            pass
    return dict(caller = "../manage_smpp_connectors", rows=connectors)
    
@action('remove_smpp_connector/<cid>')
@action.uses(db, flash, session)
def remove_smpp_connector(cid):
    flash.set('Inside remove smpp connector %s' % cid)
    con = cid
    t = jasmin.connector(['remove', con])
    if not t:
        flash.set("Removed Connector %s" % con)
        query = db.connector.name == con
        db(query).delete()
    else:
        flash.set('ERROR: %s', t)
    redirect(URL('manage_smpp_connectors'))

def list_smpp_connectors():
    connectors = []
    rows=(jasmin.list_it('smppcs'))
    lines=rows
    if not lines:
        return connectors
    tt = cols_split(lines[2:-2])
    n = len(rows[0])
    connector={}
    for row in tt:
        connector={}
        connector.update(
                cid=row[0][1:],
                status=row[1],
                session=row[2],
                starts=row[3],
                stops=row[4]
                )
        connectors.append(connector)
    return connectors

@action('manage_smpp_connectors', method=['GET', 'POST'])
@action.uses(db, flash, session, 'smpp_connector_list.html')
def manage_smpp_connectors():
    headers = ['CID', 'Status', 'Host', 'Port', 'Username', 'Pasword', 'Session', 'Starts', 'Stops', 'Options']
    for f in db['connector']:
        f.readable= f.writable = False
    db.connector.name.readable = db.connector.name.writable = True
    db.connector.c_host.readable = db.connector.c_host.writable = True
    db.connector.c_port.readable = db.connector.c_port.writable = True
    db.connector.c_username.readable = db.connector.c_username.writable = True
    db.connector.c_password.readable = db.connector.c_password.writable = True
    db.connector.c_submit_throughput.readable = db.connector.c_submit_throughput.writable = True
    
    form=Form(db.connector, dbio=False, formstyle=FormStyleBulma)
    if form.accepted:
        name = form.vars['name']
        res = jasmin.connector(['create', name, form.vars['c_username'], form.vars['c_password'],\
                                 form.vars['c_host'], form.vars['c_port'], form.vars['c_submit_throughput']])
        if not res:
            form.vars['c_logfile'] = '/var/log/jasmin/default-%s.log' % name
            id = db.connector.insert(**db.connector._filter_fields(form.vars))
            #id = db.connector.insert(**dict(form.vars))
            if id:
                flash.set('Added new connector %s' % name)
            else:
                flash.set ('DB ERROR adding connector %s' % name)
        else:
            flash.set('ERROR: %s' % res)
        #redirect(URL('j_connectors', 'list_connectors'))
    elif form.errors:
        flash.set('ERRORS: %s' % form.errors)
    cons=list_smpp_connectors()
    return dict(form=form, cons=cons, db=db)

@action('delete_http_con/<cid>', method=['GET', 'POST'])
@action.uses(db,auth,session,flash)
def delete_http_con(cid):
    if not cid:
        flash.set('Please select a connector to delete')
        redirect(URL('manage_http_connectors'))
    con = cid
    t = jasmin.http_cons(['remove',con])
    flash.set('Removed Connector %s' % con)
    db(db.http_cons.hcon_cid == con).delete()
    redirect(URL('manage_http_connectors'))
    
def http_cons():
    connectors = []
    rows=(jasmin.list_it('httpcs'))
    lines=rows
    if not rows:
        return connectors
    tt = cols_split(lines[2:-2])
    n = len(rows[0])
    connector={}
    for row in tt:
        connector={}
        connector = dict(cid=row[0][1:], c_type=row[1],method=row[2], baseurl=row[3])
        connectors.append(connector)
    return connectors

@action('manage_http_connectors', method=['GET','POST'])
@action.uses(db, session, auth, flash, 'http_connector_list.html')
def manage_http_connectors():
    form=Form([
        Field('hcon_cid','string',length=10,label='Connector ID', comment= 'Must be unique'),
        Field('hcon_method', label='Method', comment='GET/POST',requires = IS_IN_SET(('GET', 'POST'))),
        Field('hcon_url',label='Base URL', comment='URL for MO messages e.g http://10.10.20.125/receive-sms/mo.php'), 
              ], dbio=False, formstyle=FormStyleBulma, deletable=False)
    if form.accepted:
        name = form.vars['hcon_cid']
        resp = jasmin.http_cons(['create', form.vars['hcon_cid'],form.vars['hcon_method'], form.vars['hcon_url']])
        if resp: # we have an error
            flash.set(resp)
        else:     
            id = db.http_cons.update_or_insert(db.http_cons.hcon_cid == form.vars['hcon_cid'],
                                                hcon_cid = form.vars['hcon_cid'],
                                                hcon_method = form.vars['hcon_method'],
                                                hcon_url = form.vars['hcon_url'])
            if id:
                flash.set('Added HTTP connector %s' % form.vars['hcon_cid'])
            else:
                flash.set('Updated HTTP connector %s ' % form.vars['hcon_cid'])    
        redirect(URL('manage_http_connectors'))
    cons= http_cons()
    return dict(form=form, cons=cons)

