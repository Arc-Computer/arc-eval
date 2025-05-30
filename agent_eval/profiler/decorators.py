"""
Simple evaluation tracking decorator for pattern learning integration.
"""

from functools import wraps

from agent_eval.analysis.pattern_learner import PatternLearner


def track_evaluation(fn):
    """
    Decorator to hook pattern learning after an evaluation or debug session.
    Expects the decorated function to accept (agent_id, domain, evaluation_results).
    """
    @wraps(fn)
    def wrapper(self, agent_id, domain, evaluation_results, *args, **kwargs):
        result = fn(self, agent_id, domain, evaluation_results, *args, **kwargs)
        try:
            learner = PatternLearner()
            learner.learn_from_debug_session(evaluation_results)
            
            # Get learning metrics and generated fixes
            metrics = learner.get_learning_metrics()
            fixes = learner.get_generated_fixes()
            
            # Display learning progress if anything was learned
            if metrics.get("patterns_learned", 0) > 0:
                print(f"\n🧠 [Pattern Learning] Captured {metrics['patterns_learned']} failure patterns")
                if metrics.get("scenarios_generated", 0) > 0:
                    print(f"   ✨ Generated {metrics['scenarios_generated']} new test scenarios")
                if metrics.get("fixes_generated", 0) > 0:
                    print(f"   🔧 Generated {metrics['fixes_generated']} actionable fixes")
                    
                    # Display fixes by domain
                    for domain, domain_fixes in fixes.items():
                        if domain_fixes:
                            print(f"\n   📋 {domain.upper()} Fixes:")
                            for fix in domain_fixes[:2]:  # Show first 2 fixes per domain
                                print(f"   {fix}")
                            if len(domain_fixes) > 2:
                                print(f"   ... and {len(domain_fixes) - 2} more fixes")
        except Exception as e:
            # Fail silently on learning errors to not break main flow
            print(f"[WARN] Pattern learning failed: {e}")
        return result

    return wrapper