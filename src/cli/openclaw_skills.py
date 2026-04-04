import os
import sys
import json
import argparse

# Set PYTHONPATH
sys.path.append(os.getcwd())

from src.agents.tools.skills_discover import SkillDiscoveryEngine
from src.agents.tools.skills_generate import SkillGeneratorEngine
from src.agents.skills.skill_sandbox_test import SkillSandboxTester

def main():
    parser = argparse.ArgumentParser(description="OpenClaw AutoSkills CLI (Phase 2 - Task 2.1/4.2)")
    subparsers = parser.add_subparsers(dest="command", help="Skills commands", required=True)

    # 1. Discover
    discover_parser = subparsers.add_parser("discover", help="Search for skills locally and in ClawHub")
    discover_parser.add_argument("intent", help="The capability you are looking for (e.g. 'browser automation')")

    # 2. Generate
    generate_parser = subparsers.add_parser("generate", help="Dynamically create a new skill package")
    generate_parser.add_argument("intent", help="The intent for the new skill")
    generate_parser.add_argument("--reqs", help="Extra requirements for the code generator", default="")

    # 3. Test
    test_parser = subparsers.add_parser("test", help="Run a skill in the sandbox to verify permissions")
    test_parser.add_argument("path", help="Path to the skill directory")

    args = parser.parse_args()

    if args.command == "discover":
        engine = SkillDiscoveryEngine()
        result = engine.discover(args.intent)
        print(f"\n[Searching for '{args.intent}'...]")
        print(f"Hits: {result['total_count']}")
        for c in result["candidates"]:
            risk_tag = f"[Risk {c['risk_level']}]"
            print(f"- {c['name']:30} {risk_tag:10} Source: {c['source']:10}")
            print(f"  {c['description']}")
            print(f"  Permissions: {list(c.get('permissions', {}).keys())}")
            print("")

    elif args.command == "generate":
        gen = SkillGeneratorEngine()
        print(f"\n[Generating skill package for: '{args.intent}'...]")
        result = gen.generate_skill_package(args.intent, args.reqs)
        if result["success"]:
            print(f"SUCCESS: New skill created at: {result['path']}")
            print(f"Suggested Risk Level: {result['manifest']['risk_level']}")
            print("Next step: run 'openclaw python src/cli/openclaw_skills.py test [path]' to verify.")
        else:
            print(f"FAILED: {result['error']}")

    elif args.command == "test":
        tester = SkillSandboxTester()
        print(f"\n[Validating skill at {args.path} in Sandbox...]")
        result = tester.validate_full_skill(args.path)
        if result["success"]:
            print("STATUS: ALL TESTS PASSED.")
            print(f"Manifest: VALIDATED.")
            for r in result.get("reports", []):
                print(f"  - [{r['id']}]: PASS ({r['report']['audit_log']})")
        else:
            print(f"FAILED: {result.get('error', 'Test failure')}")
            for r in result.get("reports", []):
                if not r['report']['success']:
                    print(f"  - [{r['id']}]: FAIL ({r['report']['error']})")

if __name__ == "__main__":
    main()
