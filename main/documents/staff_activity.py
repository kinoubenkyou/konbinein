from mongoengine import DynamicDocument, IntField

from main.documents.activity import Activity


class StaffActivity(Activity, DynamicDocument):
    organization_id = IntField(required=True)
    user_id = IntField(required=True)
