# Fix for display_name in Nested Loops

## Problem

When using `set_display_name()` inside a `ParallelFor` loop with loop variables, you get:

```python
TypeError: 'LoopParameterArgument' object is not subscriptable
```

**Your code:**
```python
fetch_configs_op.set_display_name(f"fetch-configs-{device['device_name']}")
```

## Solution

### 1. Use Attribute Access (Not Subscript)

**❌ Wrong:**
```python
fetch_configs_op.set_display_name(f"fetch-configs-{device['device_name']}")
# TypeError: 'LoopParameterArgument' object is not subscriptable
```

**✅ Correct:**
```python
fetch_configs_op.set_display_name(f"fetch-configs-{device.device_name}")
# Works! Use attribute access (device.device_name)
```

### 2. How It Works Now

The updated `set_display_name()` method now:

1. **Detects LoopArgumentVariable objects** in f-strings
2. **Extracts the subvar name** (e.g., `device_name`) from the placeholder
3. **Replaces the placeholder** with the subvar name in the display_name
4. **Result**: `"fetch-configs-device_name"` (sanitized to `fetch-configs-device-name`)

### 3. Updated Code

Your fixed code should be:

```python
with dsl.ParallelFor(
    items=gitlab_config_filter_op.output,
    parallelism=max_replicas
) as device:
    # Step 1: Fetch GitLab configurations
    fetch_configs_op = gitlab_get_device_configs(
        gitlab_config=gitlab_config,
        device=device,  # device is LoopParameterArgument
        execution_config=execution_params,
        wandb_config=wandb_config,
    )
    set_resource_limits(fetch_configs_op, "200m", "400m", "256Mi", "512Mi")
    kubernetes.use_secret_as_env(
        fetch_configs_op,
        secret_name="gitlab-devices-access-key",
        secret_key_to_env={"token": "GITLAB_DEVICES_KEY"},
    )
    fetch_configs_op.set_caching_options(False)
    fetch_configs_op.after(gitlab_config_filter_op)
    fetch_configs_op.set_retry(3, backoff_duration="60s")
    
    # ✅ Fixed: Use attribute access
    fetch_configs_op.set_display_name(f"fetch-configs-{device.device_name}")
```

### 4. Important Notes

- **All iterations share the same base DAG key**: Since display_name is evaluated at compile time, all loop iterations will have the same base task key (e.g., `fetch-configs-device-name`)
- **Argo adds iteration indices**: Pod names will be unique because Argo automatically adds iteration indices: `{workflow}-fetch-configs-device-name-{iteration}-{hash}`
- **Runtime values not in DAG key**: The actual `device_name` values (like "device1", "device2") are resolved at runtime, so they can't be part of the compile-time DAG task key
- **Works with nested loops**: This fix works for nested `ParallelFor` loops as well

### 5. Expected Pod Names

For a loop with 3 devices, you'll get pod names like:
- `{workflow-name}-fetch-configs-device-name-0-{hash}` (iteration 0)
- `{workflow-name}-fetch-configs-device-name-1-{hash}` (iteration 1)
- `{workflow-name}-fetch-configs-device-name-2-{hash}` (iteration 2)

The base name `fetch-configs-device-name` comes from your display_name, and Argo adds the iteration index to make them unique.

### 6. Testing

To test this fix:

1. **Install SDK in editable mode** (if not already done):
   ```bash
   cd sdk/python
   pip install -e . --config-settings editable_mode=strict
   ```

2. **Update your code** to use `device.device_name` instead of `device['device_name']`

3. **Compile and test**:
   ```bash
   python pipeline.py
   ```

The error should be resolved, and your pipeline should compile successfully!

