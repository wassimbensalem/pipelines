# Quick Test Guide for display_name Feature

## Important: Install SDK in Development Mode

**You must install the SDK in editable mode for your changes to take effect:**

```bash
cd /Users/wassimbensalem/Desktop/Projects-Extra/OpenSource/pipelines

# Activate your virtual environment
source .venv/bin/activate  # or your venv path

# Install SDK in editable mode
cd sdk/python
pip install -e . --config-settings editable_mode=strict

# Verify installation
python3 -c "import kfp; print(kfp.__file__)"
# Should point to your local sdk/python/kfp directory
```

## Quick Test Steps

### 1. Compile and Inspect (Fastest)

```bash
cd /Users/wassimbensalem/Desktop/Projects-Extra/OpenSource/pipelines

# Run test script
python3 test_display_name_feature.py

# Inspect results
python3 test_display_name_inspect.py display_name_test_pipeline.yaml
```

**Expected Output (with your changes):**
```
Task Key: data-producer    ← Should use display_name!
  Display Name: Data Producer

Task Key: data-consumer    ← Should use display_name!
  Display Name: Data Consumer
  Dependencies: data-producer
```

**If you see "producer" and "consumer" instead, the SDK isn't using your local changes.**

### 2. Test on Real Cluster

```bash
# 1. Set up Kind cluster (if needed)
make -C backend kind-cluster-agnostic

# 2. Compile pipeline
python3 test_display_name_feature.py

# 3. Upload to KFP
kfp pipeline upload \
  --host http://localhost:8080 \
  display_name_test_pipeline.yaml

# 4. Create a run
kfp run submit \
  --host http://localhost:8080 \
  --experiment-name default \
  --pipeline-name display-name-test-pipeline \
  --run-name test-run

# 5. Check pod names
kubectl get pods -n kubeflow | grep display-name-test

# Pod names should contain "data-producer" and "data-consumer"
```

### 3. Verify Implementation is Active

Add a debug print to verify your code is running:

```python
# In pipeline_spec_builder.py, around line 1404, add:
if subgroup._task_spec.display_name:
    print(f"DEBUG: Using display_name '{subgroup._task_spec.display_name}' for task '{subgroup.name}'")
    task_dag_key = utils.sanitize_task_name(
        subgroup._task_spec.display_name)
    print(f"DEBUG: Generated DAG key: '{task_dag_key}'")
```

Then run the test and check for DEBUG output.

## Troubleshooting

### Issue: Changes not taking effect

1. **Verify editable install:**
   ```bash
   python3 -c "import kfp.compiler.pipeline_spec_builder as psb; print(psb.__file__)"
   ```
   Should point to your local file.

2. **Reinstall in editable mode:**
   ```bash
   pip uninstall kfp
   cd sdk/python
   pip install -e . --config-settings editable_mode=strict
   ```

3. **Check Python path:**
   ```bash
   python3 -c "import sys; print('\n'.join(sys.path))"
   ```
   Your local sdk/python should be in the path.

### Issue: Task keys still wrong

1. Check that `subgroup.container_spec is not None`
2. Check that `subgroup._task_spec.display_name` is set
3. Add print statements to debug the flow

### Issue: Import errors

Make sure you're in the right directory and have activated your venv:
```bash
cd /Users/wassimbensalem/Desktop/Projects-Extra/OpenSource/pipelines
source .venv/bin/activate  # or your venv
```

