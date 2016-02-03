from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'Happy Goblin'
settings.subtitle = 'powered by web2py'
settings.author = 'Kalle Happonen'
settings.author_email = 'kalle.happonen@iki.fi'
settings.keywords = 'Magic the Gathering'
settings.description = ''
settings.layout_theme = 'Replenish'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = 'adef841e-1951-4d96-a8e9-4021a64dd54c'
settings.email_server = 'logging'
settings.email_sender = 'support@happygoblin.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
