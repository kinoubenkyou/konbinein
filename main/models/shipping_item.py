from django.db.models import CharField, DecimalField, Model


class ShippingItem(Model):
    class Meta:
        abstract = True

    fixed_fee = DecimalField(decimal_places=4, max_digits=19)
    item_total = DecimalField(decimal_places=4, max_digits=19)
    name = CharField(max_length=255)
    unit_fee = DecimalField(decimal_places=4, max_digits=19)
