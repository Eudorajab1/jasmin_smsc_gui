from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, Field, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from .models import MT_FILTER_TYPES
from pydal.validators import *
from . common import jasmin
from .utils import cols_split


def index():
    return dict()

@action('stats', method=['GET', 'POST'])
@action.uses('stats.html')
def stats():
    return dict()

@action('users_stats', method=['GET', 'POST'])
@action('users_stats/<usr>', method=['GET', 'POST'])
@action.uses('users_stats.html')
def users_stats(usr):
    usr=usr
    tt = jasmin.stats(['user',usr])
    users = []
    for t in tt[2:-1]:
        user = []
        r = str.split(t)
        l = len(r)
        if l ==4:
            ite = r[0][1:]
            tpe = r[1]+r[2]
            val = r[3]
        else:
            ite = r[0][1:]
            tpe = r[1]+r[2]
            if r[0][1:4] == 'bou':
                val = r[3]+" "+r[4]+" "+r[5]+" "+r[6]+" "+r[7]+" "+r[8]
            else:
                val = r[3]+" "+r[4]
        user.append(ite)
        user.append(tpe)
        user.append(val)
        users.append(user)
    return dict(usr=usr,items=users)

@action('smppc_stats', method=['GET', 'POST'])
@action('smppc_stats/<con>', method=['GET', 'POST'])
@action.uses('smppc_stats.html')
def smppc_stats(con):
    con = con
    tt = jasmin.stats(['smppc', con])
    connectors = []
    for t in tt[2:-1]:
        connector = []
        r = str.split(t)
        l = len(r)
        if l ==2:
            fld = r[0][1:]
            val = r[1]
            connector.append(fld)
            connector.append(val)
            connectors.append(connector)
        elif l == 1: #weird shit here
            fld = r[0][1:]
            val = "What is this"
            
        else:
            fld = r[0][1:]
            val = r[1]+" "+r[2]
            connector.append(fld)
            connector.append(val)
            connectors.append(connector)

        
    return dict(con=con,items=connectors)

@action('httpapi_stats', method=['GET', 'POST'])
@action.uses('httpapi_stats.html')
def httpapi_stats():
    items = []
    tt=(jasmin.stats(['httpapi']))
    lines=tt
    if not lines:
        return items
        
    for t in tt[2:-1]:
        item = []
        r = str.split(t)
        l = len(r)
        if l ==2:
            fld = r[0][1:]
            val = r[1]
            item.append(fld)
            item.append(val)
            items.append(item)
        else:
            fld = r[0][1:]
            val = r[1]+" "+r[2]
            
            item.append(fld)
            item.append(val)
            items.append(item)
           
    return dict(items=items)

@action('smppsapi_stats', method=['GET', 'POST'])
@action.uses('smppsapi_stats.html')
def smppsapi_stats():
    items = []
    tt=(jasmin.stats(['smppsapi']))
    lines=tt
    if not lines:
        return items
        
    for t in tt[2:-1]:
        item = []
        r = str.split(t)
        l = len(r)
        if l ==2:
            fld = r[0][1:]
            val = r[1]
            item.append(fld)
            item.append(val)
            items.append(item)
        else:
            fld = r[0][1:]
            val = r[1]+" "+r[2]
            
            item.append(fld)
            item.append(val)
            items.append(item)
           
    return dict(items=items)

@action('smppcs_stats', method=['GET', 'POST'])
@action.uses('smppcs_stats.html')
def smppcs_stats():
    connectors = []
    rows=(jasmin.stats(['smppcs']))
    lines=rows
    if not lines:
        return connectors
    tt = cols_split(lines[2:-2])
    for row in tt:
        connector={}
        n = len(row)
        if n == 11:
            connector.update(
                             cid=row[0][1:],
                             ca=row[1]+ " "+row[2],
                             ba=row[3]+ " "+row[4],
                             da= row[5]+" "+row[6],
                             sm=row[7],
                             dl=row[8],
                             qos=row[9],
                             other=row[10]
                            )
        elif n == 10:
            connector.update(
                             cid=row[0][1:],
                             ca=row[1]+ " "+row[2],
                             ba=row[3],
                             da= row[4]+" "+row[5],
                             sm=row[6],
                             dl=row[7],
                             qos=row[8],
                             other=row[9]
                            )
        elif n == 8:
            connector.update(
                             cid=row[0][1:],
                             ca=row[1],
                             ba=row[2],
                             da= row[3],
                             sm=row[4],
                             dl=row[5],
                             qos=row[6],
                             other=row[7]
                            )
        connectors.append(connector)
    return dict(cons = connectors)
    
@action('user_stats', method=['GET', 'POST'])
@action.uses('user_stats.html')
def user_stats():
    users = []
    rows=(jasmin.stats(['users']))
    lines=rows
    if not lines:
        return users
    tt = cols_split(lines[2:-2])
    for row in tt:
        n = len(row)
        user={}
        if n == 6:
            if row[1] == '0': #must be http binds
                user.update(
                    uid=row[0][1:],
                    smpp_bc=row[1],
                    smpp_la=row[2],
                    http_rc=row[3],
                    http_la=row[4]+" "+row[5],
                )
            else:
                user.update(
                    uid=row[0][1:],
                    smpp_bc=row[1],
                    smpp_la=row[2]+" "+row[3],
                    http_rc=row[4],
                    http_la=row[5]
                )
        elif n == 7: # both http and smpp activity
            user.update(
                    uid=row[0][1:],
                    smpp_bc=row[1],
                    smpp_la=row[2] + " "+row[3],
                    http_rc=row[4],
                    http_la=row[5] + " "+row[6]
                    )
        else:
            user.update(
                    uid=row[0][1:],
                    smpp_bc=row[1],
                    smpp_la=row[2],
                    http_rc=row[3],
                    http_la=row[4]
                    )
        users.append(user)
    return dict(users=users)
