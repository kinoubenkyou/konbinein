from mongoengine import DynamicDocument

from main.documents.activity import Activity


class OrganizationActivity(Activity, DynamicDocument):
    pass
