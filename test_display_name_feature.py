#!/usr/bin/env python3
"""Test script to verify display_name affects pod names.

This script creates a simple pipeline with tasks that have display_name set,
compiles it, and shows the DAG task keys (which become pod names).
"""

from kfp import dsl
from kfp import compiler


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


@dsl.pipeline(name='display-name-test-pipeline')
def display_name_test_pipeline():
    """Test pipeline with display_name set on tasks."""
    # Task with display_name
    prod_task = producer(text='Hello World').set_display_name('Data Producer')
    
    # Task with display_name that depends on first task
    cons_task = consumer(text=prod_task.output).set_display_name('Data Consumer')
    
    # Task without display_name (backward compatibility test)
    no_display_task = producer(text='No Display Name')


if __name__ == '__main__':
    # Compile the pipeline
    compiler.Compiler().compile(
        pipeline_func=display_name_test_pipeline,
        package_path='display_name_test_pipeline.yaml'
    )
    
    print("Pipeline compiled successfully!")
    print("\nTo inspect the compiled pipeline:")
    print("  cat display_name_test_pipeline.yaml | grep -A 5 'tasks:'")
    print("\nTo check DAG task keys (which become pod names):")
    print("  python3 -c \"")
    print("import yaml")
    print("with open('display_name_test_pipeline.yaml') as f:")
    print("    spec = yaml.safe_load(f)")
    print("    if 'pipelineSpec' in spec:")
    print("        tasks = spec['pipelineSpec']['root']['dag']['tasks']")
    print("        print('DAG Task Keys (pod names will be based on these):')")
    print("        for key in tasks.keys():")
    print("            print(f'  - {key}')")
    print("            if 'taskInfo' in tasks[key] and 'name' in tasks[key]['taskInfo']:")
    print("                print(f'    Display Name: {tasks[key][\"taskInfo\"][\"name\"]}')")
    print("\"")

