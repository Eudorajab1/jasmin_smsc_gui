from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from .user_manager import list_users, list_groups
from .common import jasmin

def get_groups():
    return list_groups()

def get_gid(group):
    query = db.j_group.name == group
    rec = db(query).select().first()
    return rec

def get_users():
    users = list_users()
    for user in users:
        user_creds = {}
        query = (db.j_user.username == user['username'])
        cc=db(query).select().first()
        if not cc:
            if user['gid'][0] == '!':
                aa = user['gid'][1:]
                group = db.get_gid(aa)
            else:
                group = get_gid(user['gid'])
               
            print('user', user['uid'], 'Group', group.id, group.name)
            creds = jasmin.users(['get_creds', user['uid'] ])
            for cred in creds:
                if 'mt_messaging_cred' in cred:
                    splits = cred.split()
                    user_creds[splits[1] + '_'+splits[2]] = splits[3]
                elif 'smpps_cred' in cred:
                    splits = cred.split()
                    user_creds[splits[1] + '_'+splits[2]] = splits[3]
                else:    
                    splits = cred.split()
                    user_creds[splits[0]] = splits[1]
            u_id = db.j_user.insert(j_uid = user_creds['uid'], j_group=group, username = user_creds['username'])
            credentials = db.j_user_cred.insert(juser = user_creds['uid'],
                default_src_addr=user_creds['defaultvalue_src_addr'],
                quota_http_throughput=user_creds['quota_http_throughput'],
                quota_balance=user_creds['quota_balance'],
                quota_smpps_throughput=user_creds['quota_smpps_throughput'],
                quota_sms_count=user_creds['quota_sms_count'],
                quota_early_percent=user_creds['quota_early_percent'],
                value_priority=user_creds['valuefilter_priority'],
                value_content=user_creds['valuefilter_content'],
                value_src_addr=user_creds['valuefilter_src_addr'],
                value_dst_addr=user_creds['valuefilter_dst_addr'],
                value_validity_period=user_creds['valuefilter_validity_period'],
                author_http_send=user_creds['authorization_http_send'],
                author_http_dlr_method=user_creds['authorization_http_dlr_method'],
                author_http_balance=user_creds['authorization_http_balance'],
                author_smpps_send=user_creds['authorization_smpps_send'],
                author_priority=user_creds['authorization_priority'],
                author_http_long_content=user_creds['authorization_http_long_content'],
                author_src_addr=user_creds['authorization_src_addr'],
                author_dlr_level=user_creds['authorization_dlr_level'],
                author_http_rate=user_creds['authorization_http_rate'],
                author_validity_period=user_creds['authorization_validity_period'],
                author_http_bulk=user_creds['authorization_http_bulk']
            )
            print('User_creds', user_creds['uid'], u_id)
    return users

def get_filters():
    from .filter_manager import list_filters
    filters = list_filters()
    for filter in filters:
        ret = db.mt_filter.update_or_insert(db.mt_filter.fid == filter['filter_id'],
                                                fid = filter['filter_id'],    
                                                filter_type = filter['filter_type'],
                                                filter_route = filter['route'],
                                                f_value = filter['description'])
    rows = db(db.mt_filter.id > 0).select()
    return dict(rows=rows)
    
def get_smppcons():
    from .connector_manager import list_smpp_connectors
    connectors=list_smpp_connectors()
    for connector in connectors:
        c_det = {}
        con = jasmin.connector(['show', connector['cid']])
        for c in con:
            c_split = c.split()
            if len(c_split) > 1:
                if c_split[1] == 'Not':
                    c_det[c_split[0]] = 'Not defined'
                else:
                    c_det[c_split[0]] = c_split[1]
            else:
                c_det[c_split[0]] = ''
        ret = db.connector.update_or_insert(db.connector.name == c_det['cid'],
                name=c_det['cid'],
                c_logfile=c_det['logfile'],
                c_logrotate=c_det['logrotate'],
                c_loglevel=c_det['loglevel'],
                c_host=c_det['host'],
                c_port=c_det['port'],
                c_ssl=c_det['ssl'],
                c_username=c_det['username'],
                c_password=c_det['password'],
                c_bind=c_det['bind'],
                c_bind_to=c_det['bind_to'],
                c_trx_to=c_det['trx_to'],
                c_res_to=c_det['res_to'],
                c_pdu_red_to=c_det['pdu_red_to'],
                c_con_loss_retry=c_det['con_loss_retry'],
                c_con_loss_delay=c_det['con_loss_delay'],
                c_con_fail_retry=c_det['con_fail_retry'],
                c_con_fail_delay=c_det['con_fail_delay'],
                c_src_addr=c_det['src_addr'],
                c_src_ton=c_det['src_ton'],
                c_src_npi=c_det['src_npi'],
                c_dst_ton=c_det['dst_ton'],
                c_dst_npi=c_det['dst_npi'],
                c_bind_ton=c_det['bind_ton'],
                c_bind_npi=c_det['bind_npi'],
                c_validity=c_det['validity'],
                c_priority=c_det['priority'],
                c_requeue_delay=c_det['requeue_delay'],
                c_addr_range=c_det['addr_range'],
                c_systype=c_det['systype'],
                c_dlr_expiry=c_det['dlr_expiry'],
                c_submit_throughput=c_det['submit_throughput'],
                c_proto_id=c_det['proto_id'],
                c_coding=c_det['coding'],
                c_elink_interval=c_det['elink_interval'],
                c_def_msg_id=c_det['def_msg_id'],
                c_ripf=c_det['ripf'],
                c_dlr_msgid=c_det['dlr_msgid'])
        
    rows = db(db.connector.id > 0).select()
    return dict(rows=rows)
    
def get_httpcons():
    from .connector_manager import http_cons
    connectors=http_cons()
    for con in connectors:
        ret = db.http_cons.update_or_insert(db.http_cons.hcon_cid == con['cid'],
            hcon_cid = con['cid'],
            hcon_method = con['method'],
            hcon_url = con['baseurl'])
            
    rows = db(db.http_cons).select()
    return dict(rows=rows)

def get_fid(f_type, f_val=None):
    query = (db.mt_filter.filter_type == f_type)&(db.mt_filter.f_value == f_val)
    filter = db(query).select().first()
    return filter.id

def get_mtroutes():
    import re
    con_regex = '.*\((.*?)\).*'
    fil_regex = '.*\<(.*?)\>.*'
    from .route_manager import mt_routes
    routes = mt_routes()
    for route in routes:
        c_split = route['r_connectors'].split()
        cids = []
        fids = []
        for con in c_split:
            matches = re.search(con_regex, con)
            connector = matches.group(1)
            if 'smpp' in con:
                c = db(db.connector.name == connector).select().first()
                cids.append(c.id)
            else:
                print('MT ROUTES RE HTTP CONNECTORS', con, connector )    
        f_split = route['r_filters'].split(', ')
        for f in f_split:
            f_type = ''
            f_val = ''
            if 'DA' in f:
                f_type = 'DestinationAddrFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1] 
            elif 'U' in f:
                f_type = 'UserFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            elif 'SA' in f:
                f_type = 'SourceAddrFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            elif 'SM' in f:
                f_type = 'ShortMessageFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]    
            elif 'DI' in f:
                f_type = 'DateIntervalFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line
            elif 'TI' in f:
                f_type = 'TimeIntervalFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line
            elif 'TG' in f:
                f_type = 'TagFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]

            elif 'G' in f:    
                f_type = 'GroupFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            
            elif '<T>' in f:
                f_type = 'TransparentFilter'
            else:    
                continue    
            fid = get_fid(f_type, f_val)
            fids.append(fid)
        # now after all this update the records
        ret = db.mtroute.update_or_insert(db.mtroute.mt_order == route['r_order'],
                    mt_order = route['r_order'],
                    mt_type = route['r_type'], 
                    mt_connectors = cids,
                    mt_filters = fids,
                    mt_rate = route['r_rate']
                    )
    
    return 'Inside get_imos'
    
def get_moroutes():
    import re
    con_regex = '.*\((.*?)\).*'
    from .route_manager import mo_routes
    routes = mo_routes()
    for route in routes:
        c_split = route['r_connectors'].split()
        cids = []
        fids = []
        cidh = []
        for con in c_split:
            matches = re.search(con_regex, con)
            connector = matches.group(1)
            if 'smpp' in con:
                c = db(db.connector.name == connector).select().first()
                cids.append(c.id)
            else:
                c = db(db.http_cons.hcon_cid == connector).select().first()
                cidh.append(c.id)
        f_split = route['r_filters'].split('>,')
        for f in f_split:
            f_type = ''
            f_val = ''
            if 'DA' in f:
                f_type = 'DestinationAddrFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1] 
            elif 'U' in f:
                f_type = 'UserFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            elif 'SA' in f:
                f_type = 'SourceAddrFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            elif 'SM' in f:
                f_type = 'ShortMessageFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]    
            elif 'DI' in f:
                f_type = 'DateIntervalFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line
            elif 'TI' in f:
                f_type = 'TimeIntervalFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line
            elif 'TG' in f:
                f_type = 'TagFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]

            elif 'G' in f:    
                f_type = 'GroupFilter'
                matches = re.search(con_regex, f)
                if matches:
                    line = matches.group(1)            
                    f_val= line.split('=')[1]
            
            elif '<T' in f:
                f_type = 'TransparentFilter'
            else:    
                if '(dst_addr=' in f:
                    f_type = 'DestinationAddrFilter'
                    matches = re.search(con_regex, f)
                    if matches:
                        line = matches.group(1)            
                        f_val= line.split('=')[1]
                else:
                    continue    
            fid = get_fid(f_type, f_val)
            fids.append(fid)
        # now after all this update the records
        ret = db.moroute.update_or_insert(db.moroute.mo_order == route['r_order'],
                    mo_order = route['r_order'],
                    mo_type = route['r_type'], 
                    mo_connectors = cids,
                    mo_http_cons = cidh,
                    mo_filters = fids)
    rows = db(db.moroute.id > 0).select()
    return dict(rows=rows)

def get_imos():
    return 'Inside get_imos'
    
def get_imts():
    return 'Isnside get_imts'

@action("populate_database", method=['GET', 'POST'])
@action.uses(db, session, auth, flash, "generic.html")
def popualate_database():
    groups = get_groups()
    users = get_users()
    filters= get_filters()
    smpp_cons = get_smppcons()
    http_cons = get_httpcons()
    mt_routes = get_mtroutes()
    mo_routes = get_moroutes()
    mo_interceptors = get_imos()
    mt_interceptors = get_imts()
    flash.set('Database populated with existing Jasmin data')
    redirect(URL('index'))


@action("super_admin", method=['GET', 'POST'])
@action.uses(db, session, auth, flash, "superadmin_index.html")
def super_admin():
    tot_imos = 0
    tot_imts = 0
    tot_users = 0
    tot_mtroutes = 0
    tot_moroutes = 0
    tot_imos = db(db.j_imo).count()
    tot_imts = db(db.j_imt).count()
    tot_users = db(db.j_user).count()
    tot_mtroutes = db(db.mtroute).count()
    tot_moroutes = db(db.moroute).count()
    return dict(tot_imos = tot_imos,
                tot_imts = tot_imts,
                tot_users = tot_users,
                tot_mtroutes = tot_mtroutes,
                tot_moroutes = tot_moroutes,
                )
@action('user_unbind<user>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def user_unbind(user):
    j_user = user
    ret = jasmin.users(['unbind', j_user] )
    return ret

@action('user_ban/<user>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def user_ban(user):
    j_user = user
    ret = jasmin.users(['ban', j_user] )
    return ret

@action('flush_moroutes', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def flush_moroutes():
    route= ''
    t = jasmin.morouter(['flush', route])
    if not t:
        db(db.moroute.id > 0).delete()
        flash.set("Flushed all MO routes. This is unrecoverable")
    else:
        flash.set('Unable to fulsh MO routes. Please check and try again')
    redirect(URL('super_admin'))
    
@action('flush_mtroutes', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def flush_mtroutes():
    route = ''
    t = jasmin.mtrouter(['flush',route])
    if not t:
        db(db.mtroute.id > 0).delete()
        flash.set("Flushed all MT routes. This is unrecoverable")
    else:
        flash.set("Unable to flush MT routes. Please try again later")
    redirect(URL('super_admin'))
    
@action('flush_imos', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def flush_imos():
    order = script = filters = ''
    resp= jasmin.interceptor(['mo','flush', order, script,filters])
    if not resp:
        db(db.j_imo.id > 0).delete()
        flash.set("Flushed all MO Interceptors. This is unrecoverable")
    else:
        flash.set("Unable to flush all MO Interceptors. Please check connection and try again")
    redirect(URL('super_admin'))
    
@action('flush_imts', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def flush_imts():
    order = script = filters = ''
    resp= jasmin.interceptor(['mt','flush', order, script,filters])
    if not resp:
        db(db.j_imt.id > 0).delete()
        flash.set("Flushed all MT interceptors. This is unrecoverable")
    else:
        flash.set("Unable to flush all MT interceptors. Please check connection and try again")
    redirect(URL('super_admin'))
    
@action('s_users', method=['GET', 'POST'])
@action('s_users/<user>/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash, 's_users.html')
def s_users(user=None, action=None):
    j_gid = ''
    if action == 'unbind':
        ret = user_unbind(user)
        if ret:
            flash.set(ret)
        else:
            flash.set('Successfully unbound user %s ' % user)
    elif action == 'ban':
        ret = user_ban(user)
        if ret:
            flash.set(ret)
        else:
            flash.set('Successfully unbound and banned user %s' % user)
    users=list_users()
    return dict(users=users)
