"""
MineRL Setup Test
=================
Tests if MineRL is properly installed and working.

Run this FIRST before training!
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("📦 Testing imports...")

    required_packages = [
        ('gym', 'gym'),
        ('numpy', 'numpy'),
        ('torch', 'torch'),
        ('PIL', 'Pillow'),
        ('minerl', 'minerl')
    ]

    missing = []

    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} (install: pip install {pip_name})")
            missing.append(pip_name)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False

    print("✅ All packages installed!\n")
    return True


def test_minerl_envs():
    """Test if MineRL environments are available"""
    print("🎮 Testing MineRL environments...")

    try:
        import gym
        import minerl

        # List available environments
        minerl_envs = [env.id for env in gym.envs.registry.all()
                      if 'MineRL' in env.id]

        print(f"\n✅ Found {len(minerl_envs)} MineRL environments:")
        for env_id in minerl_envs[:10]:
            print(f"   - {env_id}")

        if len(minerl_envs) > 10:
            print(f"   ... and {len(minerl_envs) - 10} more")

        return True

    except Exception as e:
        print(f"❌ Error loading MineRL: {e}")
        return False


def test_simple_env():
    """Test creating and running a simple MineRL environment"""
    print("\n🧪 Testing MineRLTreechop-v0 environment...")

    try:
        import gym
        import minerl

        # Create environment
        print("   Creating environment...")
        env = gym.make('MineRLTreechop-v0')

        # Reset
        print("   Resetting environment...")
        obs = env.reset()

        # Check observation
        print(f"\n📊 Observation structure:")
        print(f"   Type: {type(obs)}")
        print(f"   Keys: {obs.keys() if isinstance(obs, dict) else 'N/A'}")

        if 'pov' in obs:
            print(f"   POV shape: {obs['pov'].shape}")
        if 'inventory' in obs:
            print(f"   Inventory keys: {list(obs['inventory'].keys())[:5]}...")

        # Check action space
        print(f"\n🎮 Action space:")
        print(f"   Type: {type(env.action_space)}")
        print(f"   Sample: {env.action_space.sample()}")

        # Take a few steps
        print(f"\n▶️  Taking 5 random steps...")
        for i in range(5):
            action = env.action_space.noop()
            action['forward'] = 1  # Just walk forward

            obs, reward, done, info = env.step(action)
            print(f"   Step {i+1}: reward={reward:.3f}, done={done}")

            if done:
                obs = env.reset()

        env.close()
        print("\n✅ Environment test successful!")
        return True

    except Exception as e:
        print(f"\n❌ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_availability():
    """Test if MineRL dataset is available"""
    print("\n📥 Testing MineRL dataset availability...")

    try:
        import minerl

        # Try to access data
        print("   Checking for human demonstration data...")
        data = minerl.data.make('MineRLTreechop-v0')

        # Get trajectory names
        trajectory_names = data.get_trajectory_names()
        print(f"\n✅ Found {len(trajectory_names)} trajectories!")
        print(f"   Example: {trajectory_names[0] if trajectory_names else 'None'}")

        # Try to load a small sample
        if trajectory_names:
            print("\n   Loading sample data...")
            count = 0
            for obs, action, reward, next_obs, done in data.load_data(
                trajectory_names[0], skip_interval=100
            ):
                count += 1
                if count >= 3:
                    break

            print(f"   ✅ Successfully loaded {count} samples!")

        return True

    except Exception as e:
        print(f"\n⚠️  Dataset not available: {e}")
        print("   This is OK - you can still train without human data!")
        return True  # Not critical


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  MINECRAFT BOT SETUP TEST")
    print("="*60 + "\n")

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: MineRL Environments
    if results[-1][1]:
        results.append(("MineRL Envs", test_minerl_envs()))

    # Test 3: Simple Environment
    if results[-1][1]:
        results.append(("Environment Test", test_simple_env()))

    # Test 4: Dataset (optional)
    results.append(("Dataset", test_data_availability()))

    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_critical_passed = all(passed for name, passed in results[:-1])

    if all_critical_passed:
        print("\n🎉 All critical tests passed! Ready to build Minecraft bot!")
        print("\nNext steps:")
        print("1. Check minecraft-bot/environments/minecraft_env.py")
        print("2. Check minecraft-bot/networks/worker_network.py")
        print("3. Run training: python train_minecraft_bot.py")
    else:
        print("\n❌ Some tests failed. Please fix issues before continuing.")
        print("\nCommon issues:")
        print("- MineRL not installed: pip install minerl")
        print("- Missing dependencies: pip install gym numpy torch pillow")
        print("- Java not installed: sudo apt-get install openjdk-8-jdk")

    print()


if __name__ == "__main__":
    main()
