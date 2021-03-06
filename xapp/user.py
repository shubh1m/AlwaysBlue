from xapp.models import USERS_COLLECTION
from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, email, nickname=None, db=False):
        self.email = email
        self.nickname = nickname
        if db:
            USERS_COLLECTION.insert_one({
                '_id': self.email, 'nickname': self.nickname,
                'friends': [], 'groups': [], 'bills': []
                })

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def updateGroups(self, groupID):
        USERS_COLLECTION.find_one_and_update({
            '_id': ObjectId(groupID)}, {
            '$addToSet': {'groups': groupID}
        })

    def addUserToFriend(self, emailID):
        #if not USERS_COLLECTION.find_one({'_id': emailID}):
        #    usr = User(emailID)
        USERS_COLLECTION.find_one_and_update({'_id': emailID}, {'$addToSet': {'friends': self.email}}, upsert=True)

    def addFriend(self, emailID):
        USERS_COLLECTION.find_one_and_update({'_id': self.email}, {'$addToSet': {'friends': emailID}})
        self.addUserToFriend(emailID)