
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, Field, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *
from .utils import cols_split

from . common import jasmin

@action('user_manager_index')
@action.uses(db, session, 'generic.html')
def index():
    return dict(msg="Hello form User Manager Index")

def list_groups():
    groups = []
    rows=(jasmin.list_it('groups'))
    if not rows:
        return groups
    tt = cols_split(rows[2:-2])
    group=dict(gid='')
    for t in tt:
        group=dict(gid = '')

        group.update(
               gid=t[0][1:],
                )
        groups.append(group)
        query = (db.j_group.name == group['gid'])
        cc = db(query).select().first()
        if not cc:
            if not group['gid'][0] == '!': # this is the result of disabling or enabling a group
                db.j_group.insert(name=group['gid'])

    return groups

def remove_group(group):
    gr = group
    t = jasmin.users(['remove_group',gr])
    flash.set("Removed Group %s" % gr)
    query = db.j_group.name == gr
    db(query).delete()
    redirect(URL('manage_groups'))
    

def disable_group(group):
    if not group:
        return ('You need to select a group')
    if group[0] == '!':
        return('Group %s is already disabled' % group)
    else:
        t = jasmin.users(['disable_group',group])
        return t

def enable_group(group):
    if not group:
        return ('You need to select a group')
    if group[0] != '!':
        return('Group %s is already enabled' % group)
    else:
        t=jasmin.users(['enable_group',group[1:]])
        return t

@action('manage_groups', method=['GET', 'POST'])
@action('manage_groups/<group>/<action>')
@action.uses(db, session, auth, flash, 'groups_list.html')
def manage_groups(group=None, action=None):
    groups=[]
    if action == 'enable':
        ret = enable_group(group)
        if ret:
            flash.set(ret)
        else:
            flash.set('Successfully enabled group %s' % group)
    elif action == 'disable':
        ret = disable_group(group)
        if ret:
            flash.set(ret)
        else:
            flash.set('Successfully disabled group %s' % group)
    elif action == 'remove':
        ret=remove_group(group)
        if ret:
            flash.set(ret)
        else:
            flash.set('Removed group %s' % group)

    form=Form(db.j_group, dbio=False, formstyle=FormStyleBulma)
    if form.accepted:
        group=jasmin.users(['create_group', form.vars['name']])
        if group:
            db.j_group.insert(**form.vars)
    groups=list_groups()
    return dict(form=form, groups=groups)

def disable_user(user):
    if not user:
        return ('You need to select a user')
    if user[0] == '!':
        return('User %s is already disabled' % user)
    else:
        t = jasmin.users(['disable_user',user])
        return t

def enable_user(user):
    if not user:
        return ('You need to select a user')
    if user[0] != '!':
        return('User %s is already enabled' % user)
    else:
        t=jasmin.users(['enable_user',user[1:]])
        return t
    

def remove_user(user):
    t = jasmin.users(['remove_user', user] )
    flash.set('User %s removed' % user)
    query = db.j_user.j_uid == user
    db(query).delete()
    query = db.j_user_cred.juser == user
    db(query).delete()
    redirect(URL('manage_users'))
    
@action('user_credentials/<user>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 'record_content.html')
def user_cred(user=None):
    usr = user
    title= 'Credentials for user %s ' % user
    query = db.j_user_cred.juser == usr
    juser = db(query).select().first()
    if juser:
        db.j_user_cred.juser.readable = db.j_user_cred.juser.writable = False
        db.j_user_cred.juser.default = usr
        db.j_user_cred.id.readable = db.j_user_cred.id.writable = False
        
        form = Form(db.j_user_cred, juser.id, deletable=False, formstyle=FormStyleBulma)
        flash.set('Please refer to the Jamsin user manual when updating values')
        if form.accepted:
        # need to update Jasmin with new creds
            juser=usr
            default_src_addr=form.vars.default_src_addr
            quota_http_throughput=form.vars.quota_http_throughput
            quota_balance=form.vars.quota_balance
            quota_smpps_throughput=form.vars.quota_smpps_throughput
            quota_sms_count=form.vars.quota_sms_count
            quota_early_percent=form.vars.quota_early_percent
            value_priority=form.vars.value_priority
            value_content=form.vars.value_content
            value_src_addr=form.vars.value_src_addr
            value_dst_addr=form.vars.value_dst_addr
            value_validity_period=form.vars.value_validity_period
            author_http_send=form.vars.author_http_send
            author_http_dlr_method=form.vars.author_http_dlr_method
            author_http_balance=form.vars.author_http_balance
            author_smpps_send=form.vars.author_smpps_send
            author_priority=form.vars.author_priority
            author_http_long_content=form.vars.author_http_long_content
            author_src_addr=form.vars.author_src_addr
            author_dlr_level=form.vars.author_dlr_level
            author_http_rate=form.vars.author_http_rate
            author_validity_period=form.vars.author_validity_period
            author_http_bulk=form.vars.author_http_bulk
            users=jasmin.users(['update', juser, \
                                default_src_addr,quota_http_throughput,quota_balance,quota_smpps_throughput,\
                                quota_sms_count,quota_early_percent,value_priority,value_content,value_src_addr,\
                                value_dst_addr,value_validity_period,author_http_send,author_http_dlr_method,\
                                author_http_balance,author_smpps_send,author_priority,author_http_long_content,author_src_addr,\
                                author_dlr_level,author_http_rate,author_validity_period,author_http_bulk])
            if not users:
                flash.set('User credentials updated')
            else:
                flash.set('Unable to update credentials')    
            redirect(URL('manage_users'))
    else:
        flash.set("User '%s' could not be found" % (usr))
        return dict(usr=usr, content='', caller='../manage_users')
    return dict(content=form, title=title, caller='../manage_users')

    
    return dict(usr=usr, form=form)



@action('manage_users', method=['GET', 'POST'])
@action('manage_users/<user>/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 'users_list.html')
def manage_users(user=None, action=None):
    j_gid = ''
    if action == 'enable':
        ret = enable_user(user)
        if ret:
            flash.set(ret)
        else:
            flash.set('Successfully enabled user %s' % user)
    elif action == 'disable':
        ret = disable_user(user)
        if ret:
            flash.set(ret)
        else:
            flash.set('Successfully disabled user %s' % user)
    elif action == 'remove':
        ret=remove_user(user)
        if ret:
            flash.set(ret)
        else:
            flash.set('Removed user %s ' % user)
    form = Form(db.j_user,dbio=False, formstyle=FormStyleBulma)
    '''[
        Field('username', 'string', length=10, comment="Jasmin User Name for HTTP and SMPP connecting. Must not include any spaces and can not be longer than 10 characters"),
        Field('password', 'string', length=10, comment='Jasmin Password for HTTP and SMPP connecting. Must not include any spaces and can not be longer than 10 characters'),
        Field('j_uid','string',label='Jasmin UID',length=12, comment='Jasmin UID cannot be longer than 12 characters and reccoment all in UPPER case. No spaces allowed. Suggest USER_1 etc.'),
        Field('j_group','reference j_group',label = 'Jasim GID', comment='Select a Group', requires=IS_IN_DB(db,'j_group.id','j_group.name'))],
    ]'''    
    if form.accepted:
        j_gid=db.j_group[form.vars['j_group']].name
        ret=jasmin.users(['create_user',form.vars['j_uid'],form.vars['username'], form.vars['password'], j_gid])
        if not ret:
            flash.set('Added user %s' % form.vars['username'])
            ret = db.j_user.update_or_insert(db.j_user.j_uid == form.vars['j_uid'],
                                                username = form.vars['username'],    
                                                password = form.vars['password'],
                                                j_uid = form.vars['j_uid'],
                                                j_group = form.vars['j_group'])
            if ret: #means we have inserted new one 
                cred = db.j_user_cred.insert(juser = form.vars['j_uid'])
        else:
            flash.set(ret)
    users=list_users()
    return dict(form=form, users=users)

def list_users():
    users = []
    rows=(jasmin.list_it('users'))
    if not rows:
        return users
    tt = cols_split(rows[2:-2])
    user={}
    w1=''
    w2=''
    for t in tt:
        user={}
        if len(t) == 6:
            l = len(t[5])
            i=0
            while i < l:
                if t[5][i] == '/':
                    w1=t[5][0:i]
                    i = i + 1
                else:
                    i = i + 1
            j=len(w1)
            j = j+1
            w2=t[5][j:]
            user.update(
                uid=t[0][1:],
                gid=t[1],
                username=t[2],
                balanceh=t[3],
                balances=t[4],
                mt_http=w1,
                mt_smpp=w2,
                )
        else:
            l = len(t[7])
            i=0
            while i < l:
                if t[7][i] == '/':
                    w1=t[7][0:i]
                    i = i + 1
                else:
                    i = i + 1
            j=len(w1)
            j = j+1
            w2=t[7][j:]
            user.update(
                uid=t[0][1:],
                gid=t[1],
                username=t[2],
                balanceh=t[3]+" "+t[4],
                balances=t[5]+" "+t[6],
                mt_http=w1,
                mt_smpp=w2,
                
                )
        users.append(user)
        query = (db.j_user.username == user['username'])
        cc=db(query).select().first()
        #if not cc:
        #    if user['gid'][0] == '!':
        #        aa = user['gid'][1:]
        #        group = get_gid(user['gid'][1:])
        #    else:
        #        group = get_gid(user['gid'])
        #    u_id = db.j_user.insert(gw = session.g_id, j_uid = user['uid'], j_group=group, username = user['username'])
        #    cred = db.j_user_cred.insert(gw = session.g_id, juser = user['uid'], quota_http_throughput = user['mt_http'], quota_balance=user['balanceh'],quota_smpps_throughput=user['mt_smpp'], quota_sms_count = user['balances'])
    return users

