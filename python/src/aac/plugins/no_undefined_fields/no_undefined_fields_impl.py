"""The AaC No Undefined Fields plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
)
from aac.lang.schema import Schema
from aac.lang.plugininputvalue import PluginInputValue
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.context.source_location import SourceLocation
from typing import Any


plugin_name = "No Undefined Fields"


def no_extra_fields(
    instance: Any, definition: Definition, defining_schema: Schema
) -> ExecutionResult:
    """Business logic for the No extra fields constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []


    def parent_class_defined_fields(parent_package: str, parent_name: str) -> list[str]:
        """Returns a list of defined fields for the parent class."""
        context: LanguageContext = LanguageContext()
        parent_schema = context.get_definition_by_name(parent_name)
        if not parent_schema:
            raise Exception(f"Could not find parent schema {parent_name} for {definition.name}")
        result = [field.name for field in parent_schema.instance.fields]
        if parent_schema.instance.extends:
            for parent in parent_schema.instance.extends:
                result.extend(parent_class_defined_fields(parent.package, parent.name))
        return result

    defined_fields = [field.name for field in defining_schema.fields]
    if defining_schema.extends:
        for parent in defining_schema.extends:
            defined_fields.extend(parent_class_defined_fields(parent.package, parent.name))
    for instance_field_name in [var for var in dir(instance) if not callable(getattr(instance, var)) and not var.startswith("__")]: # list(vars(instance).keys()):
        if instance_field_name not in defined_fields:
            status = ExecutionStatus.CONSTRAINT_FAILURE
            error_msg = ExecutionMessage(
                message=f"Field '{instance_field_name}' is not defined in the schema {defining_schema.name}.",
                source=definition.source,
                location=None,
            )
            messages.append(error_msg)
            raise Exception(error_msg.message)
    
    return ExecutionResult(plugin_name, "No extra fields", status, messages)
