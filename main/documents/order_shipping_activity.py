from mongoengine import DynamicDocument, IntField

from main.documents.activity import Activity


class OrderShippingActivity(Activity, DynamicDocument):
    organization_id = IntField(required=True)
