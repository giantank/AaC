"""AaC Plugin implementation module for the aac-gen-protobuf plugin."""

# NOTE: It is safe to edit this file.
# This file is only initially generated by the aac gen-plugin, and it won't be overwritten if the file already exists.

from iteration_utilities import flatten

from aac import parser, util
from aac.plugins import PluginError
from aac.plugins.plugin_execution import (
    PluginExecutionResult,
    plugin_result,
)
from aac.template_engine import (
    TemplateOutputFile,
    generate_template,
    load_default_templates,
    write_generated_templates_to_file,
)
from aac.validator import validation

plugin_name = "gen-protobuf"


def gen_protobuf(
    architecture_file: str, output_directory: str
) -> PluginExecutionResult:
    """
    Generate protobuf messages from Arch-as-Code models.

    Args:
        architecture_file (str): The yaml file containing the data models to generate as Protobuf
                                     messages.
        output_directory (str): The directory to write the generated Protobuf messages to.
    """

    def generate_protobuf():
        with validation(parser.parse_file, architecture_file) as validation_result:
            loaded_templates = load_default_templates("gen_protobuf")

            data_messages_and_enum_definitions = _collect_data_and_enum_definitions(
                validation_result.model
            )
            message_template_properties = (
                _generate_protobuf_template_details_from_data_and_enum_models(
                    data_messages_and_enum_definitions
                )
            )

            generated_template_messages = _generate_protobuf_messages(
                loaded_templates, message_template_properties
            )

            write_generated_templates_to_file(
                generated_template_messages, output_directory
            )

            return f"Successfully generated templates to directory: {output_directory}"

    with plugin_result(plugin_name, generate_protobuf) as result:
        return result


def _collect_data_and_enum_definitions(parsed_models: dict) -> dict[str, dict]:
    """
    Collect all data and enum definitions that are referenced as interface messages or as a nested type within an interface message.

    Args:
        parsed_models: A dict containing models parsed from an AaC yaml file.

    Returns:
        A dict of data message type keys to data message parsed model values
    """

    def collect_nested_types(interface_data_message_types: list[str]):
        nested_types = []
        for message_type in interface_data_message_types:
            data_model = parsed_models[message_type]["data"]

            for field in data_model.get("fields"):
                field_type = field.get("type")
                if field_type in parsed_models:
                    nested_types.append(field_type)

        return list(set(nested_types))

    def collect_behaviors(model_with_behaviors):
        return util.search(model_with_behaviors, ["model", "behavior"])

    def convert_behavior_io_to_data_type(behavior_io_model):
        return behavior_io_model.get("type")

    def collect_data_message_types(behavior_model):
        inputs = behavior_model.get("input") or []
        outputs = behavior_model.get("output") or []
        return list(map(convert_behavior_io_to_data_type, inputs + outputs))

    model_definitions = util.get_models_by_type(parsed_models, "model")
    behaviors = list(flatten(map(collect_behaviors, model_definitions.values())))
    interface_data_message_types = list(set(flatten(map(collect_data_message_types, behaviors))))
    all_definitions_types_to_generate = interface_data_message_types + collect_nested_types(
        interface_data_message_types
    )

    return {
        data_message_type: parsed_models[data_message_type]
        for data_message_type in all_definitions_types_to_generate
    }


def _generate_protobuf_template_details_from_data_and_enum_models(  # noqa: C901
    data_and_enum_models: dict,
) -> list[dict]:
    """
    Generate a list of template property dictionaries for each protobuf file to generate.

    Args:
        data_and_enum_models: a dict of models where the key is the model name and the value is the model dict

    Returns:
        a list of template property dicts
    """

    def get_properties_dict(
        name: str,
        definition_type: str,
        enums: list[str] = [],
        fields: list[dict] = [],
        imports: list[str] = [],
    ):
        properties = {
            "name": name,
            "file_type": definition_type,
        }

        if enums:
            properties["enums"] = enums
        if fields:
            properties["fields"] = fields
        if imports:
            properties["imports"] = imports

        return properties

    def get_enum_properties(enum_model):
        enum_name = enum_model.get("name")
        enum_values = [enum.upper() for enum in enum_model.get("values")]
        return get_properties_dict(enum_name, "enum", enums=enum_values)

    def get_data_model_properties(data_model):
        data_name = data_model.get("name")

        required_fields = data_model.get("required") or []

        message_fields = []
        message_imports = []
        for field in data_model.get("fields"):
            proto_field_name = field.get("name")
            proto_field_type = None

            field_type = field.get("type")
            field_proto_type = field.get("protobuf_type")
            field_proto_repeat = "[]" in field_type
            if field_type in data_and_enum_models:
                proto_field_type = field_type

                # This is the last time we have access to the other model, calculate its future protobuf file name here
                model_to_import = data_and_enum_models.get(field_type)
                model_to_import = model_to_import.get("data") or model_to_import.get("enum")
                message_imports.append(
                    _convert_message_name_to_file_name(model_to_import.get("name"))
                )

            else:
                # If the referenced type isn't a user-defined type, then set the primitive type prioritizing `protobuf_type` before `type`
                proto_field_type = field_proto_type or field_type

            message_fields.append(
                {
                    "name": proto_field_name,
                    "type": proto_field_type,
                    "optional": proto_field_name not in required_fields,
                    "repeat": field_proto_repeat,
                }
            )

        return get_properties_dict(
            data_name, "data", fields=message_fields, imports=message_imports
        )

    template_properties_list = []
    for data_or_enum_message_model in data_and_enum_models.values():
        data_model = data_or_enum_message_model.get("data")
        enum_model = data_or_enum_message_model.get("enum")

        if data_model:
            template_properties_list.append(get_data_model_properties(data_model))
        elif enum_model:
            template_properties_list.append(get_enum_properties(enum_model))

    return template_properties_list


def _generate_protobuf_messages(
    protobuf_message_templates: list, properties: list[dict]
) -> list[TemplateOutputFile]:
    """
    Compile templates and with variable properties information.

    File and general structure style will follow the google protobuf style which can be found at
        https://developers.google.com/protocol-buffers/docs/style

    Args:
        protobuf_message_templates: templates to generate against. (Should only be one template)
        properties: a list of dicts of properties

    Returns:
        list of template information dictionaries.
    """

    def generate_protobuf_message_from_template(properties) -> TemplateOutputFile:
        generated_template = generate_template(protobuf_template, properties)
        generated_template.file_name = _convert_message_name_to_file_name(properties.get("name"))
        generated_template.overwrite = True  # Protobuf files shouldn't be modified by the user, and so should always overwrite
        return generated_template

    # This plugin produces only protobuf messages and one message per file due to protobuf specifications. (it only needs one template)
    protobuf_template = None
    if len(protobuf_message_templates) != 1:
        raise GenerateProtobufException(
            f"Unexpected number of templates loaded {len(protobuf_message_templates)}, "
            f"expecting only protobuf message template.\nLoaded templates: {protobuf_message_templates}"
        )
    else:
        protobuf_template = protobuf_message_templates[0]

    return list(map(generate_protobuf_message_from_template, properties))


def _convert_message_name_to_file_name(message_name: str) -> str:
    """
    Convert a `data:` definition's name into an opinionated and stylized protobuf 3 file name.

    File and general structure style will follow the google protobuf style which can be found at
        https://developers.google.com/protocol-buffers/docs/style

    Args:
        message_name: the name of a `data:` definition to convert to a protobuf file name

    Returns:
        A protobuf file name string
    """
    new_file_name = f"{message_name}.proto"
    new_file_name = new_file_name.replace("- ", "_")
    new_file_name = _convert_camel_case_to_snake_case(new_file_name)
    return new_file_name


def _convert_camel_case_to_snake_case(camel_case_str: str) -> str:
    """
    Convert a camelCase string to a snake_case string.

    Args:
        camel_case_str: the camelCase string to convert

    Returns:
        a snake_case string
    """
    snake_case_str = camel_case_str[:1].lower()
    for char in camel_case_str[1:]:
        snake_case_str += (char, f"_{char.lower()}")[char.isupper()]
    return snake_case_str


class GenerateProtobufException(PluginError):
    """Exceptions specifically concerning protobuf message generation."""

    pass
