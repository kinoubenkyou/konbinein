from mongoengine import DynamicDocument, IntField

from main.documents.activity import Activity


class OrderActivity(Activity, DynamicDocument):
    organization_id = IntField(required=True)
