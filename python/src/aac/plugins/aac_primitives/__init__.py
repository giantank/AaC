"""__init__.py module for the AaC primitive constraints plugin."""
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
    MessageLevel,
)
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.in_out.files.aac_file import AaCFile
from aac.execute.plugin_runner import PluginRunner
from aac.context.source_location import SourceLocation


from aac.plugins.aac_primitives.aac_primitive_constraints_impl import plugin_name


from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_bool
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_date
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_directory
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_file
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_string
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_int
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_number
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_dataref
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_typeref


aac_primitive_constraints_aac_file_name = "aac_primitive_constraints.aac"


def run_check_bool(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a boolen value is True, False, or None.  None is considered False by python, so we allow None as a valid value."""

    return check_bool(value, type_declaration, source, location)


def run_check_date(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a date value is interpretable as a date."""

    return check_date(value, type_declaration, source, location)


def run_check_directory(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a directory value is interpretable as a directory."""

    return check_directory(value, type_declaration, source, location)


def run_check_file(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a file value is interpretable as a file."""

    return check_file(value, type_declaration, source, location)


def run_check_string(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a string value is interpretable as a string."""

    return check_string(value, type_declaration, source, location)


def run_check_int(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that an integer value is interpretable as an integer."""

    return check_int(value, type_declaration, source, location)


def run_check_number(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a number value is interpretable as a number."""

    return check_number(value, type_declaration, source, location)


def run_check_dataref(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a data reference value is interpretable and exists."""

    return check_dataref(value, type_declaration, source, location)


def run_check_typeref(
    value: str,
    type_declaration: str,
    arguments: Any,
    source: AaCFile,
    location: SourceLocation,
) -> ExecutionResult:
    """Verify that a type reference value is interpretable and exists."""

    return check_typeref(value, type_declaration, source, location)


@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """

    active_context = LanguageContext()
    aac_primitive_constraints_aac_file = join(
        dirname(__file__), aac_primitive_constraints_aac_file_name
    )
    definitions = active_context.parse_and_load(aac_primitive_constraints_aac_file)

    aac_primitive_constraints_plugin_definition = [
        definition for definition in definitions if definition.name == plugin_name
    ][0]

    plugin_instance = aac_primitive_constraints_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)

    plugin_runner = PluginRunner(
        plugin_definition=aac_primitive_constraints_plugin_definition
    )

    plugin_runner.add_constraint_callback("Check bool", run_check_bool)
    plugin_runner.add_constraint_callback("Check date", run_check_date)
    plugin_runner.add_constraint_callback("Check directory", run_check_directory)
    plugin_runner.add_constraint_callback("Check file", run_check_file)
    plugin_runner.add_constraint_callback("Check string", run_check_string)
    plugin_runner.add_constraint_callback("Check int", run_check_int)
    plugin_runner.add_constraint_callback("Check number", run_check_number)
    plugin_runner.add_constraint_callback("Check dataref", run_check_dataref)
    plugin_runner.add_constraint_callback("Check typeref", run_check_typeref)

    active_context.register_plugin_runner(plugin_runner)
