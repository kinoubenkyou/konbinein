from mongoengine import DynamicDocument

from main.documents.activity import Activity


class UserActivity(Activity, DynamicDocument):
    pass
