"""The AaC No Ext for Final plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)

from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.context.source_location import SourceLocation
from typing import Any


plugin_name = "No Ext for Final"


def no_extension_for_final(
    instance: Any, definition: Definition, defining_schema
) -> ExecutionResult:
    """Business logic for the No Extension for Final constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []
    context = LanguageContext()
    if context.is_aac_instance(instance, "aac.lang.Schema"):
        if instance.extends:
            for ext in instance.extends:
                ext_definition = context.get_definitions_by_name(ext.name)
                if len(ext_definition) != 1:
                    status = ExecutionStatus.GENERAL_FAILURE
                    messages.append(
                        ExecutionMessage(
                            f"Cannot resolve unique tyep for extension {ext.name}.  Found {ext_definition}",
                            MessageLevel.ERROR,
                            None,  # TODO:  figure out a better want to handle this...maybe a util function?
                            None
                        )
                    )
                else:
                    ext_definition = ext_definition[0]
                    if ext_definition.instance.modifiers and "final" in ext_definition.instance.modifiers:
                        status = ExecutionStatus.CONSTRAINT_FAILURE
                        messages.append(
                            ExecutionMessage(
                                f"{definition.name} cannot extend {ext.name} because it is final.",
                                MessageLevel.ERROR,
                                None,  # TODO:  figure out a better want to handle this...maybe a util function?
                                None
                            )
                        )

    return ExecutionResult(plugin_name, "No Extension for Final", status, messages)
