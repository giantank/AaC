"""AaC Plugin implementation module for the aac-gen-gherkin-behaviors plugin."""

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

plugin_name = "gen-gherkin-behaviors"


def gen_gherkin_behaviors(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Generate Gherkin feature files from Arch-as-Code model behavior scenarios.

    Args:
        architecture_file (str): The yaml file containing the data models to generate as Gherkin feature files.
        output_directory (str): The directory to write the generated Gherkin feature files to.
    """

    def generate_gherkin():
        with validation(parser.parse_file, architecture_file) as validation_result:
            loaded_templates = load_default_templates("gen_gherkin_behaviors")

            message_template_properties = _get_template_properties(validation_result.model)
            generated_template_messages = _generate_gherkin_feature_files(loaded_templates, message_template_properties)

            write_generated_templates_to_file(generated_template_messages, output_directory)

            return f"Successfully generated templates to directory: {output_directory}"

    with plugin_result(plugin_name, generate_gherkin) as result:
        return result


def _get_template_properties(parsed_models: dict) -> dict[str, dict]:
    """
    Generate a list of template property dictionaries for each gherkin feature file to generate.

    Args:
        parsed_models: a dict of models where the key is the model name and the value is the model dict

    Returns:
        a list of template property dictionaries
    """

    def collect_models(parsed_models: dict) -> dict:
        """Return a structured dict like parsed_models, but only consisting of model definitions."""
        return util.get_models_by_type(parsed_models, "model")

    def collect_model_behavior_properties(model: dict) -> list[dict]:
        """Produce a template property dictionary for each behavior entry in a model."""
        behaviors = model.get("model").get("behavior") or []

        return list(flatten(map(collect_behavior_entry_properties, behaviors)))

    def collect_behavior_entry_properties(behavior_entry: dict) -> list[dict]:
        """Produce a list of template property dictionaries from a behavior entry."""
        feature_name = behavior_entry.get("name")
        feature_description = (
            behavior_entry.get("description")
            or "TODO: Fill out this feature description."  # noqa: T101
        )
        behavior_scenarios = behavior_entry.get("acceptance") or []

        return [
            {
                "feature": {"name": feature_name, "description": feature_description},
                "scenarios": list(
                    flatten(map(collect_and_sanitize_scenario_steps, behavior_scenarios))
                ),
            }
        ]

    def collect_and_sanitize_scenario_steps(scenario: dict) -> dict:
        """Collect and sanitize scenario steps then return template properties for a 'scenarios' entry."""
        return [
            {
                "description": scenario.get("scenario")
                or "TODO: Write a description.",  # noqa: T101
                "givens": list(map(sanitize_scenario_step_entry, scenario.get("given"))),
                "whens": list(map(sanitize_scenario_step_entry, scenario.get("when"))),
                "thens": list(map(sanitize_scenario_step_entry, scenario.get("then"))),
            }
        ]

    def sanitize_scenario_step_entry(step: str) -> str:
        """Remove any conflicting keyword from the scenario step."""
        if does_step_start_with_gherkin_keyword(step):
            return step.split(None, 1)[1]

        return step

    def does_step_start_with_gherkin_keyword(step: str) -> bool:
        """
        Check if a string starts with a Gherkin keyword.

        Gherkin keywords can be found here: https://cucumber.io/docs/gherkin/reference/#keywords
        """
        gherkin_keywords = [
            "Feature",
            "Rule",
            "Example",
            "Given",
            "When",
            "Then",
            "And",
            "But",
            "Background",
            "Example",
            "Scenario",
            "Scenario Outline",
            "Scenario Template",
        ]

        return step.startswith(tuple(gherkin_keywords))

    return list(
        flatten(map(collect_model_behavior_properties, collect_models(parsed_models).values()))
    )


def _generate_gherkin_feature_files(
    gherkin_templates: list, properties_list: list[dict]
) -> list[TemplateOutputFile]:
    """
    Compile templates with variable properties information.

    Args:
        gherkin_templates: templates to generate against. (Should only be one template)
        properties_list: a list of template property dictionaries

    Returns:
        list of template information dictionaries
    """

    def generate_file(properties: dict) -> TemplateOutputFile:
        feature_name = properties.get("feature").get("name")

        generated_file = generate_template(gherkin_template, properties)
        generated_file.file_name = _create_gherkin_feature_file_name(feature_name)
        generated_file.overwrite = False

        return generated_file

    # This plugin produces only gherkin feature file and so it only needs one template
    gherkin_template = None
    if len(gherkin_templates) != 1:
        raise GenerateGherkinException(
            f"Unexpected number of templates loaded {len(gherkin_templates)}, \
                    expecting only gherkin feature file template. Loaded templates: {gherkin_templates}"
        )
    else:
        gherkin_template = gherkin_templates[0]

    return list(map(generate_file, properties_list))


def _create_gherkin_feature_file_name(behavior_name: str) -> str:
    sanitized_name = behavior_name.strip()

    for replacement in ((" ", "_"), ("-", "_")):
        sanitized_name = sanitized_name.replace(*replacement)

    return f"{sanitized_name}.feature"


class GenerateGherkinException(PluginError):
    """Exceptions specifically concerning gherkin feature file generation."""

    pass
