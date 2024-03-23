from mongoengine import DynamicDocument, IntField

from main.documents.activity import Activity


class ProductActivity(Activity, DynamicDocument):
    organization_id = IntField(required=True)
