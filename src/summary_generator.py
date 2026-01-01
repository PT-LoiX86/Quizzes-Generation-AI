import json
from datetime import datetime
from src.utils import get_timestamp, save_json

# Generates debug summaries for each question generation batch
class SummaryGenerator:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()

    def generate_summary(self, element_file, questions_generated, statistics, success=True, error_msg=None):
        # Calculate confidence score
        confidence = self._calculate_confidence_score(statistics, success)
        
        summary = {
            "metadata": {
                "timestamp": self.timestamp,
                "element_file": element_file,
                "success": success,
                "error_message": error_msg
            },
            "performance": {
                "questions_generated": questions_generated,
                "total_attempts": statistics['total_attempts'],
                "generation_success_rate": statistics.get('success_rate', '0%')
            },
            "quality_metrics": {
                "duplicates_found_and_removed": statistics.get('duplicates_found', 0),
                "failed_template_generations": statistics.get('failed_generations', 0)
            },
            "debug_info": {
                "confidence_score": confidence
            }
        }
        return summary

    def _calculate_confidence_score(self, statistics, success):
        if not success:
            return 0.0
            
        base_score = 1.0
        
        # Penalize failed template generations
        if statistics['total_attempts'] > 0:
            failure_rate = statistics.get('failed_generations', 0) / statistics['total_attempts']
            base_score -= (failure_rate * 0.3)
            
        # Small penalty for duplicates
        if statistics.get('duplicates_found', 0) > 0:
            base_score -= min(0.05, statistics['duplicates_found'] * 0.01)

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, base_score))

    def save_summary(self, summary, output_dir="output/summaries"):
        timestamp = get_timestamp()
        filename = f"{output_dir}/summary_{timestamp}.json"
        save_json(summary, filename)
        return filename
