class WriteNestedMixin:
    @staticmethod
    def _write_nested_objects(
        object_data_list, object_dict, parent_key, parent_object, serializer
    ):
        for object_data in object_data_list:
            object_id = object_data.get("id")
            if object_id is None:
                serializer.create({**object_data, parent_key: parent_object})
            else:
                serializer.update(object_dict[object_id], object_data)
        for object_id, object_ in object_dict.items():
            if object_id not in (data.get("id") for data in object_data_list):
                object_.delete()
