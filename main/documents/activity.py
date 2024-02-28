from mongoengine import DynamicDocument, IntField, StringField


class Activity:
    action = StringField()
    instance_id = IntField()
    meta = {"indexes": [("instance_id", "_id")]}
    user_id = IntField()
    user_name = StringField()


class AdminOrganizationActivity(Activity, DynamicDocument):
    pass


class OrderActivity(Activity, DynamicDocument):
    pass


class OrderShippingActivity(Activity, DynamicDocument):
    pass


class OrganizationActivity(Activity, DynamicDocument):
    pass


class ProductActivity(Activity, DynamicDocument):
    pass


class ProductShippingActivity(Activity, DynamicDocument):
    pass


class StaffActivity(Activity, DynamicDocument):
    pass


class UserActivity(Activity, DynamicDocument):
    pass


class UserStaffActivity(Activity, DynamicDocument):
    pass
