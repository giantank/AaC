"""The AaC CheckAaC plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from typing import Callable, Any
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus, ExecutionMessage, MessageLevel
from aac.context.language_error import LanguageError
# from aac.lang.primitive import Primitive
# from aac.lang.schema import Schema
# from aac.lang.schemaconstraintassignment import SchemaConstraintAssignment
# from aac.lang.field import Field

plugin_name = "CheckAaC"


def check(aac_file: str, fail_on_warn: bool, verbose: bool) -> ExecutionResult:
    """Business logic for the check command."""

    constraint_results: dict[str, list[ExecutionResult]] = {}

    context: LanguageContext = LanguageContext()

    # collect all constraints for easy access
    all_constraints_by_name: dict[str, Callable] = {}
    for runner in context.get_plugin_runners():
        for name, callback in runner.constraint_to_callback.items():
            all_constraints_by_name[name] = callback

    # we'll need to resurse our way through the schema to check all the constraints
    # so we'll create a couple functions to help us navigate the way
    def check_primitive_constraint(field, source_definition: Definition, value_to_check: Any, primitive_declaration: str, defining_primitive):
        """Runs all the constraints for a given primitive."""

        # Check the value_to_check against the defining_primitive
        defining_primitive_instance = defining_primitive
        for constraint_assignment in defining_primitive_instance.constraints:
            constraint_name = constraint_assignment.name
            constraint_args = constraint_assignment.arguments
            callback = all_constraints_by_name[constraint_name]
            # TODO: fix this location hack!
            locations = [lexeme.location for lexeme in source_definition.lexemes if lexeme.value == field.name]
            location = None
            if len(locations) > 0:
                location = locations[0]

            result: ExecutionResult = callback(
                value_to_check, 
                primitive_declaration, 
                constraint_args, 
                source_definition.source, 
                location
                )
            if constraint_name not in constraint_results:
                constraint_results[constraint_name] = []
            constraint_results[constraint_name].append(result)

    def check_schema_constraint(source_definition: Definition, check_me: Any, check_against):
        """Runs all the constraints for a given schema."""
        # make sure we've got a schema
        context = LanguageContext()
        if not context.is_aac_instance(check_against, "aac.lang.Schema"):
            return
        
        # collact applicable constraints
        schema_constraints = []
        for runner in context.get_plugin_runners():
            plugin = runner.plugin_definition.instance
            for constraint in plugin.schema_constraints:
                if constraint.universal:
                    schema_constraints.append(context.create_aac_object("SchemaConstraintAssignment", {"name": constraint.name, "arguments": []}))
        if check_against.constraints:
            for constraint_assignment in check_against.constraints:
                schema_constraints.append(constraint_assignment)
        
        # Check the check_me against constraints in the defining_schema
        for constraint_assignment in schema_constraints:
            constraint_name = constraint_assignment.name
            constraint_args = constraint_assignment.arguments
            callback = all_constraints_by_name[constraint_name]
            result: ExecutionResult = callback(check_me, source_definition, check_against, constraint_args)
            # TODO this would be a good place to add some verbose logging
            if constraint_name not in constraint_results:
                constraint_results[constraint_name] = []
            constraint_results[constraint_name].append(result)

        # loop through the fields on the check_against schema
        for field in check_against.fields:
            # only check the field if it is present
            if not hasattr(check_me, field.name):
                continue

            # get the name of the schema that defines the field, special handling for arrays and references
            type_name = field.type
            is_list = False
            # if type name ends with "[]", remove the brackets and set is_list to True
            if field.type.endswith("[]"):
                type_name = field.type[:-2]
                is_list = True
            # if type name has parameters in perens, remove them
            if type_name.find("(") > -1:
                type_name = type_name[:type_name.find("(")]
            
            # get the definition that defines the field
            field_definining_schema = context.get_definitions_by_name(type_name)

            if len(field_definining_schema) != 1:
                # TODO: convert this to a Constraint Failure
                raise LanguageError(f"Could not find unique schema definition for field type {field.type} with name {field.name}")
            
            if field_definining_schema[0].get_root_key() == "primitive":
                # if the field is a primitive, run the primitive constraints
                if is_list:
                    # if the field is a list, check each item in the list
                    for item in getattr(check_me, field.name):
                        value_to_check = item
                        if value_to_check is not None:
                            check_primitive_constraint(field, source_definition, item, field.type[:-2],field_definining_schema[0].instance)
                else:
                    value_to_check = getattr(check_me, field.name)
                    if value_to_check is not None:
                        check_primitive_constraint(field, source_definition, value_to_check, field.type, field_definining_schema[0].instance)
            else:
                # if the field is a schema, run the schema constraints
                if is_list:
                    # if the field is a list, check each item in the list
                    for item in getattr(check_me, field.name):
                        check_schema_constraint(source_definition, item, field_definining_schema[0].instance)
                else:
                    check_schema_constraint(source_definition, getattr(check_me, field.name), field_definining_schema[0].instance)
    
    # now that the helper functions are in place, let's run the constraints on the aac_file
    definitions_to_check = context.parse_and_load(aac_file)

    # First run all context constraint checks
    # Context constraints are "language constraints" and are not tied to a specific schema
    # You can think of these as "invariants", so they must always be satisfied
    for plugin in context.get_definitions_by_root("plugin"):
        # we want to check contest constraints, but not the ones that are defined in the aac_file we're checking to avoid gen-plugin circular logic
        for context_constraint in plugin.instance.context_constraints:
            if context_constraint.name not in [definition.name for definition in definitions_to_check]:
                continue
            callback = all_constraints_by_name[context_constraint.name]
            result: ExecutionResult = callback(context)
            if context_constraint.name not in constraint_results:
                constraint_results[context_constraint.name] = []
            constraint_results[context_constraint.name].append(result)

    for check_me in definitions_to_check:
        defining_schema = context.get_defining_schema_for_root(check_me.get_root_key())
        check_schema_constraint(check_me, check_me.instance, defining_schema.instance)

    # loop through all the constraint results and see if any of them failed
    messages = []
    status = ExecutionStatus.SUCCESS
    for name, results in constraint_results.items():
        for result in results:
            if result.is_success():
                # if the result is a success, add the messages to the list if we're in verbose mode
                # because these should only be info messages
                if verbose:
                    messages.extend(result.messages)
            elif result.status_code == ExecutionStatus.CONSTRAINT_WARNING:
                # if the result is a warning, add the messages to the list and fail the check if fail_on_warn is true
                if fail_on_warn:
                    status = ExecutionStatus.CONSTRAINT_FAILURE
                messages.extend(result.messages)
            else:
                # Any failure (including a constraint failure) is handled the same way
                messages.extend(result.messages)
                # don't change the status if already a failure
                if status != ExecutionStatus.CONSTRAINT_FAILURE:
                    status = result.status_code

    # after goign through all the constraint results, if we're still success add a success message
    if verbose:
        for check_me in definitions_to_check:
            messages.append(ExecutionMessage(f"Check {check_me.source.uri} - {check_me.name} was successful.", MessageLevel.DEBUG, None, None))
    if status == ExecutionStatus.SUCCESS:
        happy_msg = ExecutionMessage(message="All AaC constraint checks were successful.", level=MessageLevel.INFO, source=None, location=None)
        messages.append(happy_msg)

    return ExecutionResult(
        plugin_name, "check", status, messages
    )


