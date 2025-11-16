"""
Analytics Service
Provides analytics and insights on test results
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class AnalyticsService:
    """Analytics Service for test results"""
    
    def calculate_coverage(self, results: Dict[str, Dict]) -> Dict:
        """Calculate API coverage metrics"""
        total_apis = len(results)
        successful = sum(1 for r in results.values() if r.get("status") == "success")
        partial = sum(1 for r in results.values() if r.get("status") == "partial")
        failed = sum(1 for r in results.values() if r.get("status") == "failure")
        
        return {
            "total_apis": total_apis,
            "successful": successful,
            "partial": partial,
            "failed": failed,
            "success_rate": (successful / total_apis * 100) if total_apis > 0 else 0,
            "coverage_rate": ((successful + partial) / total_apis * 100) if total_apis > 0 else 0
        }
    
    def calculate_quality_metrics(self, results: Dict[str, Dict]) -> Dict:
        """Calculate data quality metrics"""
        quality_scores = []
        
        for api_name, result in results.items():
            if result.get("data_returned"):
                # Calculate quality score based on completeness and accuracy
                completeness = result.get("data_quality", {}).get("completeness", 0)
                accuracy = result.get("data_quality", {}).get("accuracy", 0)
                quality_score = (completeness + accuracy) / 2
                quality_scores.append({
                    "api": api_name,
                    "quality_score": quality_score
                })
        
        avg_quality = sum(s["quality_score"] for s in quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "average_quality": avg_quality,
            "api_quality_scores": quality_scores,
            "highest_quality": max(quality_scores, key=lambda x: x["quality_score"]) if quality_scores else None,
            "lowest_quality": min(quality_scores, key=lambda x: x["quality_score"]) if quality_scores else None
        }
    
    def calculate_costs(self, results: Dict[str, Dict]) -> Dict:
        """Calculate cost breakdown"""
        total_cost = sum(r.get("cost_incurred", 0) for r in results.values())
        
        cost_breakdown = []
        for api_name, result in results.items():
            cost = result.get("cost_incurred", 0)
            if cost > 0:
                cost_breakdown.append({
                    "api": api_name,
                    "cost": cost,
                    "currency": "GBP"
                })
        
        return {
            "total_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "most_expensive": max(cost_breakdown, key=lambda x: x["cost"]) if cost_breakdown else None,
            "free_apis": [name for name, r in results.items() if r.get("cost_incurred", 0) == 0]
        }
    
    def generate_recommendations(self, results: Dict[str, Dict[str, Any]], fusion_analysis: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for failures
        failed_apis = [name for name, r in results.items() if r.get("status") == "failure"]
        if failed_apis:
            recommendations.append(
                f"⚠️ {len(failed_apis)} API(s) failed: {', '.join(failed_apis)}. Check credentials and network connectivity."
            )
        
        # Check costs
        costs = self.calculate_costs(results)
        if costs["total_cost"] > 1.0:
            recommendations.append(
                f"💰 Total cost: £{costs['total_cost']:.2f}. Consider caching results to reduce costs."
            )
        
        # Check data quality
        quality = self.calculate_quality_metrics(results)
        if quality["average_quality"] < 70:
            recommendations.append(
                f"📊 Average data quality: {quality['average_quality']:.1f}%. Some APIs may need better configuration."
            )
        
        # Risk assessment recommendations
        if fusion_analysis:
            risk_score = fusion_analysis.get("risk_assessment", {}).get("overall_score", 0)
            if risk_score > 70:
                recommendations.append(
                    "🚨 HIGH RISK detected. Multiple quality indicators show concerns. Consider avoiding this care home."
                )
            elif risk_score > 40:
                recommendations.append(
                    "⚠️ MEDIUM RISK detected. Some quality concerns identified. Proceed with caution."
                )
        
        if not recommendations:
            recommendations.append("✅ All tests passed successfully. Data quality is good.")
        
        return recommendations

