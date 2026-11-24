feat(sdk): Add dict parameter access for granular value extraction

Add support for extracting individual values from dictionary pipeline
parameters using Pythonic dict-style syntax (config['key']).

This enables:
- Single-level access: config['db_host']
- Nested access: config['database']['host']
- Sub-dict passing: config['database']

Changes:
- Add DictSubvariable class to represent extracted dict values
- Add __getitem__ to PipelineParameterChannel for dict-style access
- Extend compiler to generate CEL parameter_expression_selector
- Skip strict type checking for DictSubvariable (runtime resolution)
- Add comprehensive unit and integration tests

Benefits:
- Improved security (components receive only needed data)
- Better code clarity and reduced coupling
- No backend changes required (uses existing CEL evaluation)
- Fully backward compatible

Example usage:
  @dsl.pipeline
  def my_pipeline(config: dict):
      component1(host=config['database']['host'])
      component2(db_config=config['database'])

