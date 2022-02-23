"""
This file defines the database models
"""

from .common import db, Field
from pydal.validators import *
from yatl.helpers import *
from py4web.utils.form import Form, FormStyleBulma

MTROUTE_TYPES = ('DefaultRoute', 'StaticMTRoute', 'RandomRoundrobinMTRoute','FailoverMTRoute')
MOROUTE_TYPES = ('DefaultRoute', 'StaticMORoute', 'RandomRoundrobinMORoute','FailoverMORoute')
HTTP_CON_TYPE =('GET', 'POST')
MT_CON_TYPES =('smppc', 'httpc')
MT_FILTER_TYPES=('DestinationAddrFilter','UserFilter','GroupFilter','SourceAddrFilter','ShortMessageFilter','DateIntervalFilter','TimeIntervalFilter','TagFilter','TransparentFilter')
MO_FILTER_TYPES=('DestinationAddrFilter','SourceAddrFilter','ConnectorFilter','ShortMessageFilter','DateIntervalFilter','TimeIntervalFilter','TagFilter','EvalPyFilter','TransparentFilter')
IMO_TYPES=('DefaultInterceptor', 'StaticMOInterceptor')
IMT_TYPES=('DefaultInterceptor', 'StaticMTInterceptor')

db.define_table('mt_filter',
                Field('fid', 'string', length=15, label='FID', comment='Filter ID must be unique'),
                Field('filter_type', requires=IS_IN_SET(MT_FILTER_TYPES), comment='Select from list of available types'),
                Field('filter_route'),
                Field('f_value', 'string', length = 50, label='Filter Value', comment='Values must correspond to filter type'),
               format='%(fid)s')


db.define_table('j_imo',
                Field('motype', label='Type',requires=IS_IN_SET(IMO_TYPES),comment='Type of interceptor'),
                Field('moorder',label='Order',comment='Interceptor will evaluate in descending order'),
                Field('mofilters', 'list:reference mt_filter', requires=IS_IN_DB(db,'mt_filter.id','mt_filter.fid',multiple=True),label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
                Field('moscript', label='Script',comment='Path and script must exist. Only python 3 scripts allowed now'))

db.define_table('j_imt',
                Field('mttype', requires=IS_IN_SET(IMT_TYPES), label='Type', comment='Type of interceptor'),
                Field('mtorder', label='Order', comment='Interceptor will evaluate in descending order'),
                Field('mtfilters', 'list:reference mt_filter',requires=IS_IN_DB(db,db.mt_filter._id, db.mt_filter.fid ,multiple=True),label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
                Field('mtscript', label='Script', comment='Path and script must exist. Only python 3 scripts allowed now'))

db.define_table('j_group',
                Field('name','string',length = 10, comment='Must be a string with no spaces or special characters'),
               format='%(name)s')

db.define_table('j_user',
                Field('username', 'string', length=10, comment="Jasmin User Name for HTTP and SMPP connecting. Must not include any spaces and can not be longer than 10 characters"),
                Field('password', 'string', length=10, comment='Jasmin Password for HTTP and SMPP connecting. Must not include any spaces and can not be longer than 10 characters'),
                Field('j_uid','string',label='Jasmin UID',length=12, comment='Jasmin UID cannot be longer than 12 characters and reccoment all in UPPER case. No spaces allowed. Suggest USER_1 etc.'),
                Field('j_group','reference j_group',label = 'Jasim GID', comment='Select a Group', requires=IS_IN_DB(db,'j_group.id','j_group.name')),
               format='%(username)s')

db.define_table('j_user_cred',
                Field('juser', 'string',label='Jasmin UID', length = 10),
                Field('default_src_addr', default='None', comment='Default source address of SMS-MT'),
                Field('quota_http_throughput',default='ND', comment='Max. number of messages per second to accept through HTTP API'),
                Field('quota_balance',default = 'ND', comment='c.f. 1. Balance quota'),
                Field('quota_smpps_throughput',default = 'ND', comment='Max. number of messages per second to accept through SMPP Server'),
                Field('quota_sms_count', default='ND', comment='c.f. 2. sms_count quota'),
                Field('quota_early_percent', default='ND', comment='c.f. Asynchronous billing'),
                Field('value_priority',default='^[0-3]$', comment='Regex pattern to validate priority of SMS-MT'),
                Field('value_content',default='.*', comment='Regex pattern to validate content of SMS-MT'),
                Field('value_src_addr', default='.*', comment='Regex pattern to validate source address of SMS-MT'),
                Field('value_dst_addr', default='.*', comment='Regex pattern to validate destination address of SMS-MT'),
                Field('value_validity_period', default='^\d+$', comment='Regex pattern to validate validity_period of SMS-MT'),
                Field('author_http_send',default=True, comment='Privilege to send SMS through Sending SMS-MT'),
                Field('author_http_dlr_method', default=True, comment='Privilege to set dlr-method HTTP parameter (default is GET)'),
                Field('author_http_balance', default= True, comment='Privilege to check balance through Checking account balance'),
                Field('author_smpps_send',default= True, comment='Privilege to send SMS through SMPP Server API'),
                Field('author_priority', default= True, comment='Privilege to defined priority of SMS-MT (default is 0)'),
                Field('author_http_long_content', default= True, comment='Privilege to send long content SMS through Sending SMS-MT'),
                Field('author_src_addr', default= True, comment='Privilege to defined source address of SMS-MT'),
                Field('author_dlr_level', default= True, comment='Privilege to set dlr-level parameter (default is 1)'),
                Field('author_http_rate', default =True, comment='Privilege to check a message rate through Checking rate price'),
                Field('author_validity_period', default=True, comment='Privilege to defined validity_period of SMS-MT (default is NOT SET)'),
                Field('author_http_bulk', default= False, comment='Privilege to send bulks through http api (Not implemented yet)'),
               format = '%(juser)s')


db.define_table('mo_filter',
                Field('fid', 'string', length=15, unique=True),
                Field('filter_type', requires=IS_IN_SET(MO_FILTER_TYPES)),
                Field('f_value', 'string', length = 50),
               format='%(name)s')

db.define_table('connector',
                Field('name','string',length=15, label='Connector ID',comment='Connector ID must be unique on each gateway', requires=[IS_LENGTH(minsize=1,maxsize=15),IS_NOT_IN_DB(db, 'connector.name')]),
                Field('c_logfile', label = 'Logfile',default='/var/log/jasmin/default-<cid>.log'),
                Field('c_logrotate', label = 'Log Rotate', default='midnight', comment='When to rotate the log file, possible values: S=Seconds, M=Minutes, H=Hours, D=Days, W0-W6=Weekday (0=Monday) and midnight=Roll over at midnight'),
                Field('c_loglevel', label = 'Log Level',default='20', comment='Logging numeric level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICCAL'),
                Field('c_host', label = 'Host',default='127.0.0.1', comment='Server that runs SMSC'),
                Field('c_port', label = 'Port',default='2775', comment='The port number for the connection to the SMSC'),
                Field('c_ssl', label = 'SSL', default='no', comment='Activate ssl connection'),
                Field('c_username', 'string', label = 'User name',length=15, comment='User name max 12 characters with no spaces'),
                Field('c_password', 'string', length=15, label = 'Password', comment='Password max 12 characters with no spaces'),
                Field('c_bind', label = 'Bind Type', requires=IS_IN_SET(('transceiver', 'transmitter', 'receiver')), default='transceiver', comment='Bind type: transceiver, receiver or transmitter'),
                Field('c_bind_to', label = 'Bind To', default='30', comment='Timeout for response to bind request'),
                Field('c_trx_to', label = 'Transmit Timeout',default='300', comment='Maximum time lapse allowed between transactions, after which, the connection is considered as inactive and will reconnect'),
                Field('c_res_to', label = 'Response Timeout',default='60', comment='Timeout for responses to any request PDU'),
                Field('c_pdu_red_to', label = 'PDU Read Timeout',default='10', comment='Timeout for reading a single PDU, this is the maximum lapse of time between receiving PDU’s header and its complete read, if the PDU reading timed out, the connection is considered as ‘corrupt’ and will reconnect'),
                Field('c_con_loss_retry', label = 'Coonection Loss Retry', default='yes', comment='Reconnect on connection loss ? (yes, no)'),
                Field('c_con_loss_delay', label = 'Connection Loss Delay',default='10', comment='Reconnect delay on connection loss (seconds)'),
                Field('c_con_fail_retry', label = 'Connection Fail Retry',default='yes', comment='Reconnect on connection failure ? (yes, no)'),
                Field('c_con_fail_delay', label = 'Connection Fail Delay',default='10', comment='Reconnect delay on connection failure (seconds)'),
                Field('c_src_addr', label = 'Default Source Address',default='Not defined', comment='Default source adress of each SMS-MT if not set while sending it, can be numeric or alphanumeric, when not defined it will take SMSC default'),
                Field('c_src_ton', label = 'Source TON',default='2', comment='Source address TON setting for the link: 0=Unknown, 1=International, 2=National, 3=Network specific, 4=Subscriber number, 5=Alphanumeric, 6=Abbreviated'),
                Field('c_src_npi', label = 'Source NPI',default='1', comment='Source address NPI setting for the link: 0=Unknown, 1=ISDN, 3=Data, 4=Telex, 6=Land mobile, 8=National, 9=Private, 10=Ermes, 14=Internet, 18=WAP Client ID'),
                Field('c_dst_ton', label = 'Destination TON',default='1', comment='Destination address TON setting for the link: 0=Unknown, 1=International, 2=National, 3=Network specific, 4=Subscriber number, 5=Alphanumeric, 6=Abbreviated'),
                Field('c_dst_npi', label = 'Destination NPI',default='1', comment='Destination address NPI setting for the link: 0=Unknown, 1=ISDN, 3=Data, 4=Telex, 6=Land mobile, 8=National, 9=Private, 10=Ermes, 14=Internet, 18=WAP Client ID'),
                Field('c_bind_ton', label = 'Bind TON',default='0', comment='Bind address TON setting for the link: 0=Unknown, 1=International, 2=National, 3=Network specific, 4=Subscriber number, 5=Alphanumeric, 6=Abbreviated'),
                Field('c_bind_npi', label = 'Bind NPI',default='1', comment='Bind address NPI setting for the link: 0=Unknown, 1=ISDN, 3=Data, 4=Telex, 6=Land mobile, 8=National, 9=Private, 10=Ermes, 14=Internet, 18=WAP Client ID'),
                Field('c_validity', label = 'Validtiy',default='Not defined', comment='Default validity period of each SMS-MT if not set while sending it, when not defined it will take SMSC default (seconds)'),
                Field('c_priority', label = 'Priority',default='0', comment='SMS-MT default priority if not set while sending it: 0, 1, 2 or 3'),
                Field('c_requeue_delay', label = 'Requeue Delay',default='120', comment='Delay to be considered when requeuing a rejected message'),
                Field('c_addr_range', label = 'Address Range',default='Not defined', comment='Indicates which MS’s can send messages to this connector, seems to be an informative value'),
                Field('c_systype', label = 'System Type',default='Not defined', comment='The system_type parameter is used to categorize the type of ESME that is binding to the SMSC. Examples include “VMS” (voice mail system) and “OTA” (over-the-air activation system)'),
                Field('c_dlr_expiry', label = 'DLR Expiry',default='86400', comment='When a SMS-MT is not acked, it will remain waiting in memory for expiry seconds, after this period, any received ACK will be ignored'),
                Field('c_submit_throughput', label = 'Submit Throughput',default='1', comment='Active SMS-MT throttling in MPS (Messages per second), set to 0 (zero) for unlimited throughput'),
                Field('c_proto_id', label = 'Protocol',default='0', comment='Used to indicate protocol id in SMS-MT and SMS-MO'),
                Field('c_coding',label = 'Coding',default='0', comment='Default coding of each SMS-MT if not set while sending it: 0=SMSC Default, 1=IA5 ASCII, 2=Octet unspecified, 3=Latin1, 4=Octet unspecified common, 5=JIS, 6=Cyrillic, 7=ISO-8859-8, 8=UCS2, 9=Pictogram, 10=ISO-2022-JP, 13=Extended Kanji Jis, 14=KS C 5601'),
                Field('c_elink_interval',label = 'Elink',default='30', comment='Enquire link interval (seconds)'),
                Field('c_def_msg_id',label = 'Default Msg ID',default='0', comment='Specifies the SMSC index of a pre-defined (‘canned’) message'),
                Field('c_ripf',label = 'Replace If Present',default='0', comment='Replace if present flag: 0=Do not replace, 1=Replace'),
                Field('c_dlr_msgid',label = 'DLR MsgID',default='0', comment='Indicates how to read msg id when receiving a receipt: 0=msg id is identical in submit_sm_resp and deliver_sm, 1=submit_sm_resp msg-id is in hexadecimal base, deliver_sm msg-id is in decimal base, 2=submit_sm_resp msg-id is in decimal base'),
               format='%(name)s')

db.define_table('http_cons',
                Field('hcon_cid','string',length=10,label='Connector ID', comment= 'Must be unique'),
                 Field('hcon_method', label='Method', comment='GET/POST',requires = IS_IN_SET(HTTP_CON_TYPE)),
                 Field('hcon_url',label='Base URL', comment='URL for MO messages e.g http://10.10.20.125/receive-sms/mo.php'), 
                 format='%(hcon_cid)s')

db.define_table('mtroute',
                Field('mt_order', 'string', length=10, label='Route order', requires=IS_NOT_EMPTY(), comment='Routes will be assesd in descending order based on filters and matches'),
                Field('mt_type', requires = IS_IN_SET(MTROUTE_TYPES), label='Route type'),
                Field('mt_connectors', 'list:reference connector', label='SMPP Connector(s)', comment='SMPP connector needs to be available'),
                Field('mt_filters', 'list:reference mt_filter',label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
                Field('mt_rate','string',length = 10, label='Rate', comment='Decimal rate value for the connector. All messages going over this connector will be charged at the rate specified'),

                format='%(mt_order)s')

db.define_table('moroute',
                Field('mo_order', 'string', length=10, label='Route order',comment='Routes will be assesd in descending order based on filters and matches'),
                Field('mo_type', requires = IS_IN_SET(MOROUTE_TYPES), label='Route type'),
                Field('mo_connectors', 'list:reference connector', requires=IS_IN_DB(db,'connector.id','connector.name',multiple=True), label='SMPP Connector(s)', comment='SMPP connector needs to be available'),
                Field('mo_http_cons', 'list:reference http_cons', requires=IS_IN_DB(db,'http_cons.id','http_hcons-hcons_cid', multiple=True), label='HTTP Connector(s)', comment='HTTP connector needs to be available'),
                Field('mo_filters', 'list:reference mt_filter', requires=IS_IN_DB(db,'mt_filter.id','mt_filter.fid',multiple=True), label='Filter(s)', comment='Filters need to be added prior to adding routes. Please see filter management'),
                format='%(mo_order)s')
db.commit() 