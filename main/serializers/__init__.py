def _write_nested_objects(
    data_list,
    object_dict,
    parent_key,
    parent_object,
    partial,
    serializer_class,
):
    for data in data_list:
        id_ = data.get("id")
        if id_ is None:
            serializer_class().create({**data, parent_key: parent_object})
        else:
            serializer_class(partial=partial).update(object_dict[id_], data)
    for id_, object_ in object_dict.items():
        if id_ not in (data.get("id") for data in data_list):
            object_.delete()
