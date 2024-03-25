from mongoengine import DictField, IntField, StringField

from main.shortcuts import ActivityType


class Activity:
    creator_id = IntField()
    creator_organization_id = IntField()
    creator_type = StringField(choices=ActivityType.ALL, required=True)
    data = DictField()
    object_id = IntField(required=True)
