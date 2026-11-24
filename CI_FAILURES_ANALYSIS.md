# CI Test Failures Analysis and Fixes

## Summary

This document analyzes potential CI test failures for the `display_name` feature branch and provides recommendations for fixes.

## Changes Made

The branch adds support for using `display_name` as the DAG task key (which flows through to Kubernetes pod names) for container tasks. The changes affect:

1. `sdk/python/kfp/dsl/pipeline_task.py` - Added `set_display_name()` method
2. `sdk/python/kfp/compiler/pipeline_spec_builder.py` - Updated to use display_name for DAG task keys
3. `sdk/python/kfp/compiler/compiler_test.py` - Added comprehensive tests

## Potential CI Failures

### 1. Backend Compiler Tests (Most Likely)

**Workflow**: `.github/workflows/compiler-tests.yml`

**Issue**: The backend compiler tests compile pipelines and compare them to golden files in `test_data/compiled-workflows/`. If any existing test pipelines use display_name or if the changes affect how tasks are named, the golden files may need updating.

**How to Check**:
```bash
# Run compiler tests locally
cd backend/test/compiler
ginkgo -v ./backend/test/compiler -- -updateCompiledFiles=true
```

**Fix**: If tests fail due to golden file mismatches:
1. Review the diff to ensure the changes are expected
2. Update golden files with: `ginkgo -v ./backend/test/compiler -- -updateCompiledFiles=true`
3. Commit the updated golden files

### 2. SDK Unit Tests

**Workflow**: `.github/workflows/kfp-sdk-unit-tests.yml`

**Status**: ✅ All display_name tests pass locally

**Verification**:
```bash
pytest -v sdk/python/kfp/compiler/compiler_test.py -k "test_set_display_name"
```

### 3. Formatting/Linting Checks

**Workflows**: 
- `.github/workflows/sdk-yapf.yml`
- `.github/workflows/sdk-isort.yml`
- `.github/workflows/sdk-docformatter.yml`

**Status**: ✅ All checks pass locally

**Verification**:
```bash
# YAPF
yapf --recursive --diff sdk/python/

# isort
isort --check --profile google sdk/python/

# docformatter
docformatter --check --recursive sdk/python/ --exclude "compiler_test.py"
```

### 4. Backend Unit Tests

**Workflow**: `.github/workflows/presubmit-backend.yml`

**Issue**: Unlikely to be affected since changes are in Python SDK, but worth checking if any Go code references task naming.

## Recommended Actions

### Step 1: Check CI Status
1. Push your branch and check which specific tests are failing in GitHub Actions
2. Review the error messages and logs

### Step 2: Update Golden Files (if needed)
If backend compiler tests fail:

```bash
# Make sure you have ginkgo installed
make ginkgo
export PATH="$PWD/bin:$PATH"

# Run compiler tests with update flag
cd backend/test/compiler
ginkgo -v ./backend/test/compiler -- -updateCompiledFiles=true
```

### Step 3: Verify All Tests Pass
```bash
# SDK tests
pytest -v sdk/python/kfp/compiler/compiler_test.py

# Formatting
./test/presubmit-yapf-sdk.sh
./test/presubmit-isort-sdk.sh
./test/presubmit-docformatter-sdk.sh
```

## Common Issues and Solutions

### Issue: Golden files don't match
**Solution**: Update golden files using the `-updateCompiledFiles=true` flag. Review diffs carefully to ensure changes are expected.

### Issue: Task dependencies not resolving correctly
**Solution**: Verify that `internal_name_to_dag_key` mapping is correctly used in all places where task names are referenced (producer_task, dependent_tasks, etc.)

### Issue: Tests failing for tasks without display_name
**Solution**: Ensure backward compatibility - tasks without display_name should use the existing behavior (sanitized task name).

## Files to Review

1. **Backend compiler test failures**: Check `backend/test/compiler/` for any test failures
2. **Golden file diffs**: Review changes in `test_data/compiled-workflows/` if updated
3. **Task name mapping**: Verify `internal_name_to_dag_key` is used consistently in:
   - `build_task_spec_for_task()` - producer_task references
   - `build_task_spec_for_group()` - producer_task references  
   - `build_spec_by_group()` - dependent_tasks and DAG task keys

## Next Steps

1. Push branch and identify specific failing tests
2. Update this document with actual failure details
3. Apply fixes based on the specific failures
4. Re-run CI to verify fixes
