# Testing display_name Feature for Pod Names

This guide explains how to test the `set_display_name()` feature that affects Kubernetes pod names.

## Prerequisites

1. **SDK installed in development mode:**
   ```bash
   cd sdk/python
   pip install -e . --config-settings editable_mode=strict
   ```

2. **For local testing:** No additional setup needed
3. **For cluster testing:** A running KFP cluster (Kind cluster or real cluster)

## Testing Methods

### Method 1: Compile and Inspect (Quickest)

This method compiles the pipeline and shows the DAG task keys without running it.

```bash
# Run the test script
python3 test_display_name_feature.py

# Inspect the compiled pipeline
python3 test_display_name_inspect.py display_name_test_pipeline.yaml
```

**Expected Output:**
```
DAG Task Keys (these become part of Kubernetes pod names)
============================================================

Task Key: data-producer
  Display Name: Data Producer

Task Key: data-consumer
  Display Name: Data Consumer
  Dependencies: data-producer

Task Key: producer  (or similar - this one has no display_name)
```

### Method 2: Local Execution (No Kubernetes Required)

This runs the pipeline locally using the SubprocessRunner.

```bash
python3 test_display_name_local.py
```

**Note:** Local execution doesn't create Kubernetes pods, but it verifies:
- The pipeline compiles correctly
- Dependencies work with display_name
- The pipeline executes successfully

### Method 3: Deploy to KFP Cluster (Full Test)

This method actually creates Kubernetes pods so you can verify pod names.

#### Step 1: Set up a local Kind cluster (if needed)

```bash
# From the backend directory
make -C backend kind-cluster-agnostic
```

#### Step 2: Compile and upload the pipeline

```bash
# Compile the pipeline
python3 test_display_name_feature.py

# Upload to KFP (adjust host/namespace as needed)
kfp pipeline upload \
  --host http://localhost:8080 \
  --pipeline-name display-name-test \
  display_name_test_pipeline.yaml
```

#### Step 3: Create a run

```bash
kfp run submit \
  --host http://localhost:8080 \
  --experiment-name default \
  --pipeline-name display-name-test \
  --run-name test-display-name-run
```

#### Step 4: Check pod names

```bash
# Get the workflow name
kubectl get workflows -n kubeflow

# Get pods for the workflow (replace WORKFLOW_NAME)
kubectl get pods -n kubeflow | grep WORKFLOW_NAME

# Inspect a specific pod name
kubectl describe pod <pod-name> -n kubeflow
```

**Expected Pod Names:**
- Should contain `data-producer` (from display_name "Data Producer")
- Should contain `data-consumer` (from display_name "Data Consumer")
- Format: `{workflow-name}-{task-key}-{hash}`

### Method 4: Python API Test

Create a simple Python script to test programmatically:

```python
from kfp import dsl
from kfp import compiler

@dsl.component
def my_task(text: str) -> str:
    return text

@dsl.pipeline(name='test-pipeline')
def test_pipeline():
    task = my_task(text='test').set_display_name('My Custom Task')
    return task

# Compile
compiler.Compiler().compile(
    pipeline_func=test_pipeline,
    package_path='test.yaml'
)

# Inspect
import yaml
with open('test.yaml') as f:
    spec = yaml.safe_load(f)
    tasks = spec['pipelineSpec']['root']['dag']['tasks']
    print("Task keys:", list(tasks.keys()))
    # Should show: ['my-custom-task']
```

## Verification Checklist

- [ ] Pipeline compiles without errors
- [ ] DAG task keys use sanitized display_name (e.g., "My Task" → "my-task")
- [ ] Tasks without display_name use default behavior
- [ ] Duplicate display_names get uniqueness suffixes
- [ ] Dependencies reference correct task keys
- [ ] Pod names (in cluster) contain the display_name-based keys

## Troubleshooting

### Issue: Task key doesn't match display_name

**Check:**
1. Is the task a container task? (Only container tasks use display_name for pod names)
2. Is display_name set before compilation?
3. Check the compiled YAML: `python3 test_display_name_inspect.py <yaml-file>`

### Issue: Dependencies not working

**Check:**
1. Verify dependencies use DAG keys, not internal names
2. Check the compiled YAML for `dependentTasks` field
3. Ensure both tasks are in the same DAG level

### Issue: Pod names don't match

**Check:**
1. Verify you're looking at the correct workflow/pods
2. Pod names include workflow name and hash: `{workflow}-{task-key}-{hash}`
3. Use `kubectl get pods -n kubeflow --show-labels` to see workflow labels

## Advanced Testing

### Test with loops:

```python
@dsl.pipeline(name='loop-test')
def loop_test():
    with dsl.ParallelFor(items=['a', 'b', 'c']) as item:
        task = my_component(text=item).set_display_name('Loop Task')
    return task
```

### Test with long names:

```python
task = my_component(text='test').set_display_name('A' * 100)
# Should be truncated to ~15 characters
```

### Test with special characters:

```python
task = my_component(text='test').set_display_name('My Task @#$%')
# Should be sanitized to: my-task
```

