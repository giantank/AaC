"""Generated AaC Plugin hookimpls module for the gen-plugin plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from aac.AacCommand import AacCommand, AacCommandArgument
from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.gen_plugin.gen_plugin_impl import generate_plugin


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Returns the gen-plugin command type to the plugin infrastructure.

    Returns:
        A list of AacCommands
    """

    command_arguments = [
        AacCommandArgument(
            "architecture_file",
            "The yaml file containing the AaC DSL of the plugin architecture.",
        )
    ]

    plugin_commands = [
        AacCommand(
            "gen-plugin",
            "Generates an AaC plugin from an AaC model of the plugin",
            generate_plugin,
            command_arguments,
        )
    ]

    return plugin_commands


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and data definitions employed by the plugin
    """

    return get_resource_file_contents(__package__, "gen_plugin.yaml")
