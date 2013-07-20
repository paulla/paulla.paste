import hashlib
import datetime

import couchdbkit

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_registry
from pyramid.events import NewRequest
from pyramid.events import subscriber

from beaker.cache import cache_region

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers

from paulla.paste.models import Paste

settings = get_current_registry().settings
# server object
server = couchdbkit.Server(settings['couchdb.url'])

# create database
db = server.get_or_create_db(settings['couchdb.db'])
Paste.set_db(db)

formatter = HtmlFormatter(linenos=True, full=True, cssclass="source")

@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {'lexers': lexers()}

def _buildPassword(username, createdTime, password):
    """
    """
    if not password:
        return ''

    tmp = ''.join((username, str(createdTime).split('.')[0], password, settings['salt']))

    sha1 = hashlib.sha224()
    sha1.update(tmp)

    return sha1.hexdigest()

@view_config(route_name='addContent', renderer='json')
def add(request):

    username = request.POST['username']
    password = ''

    now = datetime.datetime.now()

    if username:
      password = _buildPassword(username, now, request.POST['password'])

    paste = Paste(title=request.POST['title'],
                  content=request.POST['content'],
                  created=now,
                  typeContent=request.POST['type'],
                  username=username,
                  password=password)
    paste.save()

    request.session.flash(u"Add ok") # TODO translatoion

    return HTTPFound(request.route_path('oneContent', idContent=paste._id))


@view_config(route_name='oneContent', renderer='templates/content.pt')
def content(request):
    paste = Paste.get(request.matchdict['idContent'])
    lexer = get_lexer_by_name(paste.typeContent, stripall=True)

    result = highlight(paste['content'], lexer, formatter)

    return {'paste': paste,
            'content': result,}

@view_config(route_name='oneContentRaw', renderer='string' )
def contentRaw(request):
    paste = Paste.get(request.matchdict['idContent'])
    # TODO type/mime
    return paste.content


@cache_region('short_term', 'previous')
def previous():
    previousPastes = Paste.view('paste/all',  limit=10).all()
    return previousPastes

@cache_region('long_term', 'lexers')
def lexers():
    result = [(lexer[0], lexer[1][0]) for lexer in get_all_lexers()]
    result.sort()
    return result

@subscriber(NewRequest)
def previousEvent(event):
    event.request.previous = previous()

@view_config(route_name='edit', renderer='templates/edit.pt')
def edit(request):

    paste = Paste.get(request.matchdict['idContent'])

    return {'lexers': lexers(),
            'paste': paste,}

@view_config(route_name='update')
def update(request):
    paste = Paste.get(request.matchdict['idContent'])

    password = _buildPassword(paste.username, paste.created, request.POST['password'])

    if password == paste.password:
        paste.title = request.POST['title']
        paste.content = request.POST['content']

        paste.save()

        request.session.flash(u"Updated") # TODO translatoion

        return HTTPFound(request.route_path('oneContent', idContent=paste._id))

    request.session.flash(u"Wrong password") # TODO translatoion

    return HTTPFound(request.route_path('edit', idContent=paste._id))


@view_config(route_name='deleteConfirm', renderer='templates/delete_confirm.pt')
def deleteConfirm(request):
    paste = Paste.get(request.matchdict['idContent'])

    if not(paste.username and paste.password):
        return HTTPFound(request.route_path('oneContent', idContent=paste._id))

    lexer = get_lexer_by_name(paste.typeContent, stripall=True)

    result = highlight(paste['content'], lexer, formatter)

    return {'paste': paste,
            'content': result,}


@view_config(route_name='delete')
def delete(request):
    paste = Paste.get(request.matchdict['idContent'])

    password = _buildPassword(paste.username,
                              paste.created,
                              request.POST['password'])

    if password == paste.password:

        paste.delete()

        request.session.flash(u"Deleted") # TODO translatoion

        return HTTPFound(request.route_path('home', ))

    request.session.flash(u"Wrong password") # TODO translatoion

    return HTTPFound(request.route_path('deleteConfirm', idContent=paste._id))
