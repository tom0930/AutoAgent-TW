import os
import sys
import json
import argparse

# Set PYTHONPATH
sys.path.append(os.getcwd())

from src.agents.tools.skills_discover import SkillDiscoveryEngine
from src.agents.tools.skills_generate import SkillGeneratorEngine
from src.agents.skills.skill_sandbox_test import SkillSandboxTester
from src.agents.skills.skill_metrics import SkillMetricsManager
from src.cron.skill_evolution import SkillEvolutionEngine
from src.agents.skills.skill_rollback import SkillRollbackManager

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

    # 4. Health
    health_parser = subparsers.add_parser("health", help="Check skill health metrics (success rate, latency)")
    health_parser.add_argument("name", help="Name of the skill")

    # 5. Evolve
    evolve_parser = subparsers.add_parser("evolve", help="Run the evolution cycle for all skills")

    # 6. Rollback
    rollback_parser = subparsers.add_parser("rollback", help="Restore a skill to an earlier version")
    rollback_parser.add_argument("name", help="Name of the skill")

    # 7. List
    list_parser = subparsers.add_parser("list", help="List all installed skills with health status")

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

    elif args.command == "health":
        mgr = SkillMetricsManager()
        summary = mgr.get_health_summary(args.name)
        print(f"\n[Health Summary for '{args.name}']")
        if summary.get("status") == "unknown":
            print(f"Status: {summary['message']}")
        else:
            print(f"Status: {summary['status'].upper()}")
            print(f"Success Rate: {summary['success_rate']}")
            print(f"Avg Latency: {summary['avg_latency']}")
            print(f"Total Runs: {summary['total_runs']}")
            print(f"Suggestion: {summary['suggestion']}")

    elif args.command == "evolve":
        engine = SkillEvolutionEngine()
        print("\n[Running Evolution Cycle...]")
        reports = engine.run_evolution_cycle()
        if not reports:
            print("No skills required evolution at this time.")
        for r in reports:
            print(f"- Skill '{r['skill']}': Old SR {r['old_success_rate']} -> Evolution {r['evolution_result']}")

    elif args.command == "rollback":
        mgr = SkillRollbackManager()
        success, msg = mgr.rollback(args.name)
        if success:
            print(f"\n✅ {msg}")
        else:
            print(f"\n❌ {msg}")

    elif args.command == "list":
        # Scanning .agents/skills
        skills_dir = ".agents/skills"
        metrics_mgr = SkillMetricsManager()
        print(f"\n[Installed AutoSkills List]")
        if not os.path.exists(skills_dir):
            print("No skills folder found.")
        else:
            for skill_name in os.listdir(skills_dir):
                skill_path = os.path.join(skills_dir, skill_name)
                if os.path.isdir(skill_path):
                    health = metrics_mgr.get_health_summary(skill_name)
                    status_flag = "[HEALTHY]" if health.get("status") == "healthy" else "[WARNING]" if health.get("status") == "warning" else "[UNKNOWN]"
                    print(f"- {skill_name:25} {status_flag:12} SR: {health.get('success_rate', 'N/A')}")

if __name__ == "__main__":
    main()
