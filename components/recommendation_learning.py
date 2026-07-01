#!/usr/bin/env python3
"""
Recommendation Learning Component
Learning system for recommendation improvement.
"""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class RecommendationTracker:
    """Recommendation tracking and learning system."""
    
    def __init__(self):
        self.tracked_recommendations = {}
        self.performance_data = []
        logger.info("Recommendation Tracker initialized")
    
    def track_recommendation(self, recommendation_data: Dict):
        """Track a recommendation for learning."""
        try:
            tracking_id = f"{recommendation_data.get('symbol', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.tracked_recommendations[tracking_id] = recommendation_data
            logger.info(f"Tracked recommendation: {tracking_id}")
        except Exception as e:
            logger.error(f"Error tracking recommendation: {str(e)}")
    
    def add_performance_record(self, performance_record: Dict):
        """Add performance record."""
        try:
            self.performance_data.append(performance_record)
            logger.info(f"Added performance record for {performance_record.get('symbol', 'unknown')}")
        except Exception as e:
            logger.error(f"Error adding performance record: {str(e)}")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        try:
            if not self.performance_data:
                return {"message": "No performance data available"}
            
            total_recommendations = len(self.performance_data)
            successful_recommendations = len([p for p in self.performance_data if p.get('performance_pct', 0) > 0])
            success_rate = (successful_recommendations / total_recommendations) * 100 if total_recommendations > 0 else 0
            
            return {
                'total_recommendations': total_recommendations,
                'successful_recommendations': successful_recommendations,
                'success_rate': success_rate,
                'average_performance': sum(p.get('performance_pct', 0) for p in self.performance_data) / total_recommendations if total_recommendations > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {"error": str(e)}
