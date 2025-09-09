# aura_v2/infrastructure/reporting/system_report.py
from datetime import datetime
from typing import Dict, List, Any
import json
from pathlib import Path


class SystemReportGenerator:
    """Generates comprehensive system reports for debugging and monitoring."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_health_report(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a system health report."""
        timestamp = datetime.now()

        report = {
            "timestamp": timestamp.isoformat(),
            "system_status": "operational",
            "metrics": telemetry_data,
            "components": {
                "tracker": {
                    "status": "active",
                    "tracks": len(telemetry_data.get("active_tracks", [])),
                },
                "sensors": {
                    "status": "active",
                    "count": telemetry_data.get("sensor_count", 0),
                },
                "fusion": {"status": "active", "last_update": timestamp.isoformat()},
            },
            "performance": {
                "processing_time_ms": telemetry_data.get("processing_time_ms", 0),
                "memory_usage": telemetry_data.get("memory_usage", "unknown"),
                "cpu_usage": telemetry_data.get("cpu_usage", "unknown"),
            },
        }

        # Save report
        report_file = self.output_dir / f"health_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def generate_tracking_summary(self, tracking_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a tracking performance summary."""
        if not tracking_results:
            return {"error": "No tracking results available"}

        total_tracks = sum(len(result.get("active_tracks", [])) for result in tracking_results)
        avg_processing_time = sum(
            result.get("processing_time_ms", 0) for result in tracking_results
        ) / len(tracking_results)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_frames_processed": len(tracking_results),
            "total_tracks_detected": total_tracks,
            "average_tracks_per_frame": total_tracks / len(tracking_results),
            "average_processing_time_ms": avg_processing_time,
            "performance_metrics": {
                "min_processing_time": min(
                    result.get("processing_time_ms", 0) for result in tracking_results
                ),
                "max_processing_time": max(
                    result.get("processing_time_ms", 0) for result in tracking_results
                ),
                "frames_with_tracks": sum(
                    1 for result in tracking_results if result.get("active_tracks")
                ),
            },
        }

        # Save summary
        summary_file = (
            self.output_dir / f"tracking_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary

    def generate_error_report(self, errors: List[Exception]) -> Dict[str, Any]:
        """Generate an error analysis report."""
        error_report = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors),
            "error_types": {},
            "error_details": [],
        }

        for error in errors:
            error_type = type(error).__name__
            error_report["error_types"][error_type] = (
                error_report["error_types"].get(error_type, 0) + 1
            )
            error_report["error_details"].append(
                {
                    "type": error_type,
                    "message": str(error),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Save error report
        error_file = (
            self.output_dir / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(error_file, "w") as f:
            json.dump(error_report, f, indent=2)

        return error_report
