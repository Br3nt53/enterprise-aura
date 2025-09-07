"""
Main entry point and API definitions for AURA v2.

This module wires together the domain services, infrastructure trackers and
FastAPI application.  It provides a command‑line interface via Typer to
run the service and includes health checks and a primary tracking endpoint.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np  # type: ignore
import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from aura_v2.domain import (
    Detection,
    Position3D,
    Confidence,
    Track,
    TrackStatus,
    ThreatLevel,
)
from aura_v2.domain.services import MultiSensorFusion, SensorCharacteristics
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker, TrackingResult

class DetectionInput(BaseModel):
    """Incoming detection payload for the API."""
    timestamp: datetime
    position: Dict[str, float]
    confidence: float = Field(ge=0.0, le=1.0)
    sensor_id: str
    attributes: Optional[Dict[str, Any]] = None

class TrackOutput(BaseModel):
    """Track output as returned by the API."""
    id: str
    position: Dict[str, float]
    velocity: Dict[str, float]
    confidence: float
    status: str
    threat_level: str
    created_at: datetime
    updated_at: datetime

class TrackRequest(BaseModel):
    """Request model for tracking endpoint."""
    radar_detections: List[DetectionInput] = Field(default_factory=list)
    camera_detections: List[DetectionInput] = Field(default_factory=list)
    lidar_detections: List[DetectionInput] = Field(default_factory=list)
    timestamp: Optional[datetime] = None

class TrackResponse(BaseModel):
    """Response model for tracking endpoint."""
    active_tracks: List[TrackOutput]
    new_tracks: List[TrackOutput] = Field(default_factory=list)
    deleted_tracks: List[str] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_id: int = 0

class AURAApplication:
    """AURA v2 application encapsulating domain services and API."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        self.app: Optional[FastAPI] = None
        self.tracker: Optional[ModernTracker] = None
        self.fusion_service: Optional[MultiSensorFusion] = None
        self._frame_id: int = 0

    async def initialize(self) -> None:
        """Initialize configuration, tracker and services."""
        if self.config_path and self.config_path.exists():
            self._load_config()

        # Tracker configuration
        tracking_cfg = self.config.get("tracking", {})
        self.tracker = ModernTracker(
            max_age=int(tracking_cfg.get("max_age", 30)),
            min_hits=int(tracking_cfg.get("min_hits", 3)),
            iou_threshold=float(tracking_cfg.get("iou_threshold", 0.3)),
            max_distance=float(tracking_cfg.get("max_distance", 50.0)),
        )

        # Sensor fusion configuration
        sensor_configs: Dict[str, SensorCharacteristics] = {
            "radar": SensorCharacteristics(
                sensor_id="radar",
                accuracy=2.0,
                update_rate=20.0,
                detection_probability=0.95,
                false_alarm_rate=0.01,
                covariance=np.eye(3) * 4.0,
            ),
            "camera": SensorCharacteristics(
                sensor_id="camera",
                accuracy=5.0,
                update_rate=30.0,
                detection_probability=0.90,
                false_alarm_rate=0.05,
                covariance=np.diag([25.0, 1.0, 25.0]),
            ),
            "lidar": SensorCharacteristics(
                sensor_id="lidar",
                accuracy=0.2,
                update_rate=10.0,
                detection_probability=0.85,
                false_alarm_rate=0.001,
                covariance=np.eye(3) * 0.04,
            ),
        }
        self.fusion_service = MultiSensorFusion(sensor_configs)

        self._build_app()

    def _load_config(self) -> None:
        """Load configuration from JSON or YAML file."""
        try:
            text = self.config_path.read_text()
            if self.config_path.suffix in {".yaml", ".yml"}:
           

This message was truncated. You can access the complete answer  :agentCitation{citationIndex='0' label='here'}
