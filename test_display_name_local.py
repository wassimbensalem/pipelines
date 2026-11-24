#!/usr/bin/env python3
"""Test display_name feature using local execution.

This runs the pipeline locally to verify the feature works.
"""

from kfp import dsl
from kfp import local

# Configure local execution
local.init(runner=local.SubprocessRunner())


@dsl.component
def producer(text: str) -> str:
    """Producer component."""
    print(f"Producing: {text}")
    return text


@dsl.component
def consumer(text: str) -> str:
    """Consumer component."""
    print(f"Consuming: {text}")
    return text


@dsl.pipeline(name='display-name-local-test')
def display_name_local_test():
    """Test pipeline with display_name set on tasks."""
    # Task with display_name
    prod_task = producer(text='Hello World').set_display_name('Data Producer')
    
    # Task with display_name that depends on first task
    cons_task = consumer(text=prod_task.output).set_display_name('Data Consumer')
    
    return cons_task


if __name__ == '__main__':
    print("Running pipeline locally...")
    print("Note: Local execution doesn't create Kubernetes pods,")
    print("      but you can verify the DAG structure is correct.\n")
    
    result = display_name_local_test()
    print(f"\nPipeline execution completed!")
    print(f"Output: {result.output}")

