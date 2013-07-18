import couchdbkit


class Paste(couchdbkit.Document):
    title = couchdbkit.StringProperty()
    content = couchdbkit.StringProperty()
    created = couchdbkit.DateTimeProperty()
    user = couchdbkit.StringProperty()
    password = couchdbkit.StringProperty()
    typeContent = couchdbkit.StringProperty()
