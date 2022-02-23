from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, Field, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from .models import MT_FILTER_TYPES
from pydal.validators import *
from . common import jasmin
from .utils import cols_split

@action('db_filters', method=['GET', 'POST'])
@action.uses(db, auth, session, flash, 'generic.html')
def db_filters():
    rows = db(db.mt_filter.id >0).select()
    return dict(rows=rows)


@action('delete_filter/<fid>')
@action.uses(db,auth,session,flash)
def delete_filter(fid):
    if not fid:
        flash.set('You need to select a filter to delet')
        redirect(URL('manage_filters'))
    res = jasmin.filters(['delete',  fid])
    flash.set('Removed Filter %s' % fid)
    query = db.mt_filter.fid == fid
    db(query).delete()
    redirect(URL('manage_filters'))

def list_filters():
    filters = []
    rows=jasmin.list_it('filters')
    if rows:
        tt = cols_split(rows[2:-2])
        for t in tt:
            j_filter={}
            description = ''
            if t[1] =='UserFilter':
                description=t[4][5:-2]
            elif t[1] == 'GroupFilter':
                description=t[4][5:-2]
            elif t[1] == 'DestinationAddrFilter':
                description=t[5][10:-2]
            elif t[1] == 'SourceAddrFilter':
                description=t[5][10:-2]
            elif t[1] == 'ShortMessageFilter':
                description=t[5][5:-2]
            elif t[1] == 'DateIntervalFilter':
                description=t[5][1:-2]
            elif t[1] == 'TimeIntervalFilter':
                description=t[5][1:-2]
            elif t[1] == 'TagFilter':
                description=t[5][5:-2]
            elif t[1] == 'TransparentFilter':
                    description=''
            else:
                description = ''
            if len(t) == 5:
                j_filter.update(
                    filter_id=t[0][1:],
                    filter_type=t[1],
                    route=t[2],
                    description=description
                    )
            else:
                j_filter.update(
                    filter_id=t[0][1:],
                    filter_type=t[1],
                    route=t[2]+"/"+t[3],
                    description=description
                    )
        
            filters.append(j_filter)
    return filters

@action('manage_filters', method=['GET', 'POST'])
@action.uses(db, auth, session, flash, 'list_filters.html')
def manage_filters():
    db.mt_filter.filter_route.readable = db.mt_filter.filter_route.writable = False
    form=Form([Field('fid', 'string', length=15, label='FID', comment='Filter ID must be unique'),
                Field('filter_type', requires=IS_IN_SET(MT_FILTER_TYPES), comment='Select from list of available types'),
                Field('f_value', 'string', length = 50, label='Filter Value', comment='Values must correspond to filter type'),
               ], dbio=False, formstyle=FormStyleBulma, deletable=False)
    if form.accepted:
        response=jasmin.filters(['create', form.vars['fid'], form.vars['filter_type'], form.vars['f_value']])
        if not response:
            ret = db.mt_filter.update_or_insert(db.mt_filter.fid == form.vars['fid'],
                                                fid = form.vars['fid'],    
                                                filter_type = form.vars['filter_type'],
                                                f_value = form.vars['f_value'])
            
            flash.set("Added a new filter %s" % form.vars['fid'])
        else:
            flash.set('Problem adding filter %s' % response)
        redirect(URL('manage_filters'))
    if form.errors:
        flash.set('Form has errors')
    filters=list_filters()
    return dict(form=form, filters=filters)
