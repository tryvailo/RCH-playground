"""Logging utilities for structured error tracking"""
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class GenerationStep(Enum):
    """Steps in report generation"""

    INITIALIZATION = "initialization"
    POSTCODE_RESOLUTION = "postcode_resolution"
    DATA_LOADING = "data_loading"
    FILTERING = "filtering"
    MATCHING = "matching"
    GAP_CALCULATION = "gap_calculation"
    AREA_ANALYSIS = "area_analysis"
    MAP_GENERATION = "map_generation"
    INSIGHTS_GENERATION = "insights_generation"
    RESPONSE_ASSEMBLY = "response_assembly"


class GenerationContext:
    """Context for tracking report generation process"""

    def __init__(self, report_id: str, postcode: str, care_type: str):
        self.report_id = report_id
        self.postcode = postcode
        self.care_type = care_type
        self.start_time = datetime.now()
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.steps_completed: List[str] = []
        self.logger = logging.getLogger(f"free_report.{report_id}")

    def log_step_start(self, step: GenerationStep):
        """Log step start"""
        self.logger.info(f"Starting: {step.value}")

    def log_step_complete(self, step: GenerationStep, details: dict = None):
        """Log step completion"""
        self.steps_completed.append(step.value)
        msg = f"Completed: {step.value}"
        if details:
            msg += f" | {json.dumps(details)}"
        self.logger.info(msg)

    def log_error(
        self, step: GenerationStep, error: Exception, context: str = ""
    ):
        """Log error in specific step"""
        error_entry = {
            "step": step.value,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        self.errors.append(error_entry)
        self.logger.error(
            f"Error in {step.value}: {error}",
            extra={"context": context},
            exc_info=True,
        )

    def log_warning(self, step: GenerationStep, message: str):
        """Log warning in specific step"""
        warning_entry = {
            "step": step.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        self.warnings.append(warning_entry)
        self.logger.warning(f"[{step.value}] {message}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of generation process"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            "report_id": self.report_id,
            "postcode": self.postcode,
            "care_type": self.care_type,
            "elapsed_seconds": elapsed,
            "steps_completed": self.steps_completed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "status": "success" if not self.errors else "partial_success",
        }
