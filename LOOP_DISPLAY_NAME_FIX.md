# Fix for display_name in ParallelFor Loops

## Problem

When using `set_display_name()` inside a `ParallelFor` loop with loop variables, you get:

```
TypeError: 'LoopParameterArgument' object is not subscriptable
```

This happens when you try to use dictionary-style access: `device['device_name']`

## Solution

### 1. Use Attribute Access, Not Subscript

**Wrong:**
```python
fetch_configs_op.set_display_name(f"fetch-configs-{device['device_name']}")
# ❌ TypeError: 'LoopParameterArgument' object is not subscriptable
```

**Correct:**
```python
fetch_configs_op.set_display_name(f"fetch-configs-{device.device_name}")
# ✅ Works! Use attribute access (device.device_name)
```

### 2. How It Works

When you use `device.device_name` in an f-string:
- `device.device_name` is a `LoopArgumentVariable` object
- Python converts it to a string placeholder: `{{channel:task=...;name=...;type=...;}}`
- Our code extracts this placeholder and replaces it with the subvar name (`device_name`)
- Final display_name becomes: `"fetch-configs-device_name"`

### 3. Important Notes

- **All iterations share the same DAG task key**: Since display_name is evaluated at compile time, all loop iterations will have the same base task key (e.g., `fetch-configs-device_name`)
- **Argo adds iteration indices**: Pod names will be unique because Argo adds iteration indices: `{workflow}-fetch-configs-device_name-{iteration}-{hash}`
- **Runtime values not available**: The actual `device_name` values (like "device1", "device2") are not available at compile time, so they can't be in the DAG task key

### 4. Example

```python
with dsl.ParallelFor(
    items=gitlab_config_filter_op.output,
    parallelism=max_replicas
) as device:
    fetch_configs_op = gitlab_get_device_configs(
        gitlab_config=gitlab_config,
        device=device,  # device is LoopParameterArgument
        execution_config=execution_params,
        wandb_config=wandb_config,
    )
    
    # ✅ Correct: Use attribute access
    fetch_configs_op.set_display_name(f"fetch-configs-{device.device_name}")
    
    # ❌ Wrong: Don't use subscript
    # fetch_configs_op.set_display_name(f"fetch-configs-{device['device_name']}")
```

### 5. Result

- **DAG task key**: `fetch-configs-device_name` (same for all iterations)
- **Pod names**: 
  - `{workflow}-fetch-configs-device_name-0-{hash}` (iteration 0)
  - `{workflow}-fetch-configs-device_name-1-{hash}` (iteration 1)
  - etc.

The pod names will be unique per iteration due to Argo's iteration indexing, even though the base task key is the same.

