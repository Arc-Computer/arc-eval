"""
Cost Tracker: API cost calculation and optimization.

Tracks API usage costs and provides optimization suggestions.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CostTracker:
    """Tracks API costs and provides optimization suggestions."""
    
    def __init__(self):
        """Initialize cost tracker with current pricing."""
        # Current API pricing (per 1K tokens) - Updated as of 2024
        self.pricing = {
            'openai': {
                'gpt-4o': {'input': 0.00250, 'output': 0.01000},
                'gpt-4o-mini': {'input': 0.000150, 'output': 0.000600},
                'gpt-4-turbo': {'input': 0.01000, 'output': 0.03000},
                'gpt-3.5-turbo': {'input': 0.000500, 'output': 0.001500},
            },
            'anthropic': {
                'claude-3-5-sonnet-20241022': {'input': 0.003000, 'output': 0.015000},
                'claude-3-5-haiku-20241022': {'input': 0.000250, 'output': 0.001250},
                'claude-3-opus-20240229': {'input': 0.015000, 'output': 0.075000},
            },
            'google': {
                'gemini-1.5-pro': {'input': 0.001250, 'output': 0.005000},
                'gemini-1.5-flash': {'input': 0.000075, 'output': 0.000300},
            },
            'cerebras': {
                'llama-3.3-70b': {'input': 0.000600, 'output': 0.000600},
                'llama-3.1-8b': {'input': 0.000100, 'output': 0.000100},
            }
        }
        
        # Cost optimization thresholds
        self.optimization_thresholds = {
            'high_cost_per_run': 0.10,  # $0.10 per run
            'high_monthly_cost': 100.0,  # $100 per month
            'low_utilization': 0.3,  # 30% utilization
        }
    
    def calculate_cost(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Calculate cost for API usage.
        
        Args:
            provider: API provider (openai, anthropic, etc.)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        provider = provider.lower()
        
        if provider not in self.pricing:
            logger.warning(f"Unknown provider: {provider}")
            return 0.0
        
        if model not in self.pricing[provider]:
            logger.warning(f"Unknown model: {model} for provider: {provider}")
            return 0.0
        
        pricing = self.pricing[provider][model]
        
        # Calculate cost (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000.0) * pricing['input']
        output_cost = (output_tokens / 1000.0) * pricing['output']
        total_cost = input_cost + output_cost
        
        logger.debug(f"Cost calculation: {provider}/{model} - "
                    f"Input: {input_tokens} tokens (${input_cost:.4f}), "
                    f"Output: {output_tokens} tokens (${output_cost:.4f}), "
                    f"Total: ${total_cost:.4f}")
        
        return total_cost
    
    def get_optimization_suggestions(
        self, 
        current_provider: str, 
        current_model: str,
        usage_stats: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """Get cost optimization suggestions.
        
        Args:
            current_provider: Current API provider
            current_model: Current model
            usage_stats: Usage statistics including cost_per_run, monthly_runs, etc.
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        cost_per_run = usage_stats.get('cost_per_run', 0.0)
        monthly_runs = usage_stats.get('monthly_runs', 0)
        monthly_cost = cost_per_run * monthly_runs
        
        # High cost per run optimization
        if cost_per_run > self.optimization_thresholds['high_cost_per_run']:
            cheaper_alternatives = self._find_cheaper_alternatives(
                current_provider, current_model, cost_per_run
            )
            for alt in cheaper_alternatives:
                suggestions.append({
                    'type': 'model_switch',
                    'description': f"Switch to {alt['provider']}/{alt['model']} for {alt['savings']:.0%} cost reduction",
                    'current_cost': f"${cost_per_run:.4f}",
                    'new_cost': f"${alt['estimated_cost']:.4f}",
                    'priority': 'high' if alt['savings'] > 0.5 else 'medium'
                })
        
        # High monthly cost optimization
        if monthly_cost > self.optimization_thresholds['high_monthly_cost']:
            suggestions.append({
                'type': 'usage_optimization',
                'description': f"Monthly cost (${monthly_cost:.2f}) is high. Consider batch processing or caching",
                'current_cost': f"${monthly_cost:.2f}/month",
                'priority': 'high'
            })
        
        # Batch processing suggestions
        if monthly_runs > 100:
            suggestions.append({
                'type': 'batch_processing',
                'description': f"Process {monthly_runs} runs in batches for potential volume discounts",
                'priority': 'medium'
            })
        
        # Token optimization
        avg_tokens = usage_stats.get('avg_tokens_per_run', 0)
        if avg_tokens > 2000:
            suggestions.append({
                'type': 'token_optimization',
                'description': f"Average {avg_tokens} tokens per run is high. Consider prompt optimization",
                'priority': 'medium'
            })
        
        return suggestions
    
    def _find_cheaper_alternatives(
        self, 
        current_provider: str, 
        current_model: str,
        current_cost: float
    ) -> List[Dict[str, any]]:
        """Find cheaper model alternatives."""
        alternatives = []
        
        # Estimate tokens for comparison (rough approximation)
        estimated_tokens = self._estimate_tokens_from_cost(current_provider, current_model, current_cost)
        
        for provider, models in self.pricing.items():
            for model, pricing in models.items():
                if provider == current_provider and model == current_model:
                    continue
                
                # Estimate cost with this alternative
                estimated_cost = self.calculate_cost(
                    provider, model, 
                    estimated_tokens['input'], 
                    estimated_tokens['output']
                )
                
                if estimated_cost < current_cost:
                    savings = (current_cost - estimated_cost) / current_cost
                    alternatives.append({
                        'provider': provider,
                        'model': model,
                        'estimated_cost': estimated_cost,
                        'savings': savings
                    })
        
        # Sort by savings (highest first)
        alternatives.sort(key=lambda x: x['savings'], reverse=True)
        
        return alternatives[:3]  # Top 3 alternatives
    
    def _estimate_tokens_from_cost(
        self, 
        provider: str, 
        model: str, 
        cost: float
    ) -> Dict[str, int]:
        """Estimate token usage from cost (rough approximation)."""
        if provider not in self.pricing or model not in self.pricing[provider]:
            return {'input': 1000, 'output': 500}  # Default estimate
        
        pricing = self.pricing[provider][model]
        
        # Assume 2:1 input:output ratio (common pattern)
        # Solve: cost = (input_tokens/1000) * input_price + (output_tokens/1000) * output_price
        # Where output_tokens = input_tokens / 2
        
        input_price = pricing['input']
        output_price = pricing['output']
        
        # cost = (tokens/1000) * input_price + (tokens/2000) * output_price
        # cost = tokens * (input_price/1000 + output_price/2000)
        combined_price_per_token = input_price / 1000 + output_price / 2000
        
        total_tokens = cost / combined_price_per_token
        input_tokens = int(total_tokens * 2 / 3)  # 2/3 input, 1/3 output
        output_tokens = int(total_tokens / 3)
        
        return {'input': max(input_tokens, 100), 'output': max(output_tokens, 50)}
    
    def get_cost_trends(
        self, 
        cost_history: List[Tuple[datetime, float]]
    ) -> Dict[str, any]:
        """Analyze cost trends over time.
        
        Args:
            cost_history: List of (timestamp, cost) tuples
            
        Returns:
            Trend analysis including direction and rate of change
        """
        if len(cost_history) < 2:
            return {'trend': 'stable', 'change_rate': 0.0, 'confidence': 'low'}
        
        # Sort by timestamp
        sorted_history = sorted(cost_history, key=lambda x: x[0])
        
        # Calculate trend over last 7 days
        now = datetime.now()
        recent_history = [
            (timestamp, cost) for timestamp, cost in sorted_history
            if now - timestamp <= timedelta(days=7)
        ]
        
        if len(recent_history) < 2:
            return {'trend': 'stable', 'change_rate': 0.0, 'confidence': 'low'}
        
        # Simple linear trend calculation
        first_cost = recent_history[0][1]
        last_cost = recent_history[-1][1]
        
        if first_cost == 0:
            change_rate = 0.0
        else:
            change_rate = (last_cost - first_cost) / first_cost
        
        # Determine trend direction
        if abs(change_rate) < 0.05:  # Less than 5% change
            trend = 'stable'
            trend_symbol = '→'
        elif change_rate > 0:
            trend = 'increasing'
            trend_symbol = '↑'
        else:
            trend = 'decreasing'
            trend_symbol = '↓'
        
        # Confidence based on data points
        confidence = 'high' if len(recent_history) > 10 else 'medium' if len(recent_history) > 5 else 'low'
        
        return {
            'trend': trend,
            'trend_symbol': trend_symbol,
            'change_rate': change_rate,
            'confidence': confidence,
            'data_points': len(recent_history)
        }
    
    def estimate_monthly_cost(
        self, 
        cost_per_run: float, 
        runs_per_day: float
    ) -> Dict[str, float]:
        """Estimate monthly cost projection.
        
        Args:
            cost_per_run: Average cost per agent run
            runs_per_day: Average runs per day
            
        Returns:
            Monthly cost projections
        """
        daily_cost = cost_per_run * runs_per_day
        weekly_cost = daily_cost * 7
        monthly_cost = daily_cost * 30
        yearly_cost = daily_cost * 365
        
        return {
            'daily': daily_cost,
            'weekly': weekly_cost,
            'monthly': monthly_cost,
            'yearly': yearly_cost
        }
    
    def get_provider_comparison(self, estimated_tokens: Dict[str, int]) -> List[Dict[str, any]]:
        """Compare costs across all providers for given token usage.
        
        Args:
            estimated_tokens: Dict with 'input' and 'output' token counts
            
        Returns:
            List of provider/model combinations sorted by cost
        """
        comparisons = []
        
        input_tokens = estimated_tokens.get('input', 1000)
        output_tokens = estimated_tokens.get('output', 500)
        
        for provider, models in self.pricing.items():
            for model, pricing in models.items():
                cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
                
                comparisons.append({
                    'provider': provider,
                    'model': model,
                    'cost': cost,
                    'cost_per_1k_input': pricing['input'],
                    'cost_per_1k_output': pricing['output']
                })
        
        # Sort by cost (lowest first)
        comparisons.sort(key=lambda x: x['cost'])
        
        return comparisons 