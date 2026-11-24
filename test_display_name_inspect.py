#!/usr/bin/env python3
"""Inspect compiled pipeline to see DAG task keys."""

import yaml
import sys


def inspect_pipeline(yaml_file):
    """Inspect the compiled pipeline YAML to show DAG task keys."""
    with open(yaml_file) as f:
        spec = yaml.safe_load(f)
    
    # Handle both direct pipeline spec and wrapped in PipelineJob
    if 'pipelineSpec' in spec:
        pipeline_spec = spec['pipelineSpec']
    else:
        pipeline_spec = spec
    
    if 'root' not in pipeline_spec:
        print("Error: Could not find root DAG in pipeline spec")
        return
    
    root = pipeline_spec['root']
    if 'dag' not in root or 'tasks' not in root['dag']:
        print("Error: Could not find tasks in root DAG")
        return
    
    tasks = root['dag']['tasks']
    
    print("=" * 60)
    print("DAG Task Keys (these become part of Kubernetes pod names)")
    print("=" * 60)
    print()
    
    for task_key, task_spec in tasks.items():
        print(f"Task Key: {task_key}")
        if 'taskInfo' in task_spec and 'name' in task_spec['taskInfo']:
            display_name = task_spec['taskInfo']['name']
            print(f"  Display Name: {display_name}")
        if 'dependentTasks' in task_spec and task_spec['dependentTasks']:
            print(f"  Dependencies: {', '.join(task_spec['dependentTasks'])}")
        print()
    
    print("=" * 60)
    print("Expected Pod Name Format:")
    print("  {workflow-name}-{task-key}-{hash}")
    print()
    print("Example:")
    print("  display-name-test-pipeline-{hash}-data-producer-{hash}")
    print("  display-name-test-pipeline-{hash}-data-consumer-{hash}")
    print("=" * 60)


if __name__ == '__main__':
    yaml_file = sys.argv[1] if len(sys.argv) > 1 else 'display_name_test_pipeline.yaml'
    inspect_pipeline(yaml_file)

