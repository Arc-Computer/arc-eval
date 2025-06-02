# 🚀 Agent-as-a-Judge Performance Optimization Plan

## 🎯 **Objective**
Reduce Agent-as-a-Judge evaluation time from **82 seconds** to **10-15 seconds** for 5 scenarios by defaulting to faster models and adding OpenRouter support.

## ⚡ **Current Performance Issues**
- **Current**: 16.4 seconds per scenario (unacceptable)
- **Target**: 2-3 seconds per scenario (excellent UX)
- **Root Cause**: Using slow premium models (Claude Sonnet 4) by default
- **Impact**: Poor user experience, slow iteration cycles, high costs

## 🔧 **Solution: Smart Model Defaults**

### **New Default Models (Fast & Cost-Effective)**
1. **Primary**: `gpt-4o-mini` (OpenAI)
   - Speed: ~2 seconds per scenario
   - Cost: ~$0.001 per scenario
   - Accuracy: 85-90%

2. **Secondary**: `claude-3-5-haiku-latest` (Anthropic)
   - Speed: ~2-3 seconds per scenario  
   - Cost: ~$0.001 per scenario
   - Accuracy: 85-90%

### **Smart Model Selection Logic**
```python
# Default behavior (prioritize speed)
if scenario_count <= 10:
    model = "gpt-4o-mini"  # Fastest for small batches
elif scenario_count <= 50:
    model = "claude-3-5-haiku-latest"  # Good balance
else:
    model = "claude-3-5-sonnet-latest"  # Accuracy for large batches

# User can override for accuracy
if high_accuracy_mode:
    model = "claude-3-5-sonnet-latest"
```

## 🌐 **OpenRouter Integration**

### **Why OpenRouter?**
- **Unified API**: Access 100+ models through single endpoint
- **Automatic Fallbacks**: Built-in redundancy and uptime optimization
- **Cost Optimization**: Automatic routing to most cost-effective providers
- **Model Diversity**: Access to latest models from multiple providers

### **Implementation Plan**
1. **Add OpenRouter Provider**
   ```python
   # New provider class
   class OpenRouterProvider(BaseProvider):
       base_url = "https://openrouter.ai/api/v1"
       # Compatible with OpenAI SDK
   ```

2. **Model Mapping**
   ```python
   OPENROUTER_MODELS = {
       "gpt-4o-mini": "openai/gpt-4o-mini",
       "claude-3-5-haiku": "anthropic/claude-3-5-haiku",
       "claude-3-5-sonnet": "anthropic/claude-3-5-sonnet",
       "gemini-1.5-flash": "google/gemini-1.5-flash"
   }
   ```

3. **Configuration**
   ```bash
   # Environment variable
   export OPENROUTER_API_KEY="your-key"
   
   # CLI usage
   arc-eval compliance --provider openrouter --model gpt-4o-mini
   ```

## 📋 **Implementation Tasks**

### **Phase 1: Model Defaults (High Priority)**
- [ ] Update `api_manager.py` to default to `gpt-4o-mini`
- [ ] Add fallback to `claude-3-5-haiku-latest`
- [ ] Update model selection logic in `dual_track_evaluator.py`
- [ ] Add `--high-accuracy` flag for premium models
- [ ] Update documentation with new defaults

### **Phase 2: OpenRouter Integration (Medium Priority)**
- [ ] Create `OpenRouterProvider` class
- [ ] Add OpenRouter model mappings
- [ ] Implement authentication and headers
- [ ] Add provider selection logic
- [ ] Add OpenRouter to CLI options
- [ ] Update configuration documentation

### **Phase 3: Performance Validation (High Priority)**
- [ ] Benchmark new default models
- [ ] Validate 2-3 second per scenario target
- [ ] Test accuracy vs speed trade-offs
- [ ] Update performance analytics
- [ ] Document performance improvements

## 🎯 **Expected Outcomes**

### **Performance Improvements**
- **Speed**: 5-8x faster (82s → 10-15s for 5 scenarios)
- **Cost**: 5x cheaper ($0.027 → $0.005 for 5 scenarios)
- **UX**: Excellent real-time feedback for developers

### **User Experience**
```bash
# Fast by default (new behavior)
arc-eval compliance --domain finance --input data.json
# ⚡ Completes in 10-15 seconds

# High accuracy when needed
arc-eval compliance --domain finance --input data.json --high-accuracy
# 🎯 Uses premium models, takes 60-90 seconds

# OpenRouter for redundancy
arc-eval compliance --domain finance --input data.json --provider openrouter
# 🌐 Automatic fallbacks and cost optimization
```

## 📊 **Success Metrics**
- **Target Speed**: ≤3 seconds per scenario
- **Target Accuracy**: ≥85% (vs current 95%)
- **Cost Reduction**: ≥80% savings
- **User Satisfaction**: Fast feedback enables rapid iteration

## 🚀 **Next Steps**
1. Create new branch: `feature/performance-optimization`
2. Implement Phase 1 (model defaults) first
3. Test and validate performance improvements
4. Add OpenRouter integration (Phase 2)
5. Update documentation and examples
