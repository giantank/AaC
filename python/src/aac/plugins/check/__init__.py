"""__init__.py module for the CheckAaC plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from os.path import join, dirname
from copy import deepcopy
from typing import Any
from aac.execute.plugin_runner import AacCommand
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
)
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.in_out.files.aac_file import AaCFile
from aac.execute.plugin_runner import PluginRunner
from aac.context.source_location import SourceLocation


from aac.plugins.check.checkaac_impl import plugin_name, check


checkaac_aac_file_name = "checkaac.aac"


def run_check(aac_file, fail_on_warn, verbose) -> ExecutionResult:
    """Perform AaC file quality checks using defined constraints in the AaC models."""

    result = ExecutionResult(plugin_name, "check", ExecutionStatus.SUCCESS, [])

    check_result = check(aac_file, fail_on_warn, verbose)
    if not check_result.is_success():
        return check_result
    else:
        result.add_messages(check_result.messages)

    return result


@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """

    active_context = LanguageContext()
    checkaac_aac_file = join(dirname(__file__), checkaac_aac_file_name)
    definitions = active_context.parse_and_load(checkaac_aac_file)

    checkaac_plugin_definition = [
        definition for definition in definitions if definition.name == plugin_name
    ][0]

    plugin_instance = checkaac_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)

    plugin_runner = PluginRunner(plugin_definition=checkaac_plugin_definition)
    plugin_runner.add_command_callback("check", run_check)

    active_context.register_plugin_runner(plugin_runner)
