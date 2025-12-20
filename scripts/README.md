# Scripts & Examples

Demonstration scripts, test utilities, and examples for the SmartThings MCP & Agent project.

## Connection & Setup

- **mcp_connection_test.py** - Test SmartThings connection and verify PAT token
  ```bash
  python scripts/mcp_connection_test.py
  ```

## Examples

- **example_activities.py** - Device activity queries
- **example_double_confirmation.py** - Safety confirmation pattern
- **example_mandatory_preaction_checks.py** - Pre-action validation
- **example_react_enforcement.py** - ReAct pattern implementation

## Testing

- **test_device_info.py** - Test device information queries
- **test_ambiguous.py** - Test ambiguity resolution
- **test_attribute_queries.py** - Test attribute queries
- **test_evaluation.py** - Test evaluation logic
- **test_filtered_responses.py** - Test response filtering
- **test_llm_iteration.py** - Test LLM iteration
- **test_main_program.py** - Test main agent logic
- **test_status_endpoint.py** - Test status endpoint
- **test_workflow.py** - Test complete workflow
- **test_air_quality_fix.py** - Test air quality query fix
- **verify_exact_examples.py** - Verify example outputs
- **verify_tools_catalog.py** - Verify tools catalog

## Demonstrations

- **demonstrate_fix.py** - Demonstrate specific fix
- **demo_activities_fix.py** - Demonstrate activities API fix

## Running Examples

```bash
cd scripts/

# Test connection
python mcp_connection_test.py

# Run an example
python example_activities.py

# Run a test
python test_main_program.py
```

## Output Files

- **test_output.txt** - Test execution output
- **test_run_2.txt** - Additional test results

See [../docs/EXAMPLES.md](../docs/EXAMPLES.md) for usage patterns and best practices.
