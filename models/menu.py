response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Home'),URL('default','index')==URL(),URL('default','index'),[]),
(T('New game'),URL('newgame','newgame')==URL(),URL('newgame','newgame'),[]),
(T('Stats'),URL('default','index')==URL(),URL('stats','stats'),[]),
(T('Settings'),URL('settings','settings')==URL(),URL('settings','playgroup'),[]),
]
response.submenu = []