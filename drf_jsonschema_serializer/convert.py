# convert a serializer to a JSON Schema.
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

field_to_converter: ClassLookupDict = ClassLookupDict({})


def converter(converter_class):
    """Decorator to register a converter class"""
    if isinstance(converter_class.field_class, list):
        field_classes = converter_class.field_class
    else:
        field_classes = [converter_class.field_class]
    for field_class in field_classes:
        field_to_converter[field_class] = converter_class()
    return converter_class


def field_to_jsonschema(
    field,
    skip_readonly=True,
    include_title=True,
    include_description=True,
):
    if isinstance(field, serializers.Serializer):
        result = to_jsonschema(field, skip_readonly=skip_readonly)
    else:
        converter = field_to_converter[field]
        result = converter.convert(field)

    if result is None:
        return None

    if include_title and field.label:
        result["title"] = field.label
    if include_description and field.help_text:
        result["description"] = field.help_text
    return result


def to_jsonschema(
    serializer,
    skip_readonly=True,
    include_title=True,
    include_description=True,
):
    properties = {}
    required = []
    for name, field in serializer.fields.items():
        if skip_readonly and field.read_only:
            continue
        sub_schema = field_to_jsonschema(
            field,
            skip_readonly=skip_readonly,
            include_title=include_title,
            include_description=include_description,
        )
        if sub_schema is None:
            continue

        if field.required:
            required.append(name)
        properties[name] = sub_schema

    result = {"type": "object", "properties": properties}
    if required:
        result["required"] = required
    return result
