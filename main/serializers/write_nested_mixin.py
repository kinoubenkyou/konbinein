class WriteNestedMixin:
    @staticmethod
    def _write_nested_objects(data_list, dict_, parent_key, parent_object, serializer):
        for data in data_list:
            id_ = data.get("id")
            if id_ is None:
                serializer.create({**data, parent_key: parent_object})
            else:
                serializer.update(dict_[id_], data)
        for id_, object_ in dict_.items():
            if id_ not in (data.get("id") for data in data_list):
                object_.delete()
