from datetime import datetime
from poop import objstore



class Comment(objstore.Item):


    __typename__ = 'comment'
    __table__ = 'comment'


    relatesToId = objstore.column('relates_to_id')
    relatesToVersion = objstore.column('relates_to_version')
    posted = objstore.column()
    approved = objstore.column()


    def __init__(self, *a, **k):
        relatesTo = k.pop('relatesTo')
        authorName = k.pop('authorName')
        authorEmail = k.pop('authorEmail')
        comment = k.pop('comment')
        super(Comment, self).__init__(*a, **k)
        if hasattr(relatesTo,'id'):
            self.relatesToId, self.relatesToVersion = relatesTo.id, relatesTo.version
        else:
            self.relatesToId, self.relatesToVersion = relatesTo,1
        self.authorName = authorName
        self.comment = comment
        self.authorEmail = authorEmail
        self.posted = datetime.utcnow()
        self.approved = False



def registerTypes(store):
    store.registerType(Comment)

