# -*- coding: utf-8 -*-
from gluon import current
from gluon.custom_import import track_changes; track_changes(True)
import config

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
#db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
db = DAL(config.dal_url,pool_size=1)
current.db = db
#if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    #db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
#else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    #db = DAL('google:datastore')
    ## store sessions and tickets there
    #session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

db.define_table('player',
                 Field('name'),
                 Field('tappedaccount'),
                 Field('deckboxaccount'),
                 Field('guestplayer', 'boolean', default=False),
                 Field('linked', 'boolean', default=False),
                 Field('last_update', 'datetime'),
                 Field('country'),
                 format='%(name)s')

db.define_table('deck',
                 Field('name'),
                 Field('link'),
                 Field('type'),
                 Field('owner', 'reference player'),
                 format='%(name)s')

db.define_table('playgroup',
                  Field('name'),
                  Field('country'),
                  Field('open', 'boolean', notnull=True),
                  Field('useronly', 'boolean', notnull=True, default=False),
                  Field('last_update', 'datetime'),
                  format='%(name)s')

db.define_table('groupplayer',
                  Field('player', 'reference player'),
                  Field('playgroup', 'reference playgroup'),
                  Field('defaultgroup', 'boolean', default=False),
                  Field('role'))

db.define_table('game',
                  Field('playgroup', 'reference playgroup'),
                  Field('gametype'),
                  Field('format'),
                  Field('game', 'integer', default=1),
                  Field('onplay', 'integer'),
                  Field('playeramount'),
                  Field('result'),
                  Field('timestarted', 'datetime'),
                  Field('timeended', 'datetime'),
                  Field('tags', 'string'))

db.define_table('game_players',
                  Field('game', 'reference game'),
                  Field('winner', 'boolean'),
                  Field('player', 'reference player'),
                  Field('position', 'integer'),
                  Field('deck', 'reference deck'))


db.define_table('ongoing_game',
                  Field('playgroup', 'reference playgroup'),
                  Field('last_update_id', 'integer', default=0),
                  Field('gametype'),
                  Field('format'),
                  Field('game', 'integer', default=1),
                  Field('onplay', 'integer'),
                  Field('playeramount', 'integer'),
                  Field('timestarted', 'datetime'),
                  Field('tags', 'string'),
                  Field('p1life', 'integer'),
                  Field('p2life', 'integer'),
                  Field('p3life', 'integer'),
                  Field('p4life', 'integer'),
                  Field('p5life', 'integer'),
                  Field('p6life', 'integer'),
                  Field('p1poison', 'integer'),
                  Field('p2poison', 'integer'),
                  Field('p3poison', 'integer'),
                  Field('p4poison', 'integer'),
                  Field('p5poison', 'integer'),
                  Field('p6poison', 'integer'),
                  Field('p1cmdr', 'list:integer'),
                  Field('p2cmdr', 'list:integer'),
                  Field('p3cmdr', 'list:integer'),
                  Field('p4cmdr', 'list:integer'),
                  Field('p5cmdr', 'list:integer'),
                  Field('p6cmdr', 'list:integer'),
                  Field('p1deck', 'string'), 
                  Field('p2deck', 'string'), 
                  Field('p3deck', 'string'), 
                  Field('p4deck', 'string'), 
                  Field('p5deck', 'string'), 
                  Field('p6deck', 'string'))

db.define_table('ongoing_game_players',
                  Field('ongoing_game', 'reference ongoing_game'),
                  Field('position', 'integer'),
                  Field('player', 'reference player'))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)

from gluon.contrib.login_methods.browserid_account import BrowserID
crud, service, plugins = Crud(db), Service(), PluginManager()

#auth.settings.extra_fields['auth_user']=[Field('tappedotaccount'), Field('country')]
auth.settings.extra_fields['auth_user']=[Field('player','reference player', notnull=False)]
## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

# Mozilla persona
auth.settings.login_form = BrowserID(request,
        audience = config.persona_audience,
        assertion_post_url = config.persona_audience + "%sdefault/user/login" % config.base_url, 
        prompt = "Mozilla Persona login",
        on_login_failure = config.persona_audience + "%sdefault/index"  % config.base_url,
        )
auth.settings.expiration = 3600 * 24 * 365
response.cookies[response.session_id_name]['expires'] = 3600 * 24 * 365

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = False

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login



