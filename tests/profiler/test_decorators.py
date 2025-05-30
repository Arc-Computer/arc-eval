from agent_eval.profiler.decorators import track_evaluation
from agent_eval.analysis.pattern_learner import PatternLearner


class DummyRecorder:
    @track_evaluation
    def record(self, agent_id, domain, evaluation_results):
        # Return a marker
        return {"status": "ok", "data": evaluation_results}


def test_track_evaluation_decorator(monkeypatch):
    # Capture calls to PatternLearner.learn_from_debug_session
    calls = []

    def fake_learn(self, debug_results):
        calls.append(debug_results)

    monkeypatch.setattr(PatternLearner, "learn_from_debug_session", fake_learn)

    dummy = DummyRecorder()
    test_data = [{"passed": False}]
    result = dummy.record("agent-1", "finance", test_data)
    assert result["status"] == "ok"
    assert result["data"] == test_data
    # Ensure learner was invoked with same data
    assert calls and calls[0] == test_data