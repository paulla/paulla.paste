import couchdbkit
import datetime

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



@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {'lexers': lexers()}

@view_config(route_name='addContent', renderer='json')
def add(request):
    paste = Paste(title=request.POST['title'],
                  content=request.POST['content'],
                  created=datetime.datetime.now(),
                  typeContent=request.POST['type'])
    paste.save()
    request.session.flash(u"Add ok")
    return HTTPFound(request.route_path('oneContent', idContent=paste._id))


@view_config(route_name='oneContent', renderer='templates/content.pt')
def content(request):
    paste = Paste.get(request.matchdict['idContent'])
    lexer = get_lexer_by_name(paste.typeContent, stripall=True)
    formatter = HtmlFormatter(linenos=True, full=True, cssclass="source")

    result = highlight(paste['content'], lexer, formatter)

    return {'paste': paste,
            'content':result,}

@view_config(route_name='oneContentRaw', renderer='json', accept='application/json')
def contentRawJson(request):
    paste = Paste.get(request.matchdict['idContent'])
    return paste.content

@view_config(route_name='oneContentRaw', renderer='xml', accept='application/xml')
def contentRawXml(request):
    paste = Paste.get(request.matchdict['idContent'])
    return '<xml>'+paste.content+'</xml>'


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
