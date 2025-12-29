"""
Deployment Verification Script
Checks if all required files are present and valid before deployment
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) if exists else 0

    status = "[OK]" if exists else ("[FAIL]" if required else "[SKIP]")
    size_str = f"({size:,} bytes)" if exists else ""

    print(f"{status} {filepath} {size_str}")

    return exists if required else True


def verify_deployment_files():
    """Verify all deployment files are present"""
    print("=" * 70)
    print("DEPLOYMENT VERIFICATION")
    print("=" * 70)

    all_good = True

    print("\n[REQUIRED FILES]")
    print("-" * 70)

    # Core application files
    required_files = [
        "app.py",
        "model.py",
        "preprocessing.py",
        "requirements.txt",
        "Dockerfile",
        "trained_model.pth",
    ]

    for file in required_files:
        if not check_file_exists(file, required=True):
            all_good = False

    print("\n[DOCUMENTATION FILES]")
    print("-" * 70)

    # Documentation files (optional but recommended)
    doc_files = [
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        "SPACE_README.md",
    ]

    for file in doc_files:
        check_file_exists(file, required=False)

    print("\n[TEST FILES]")
    print("-" * 70)

    # Test files (optional)
    test_files = [
        "test_api.py",
        ".gitignore",
    ]

    for file in test_files:
        check_file_exists(file, required=False)

    # Check model file size
    print("\n[MODEL VALIDATION]")
    print("-" * 70)

    model_path = "trained_model.pth"
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        expected_size = 489131  # bytes

        if abs(size - expected_size) < 10000:  # Allow 10KB difference
            print(f"[OK] Model size is correct: {size:,} bytes")
        else:
            print(f"[WARN] Model size differs from expected:")
            print(f"   Expected: ~{expected_size:,} bytes")
            print(f"   Actual: {size:,} bytes")
            print(f"   This may be okay if you retrained the model")
    else:
        print("[FAIL] Model file not found!")
        all_good = False

    # Check requirements.txt content
    print("\n[DEPENDENCIES CHECK]")
    print("-" * 70)

    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
            required_deps = [
                "fastapi",
                "uvicorn",
                "torch",
                "mediapipe",
                "opencv-python",
                "numpy"
            ]

            print("Checking for required dependencies:")
            for dep in required_deps:
                if dep in content.lower():
                    print(f"  [OK] {dep}")
                else:
                    print(f"  [FAIL] {dep} - MISSING!")
                    all_good = False
    else:
        print("[FAIL] requirements.txt not found!")
        all_good = False

    # Check Dockerfile
    print("\n[DOCKERFILE CHECK]")
    print("-" * 70)

    if os.path.exists("Dockerfile"):
        with open("Dockerfile", "r") as f:
            content = f.read()

            checks = {
                "Python base image": "FROM python:",
                "Port 7860 exposed": "EXPOSE 7860",
                "Uvicorn command": "uvicorn",
                "Requirements install": "pip install",
            }

            for check_name, check_str in checks.items():
                if check_str in content:
                    print(f"  [OK] {check_name}")
                else:
                    print(f"  [FAIL] {check_name} - MISSING!")
                    all_good = False
    else:
        print("[FAIL] Dockerfile not found!")
        all_good = False

    # Final summary
    print("\n" + "=" * 70)
    if all_good:
        print("[SUCCESS] ALL CHECKS PASSED!")
        print("\nYour deployment files are ready. Next steps:")
        print("1. Review DEPLOYMENT_GUIDE.md")
        print("2. Create Hugging Face Space")
        print("3. Upload files or push via git")
        print("4. Wait for build to complete")
        print("5. Test your API")
    else:
        print("[ERROR] SOME CHECKS FAILED!")
        print("\nPlease fix the issues above before deploying.")
        print("Refer to README.md for more information.")

    print("=" * 70)

    return all_good


def print_deployment_info():
    """Print helpful deployment information"""
    print("\n" + "=" * 70)
    print("QUICK DEPLOYMENT GUIDE")
    print("=" * 70)

    print("""
Hugging Face Spaces (Recommended):

1. Create account: https://huggingface.co/join
2. Create Space: https://huggingface.co/spaces
   - SDK: Docker
   - Hardware: CPU basic (free)

3. Deploy via Git:
   git init
   git add .
   git commit -m "Deploy MSL API"
   git remote add space https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE
   git push space main

4. Or upload files via web interface

5. Wait 5-10 minutes for build

6. Your API: https://YOUR-USERNAME-YOUR-SPACE.hf.space

Full guide: See DEPLOYMENT_GUIDE.md
""")


if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Run verification
    success = verify_deployment_files()

    # Print deployment info
    print_deployment_info()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
