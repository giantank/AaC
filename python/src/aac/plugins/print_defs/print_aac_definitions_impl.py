"""The AaC Print AaC Definitions plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)
from aac.context.language_context import LanguageContext, AAC_LANG_FILE_NAME
from aac.context.definition import Definition
from aac.in_out.parser._parse_source import parse
import yaml
from os.path import join, dirname
from os import linesep
import inspect

plugin_name = "Print AaC Definitions"


def print_defs(core_only: bool) -> ExecutionResult:
    """Print YAML representation of AaC language definitions."""

    messages: list[str] = []
    context: LanguageContext = LanguageContext()
    definitions: list[Definition] = []
    if core_only:
        definitions = parse(
            join(dirname(inspect.getfile(LanguageContext)), AAC_LANG_FILE_NAME)
        )
    else:
        definitions = context.get_definitions()

    for definition in definitions:
        messages.append(yaml.dump(definition.structure))
        messages.append("---")

    output_message = ExecutionMessage(
        linesep.join(messages), MessageLevel.INFO, None, None
    )

    return ExecutionResult(
        plugin_name, "print-defs", ExecutionStatus.SUCCESS, [output_message]
    )