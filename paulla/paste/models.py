import couchdbkit
class Paste(couchdbkit.Document):
    title = couchdbkit.StringProperty()
    content = couchdbkit.StringProperty()
    created = couchdbkit.DateTimeProperty()
    typeContent = couchdbkit.StringProperty()
