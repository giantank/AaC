"""__init__.py module for the Version plugin."""
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
from aac.lang.schema import Schema
from aac.lang.plugininputvalue import PluginInputValue
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.execute.plugin_runner import PluginRunner
from aac.in_out.files.aac_file import AaCFile
from aac.context.source_location import SourceLocation


from aac.plugins.version.version_impl import plugin_name, version


version_aac_file_name = "version.aac"


def run_version() -> ExecutionResult:
    """Print the AaC package version."""

    result = ExecutionResult(plugin_name, "version", ExecutionStatus.SUCCESS, [])

    version_result = version()
    if not version_result.is_success():
        return version_result
    else:
        result.add_messages(version_result.messages)

    return result


@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """

    active_context = LanguageContext()
    version_aac_file = join(dirname(__file__), version_aac_file_name)
    definitions = active_context.parse_and_load(version_aac_file)

    version_plugin_definition = [
        definition for definition in definitions if definition.name == plugin_name
    ][0]

    plugin_instance = version_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)

    plugin_runner = PluginRunner(plugin_definition=version_plugin_definition)
    plugin_runner.add_command_callback("version", run_version)

    active_context.register_plugin_runner(plugin_runner)
