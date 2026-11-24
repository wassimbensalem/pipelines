#!/usr/bin/env python3
"""Test display_name with ParallelFor loops."""

from kfp import dsl
from kfp import compiler


@dsl.component
def gitlab_get_device_configs(
    gitlab_config: str,
    device: dict,
    execution_config: str,
    wandb_config: str,
) -> str:
    """Mock component for testing."""
    return f"config-for-{device.get('device_name', 'unknown')}"


@dsl.component
def gitlab_config_filter(config: str) -> list:
    """Mock component that returns a list of devices."""
    return [
        {'device_name': 'device1', 'type': 'sensor'},
        {'device_name': 'device2', 'type': 'actuator'},
    ]


@dsl.pipeline(name='loop-display-name-test')
def loop_display_name_test():
    """Test pipeline with display_name in ParallelFor loop."""
    
    # Mock the gitlab_config_filter_op
    gitlab_config_filter_op = gitlab_config_filter(config='test')
    
    # Test the loop with display_name
    with dsl.ParallelFor(
        items=gitlab_config_filter_op.output,
        parallelism=2
    ) as device:
        # This should work: use device.device_name (attribute access)
        fetch_configs_op = gitlab_get_device_configs(
            gitlab_config='config',
            device=device,  # device is a LoopParameterArgument
            execution_config='exec',
            wandb_config='wandb',
        )
        
        # Set display name using attribute access (correct way)
        fetch_configs_op.set_display_name(
            f"fetch-configs-{device.device_name}"  # Use .device_name, not ['device_name']
        )
        
        fetch_configs_op.after(gitlab_config_filter_op)


if __name__ == '__main__':
    print("Compiling pipeline with display_name in loop...")
    try:
        compiler.Compiler().compile(
            pipeline_func=loop_display_name_test,
            package_path='loop_display_name_test.yaml'
        )
        print("✓ Pipeline compiled successfully!")
        print("\nTo inspect:")
        print("  python3 test_display_name_inspect.py loop_display_name_test.yaml")
    except Exception as e:
        print(f"✗ Compilation failed: {e}")
        import traceback
        traceback.print_exc()

