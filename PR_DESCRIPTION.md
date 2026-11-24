# Add Dict Parameter Access Feature for Pipeline Parameters

## Summary

This PR adds support for extracting individual values from dictionary pipeline parameters using Pythonic syntax, eliminating the need to pass entire dictionaries to components that only need specific values.

## Motivation

Previously, when a pipeline had a dictionary parameter, the entire dictionary had to be passed to every component, even if the component only needed a single value or subset. This led to:
- Unnecessary data exposure to components
- Reduced code clarity
- Potential security concerns with passing sensitive data unnecessarily

## Changes

### 1. New `DictSubvariable` Class (`sdk/python/kfp/dsl/pipeline_channel.py`)
- Introduced `DictSubvariable` class to represent values extracted from dict parameters
- Added `__getitem__` method to `PipelineParameterChannel` to enable dict-style access
- Supports both single-level and nested dict access
- Supports passing sub-dictionaries to components

### 2. Compiler Support (`sdk/python/kfp/compiler/pipeline_spec_builder.py`)
- Extended compiler to recognize `DictSubvariable` instances
- Generates appropriate CEL (Common Expression Language) `parameter_expression_selector` expressions
- Supports nested access by building chained CEL expressions
- Works in both task and group contexts

### 3. Type Checking (`sdk/python/kfp/dsl/pipeline_task.py`)
- Modified type compatibility checking to skip strict validation for `DictSubvariable`
- Actual types are resolved at runtime by the CEL evaluator

### 4. Tests
- Added comprehensive unit tests in `pipeline_channel_test.py`
- Added integration test pipeline in `test_data/pipeline_files/valid/pipeline_with_dict_parameter_access.py`

## Usage Examples

### Single-Level Access
```python
@dsl.pipeline
def my_pipeline(config: dict):
    # Extract a single value
    component1(db_host=config['db_host'])
```

### Nested Access
```python
@dsl.pipeline
def my_pipeline(config: dict):
    # Access nested values
    component2(host=config['database']['host'])
    component3(username=config['database']['credentials']['username'])
```

### Sub-Dictionary Passing
```python
@dsl.pipeline
def my_pipeline(config: dict):
    # Pass an entire sub-dictionary
    component4(db_config=config['database'])
```

## Technical Details

### Compile-Time vs Runtime
- **Compile-time**: The SDK creates `DictSubvariable` objects and the compiler generates CEL expressions
- **Runtime**: The backend driver evaluates CEL expressions to extract values from the actual JSON data

### CEL Expression Generation
- Single: `parseJson(string_value)["key"]`
- Nested: `parseJson(string_value)["database"]["host"]`
- Backend already supports these expressions (no backend changes required)

## Benefits

1. **Improved Security**: Components only receive the data they need
2. **Better Code Clarity**: Clear intent about what data each component uses
3. **Reduced Coupling**: Components don't depend on entire config structures
4. **Type Safety**: Type checking happens at runtime based on actual values
5. **Backward Compatible**: Existing code continues to work unchanged

## Testing

Run unit tests:
```bash
pytest -v sdk/python/kfp/dsl/pipeline_channel_test.py::DictSubvariableTest
```

Run integration test:
```bash
python test_data/pipeline_files/valid/pipeline_with_dict_parameter_access.py
```

## Checklist
- [x] Added unit tests
- [x] Added integration test
- [x] Code follows project formatting standards (isort)
- [x] All tests pass
- [x] No breaking changes
- [x] Documentation (docstrings) added

## Related Issues

Closes #[issue_number] (if applicable)

## Additional Notes

This feature leverages existing backend CEL expression evaluation capabilities, so no server-side changes are required. All changes are SDK-side and applied at compile time.

