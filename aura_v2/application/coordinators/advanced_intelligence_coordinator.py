from __future__ import annotations
from typing import Optional, List, Coroutine
from ...domain.value_objects import Collision
from ..domain.value_objects import Collision

# aura_v2/application/coordinators/advanced_intelligence_coordinator.py
import asyncio
import logging
from dataclasses import dataclass

from ...domain.entities import Track, ThreatLevel
from ...domain.services import ThreatAnalyzer, CollisionPredictor
from ...domain.value_objects import Threat, TacticalAlert
from ...infrastructure.persistence.in_memory import TrackHistoryRepository


@dataclass
class CoordinatorConfig:
    """Configuration for the AdvancedIntelligenceCoordinator."""

    threat_assessment_threshold: ThreatLevel = ThreatLevel.MEDIUM
    prune_history: bool = True


class AdvancedIntelligenceCoordinator:
    """
    A sophisticated, stateful coordinator that processes intelligence concurrently.
    """

    def __init__(
        self,
        threat_analyzer: ThreatAnalyzer,
        collision_predictor: CollisionPredictor,
        track_history: TrackHistoryRepository,
        logger: logging.Logger,
        config: CoordinatorConfig = CoordinatorConfig(),
    ):
        self.threat_analyzer = threat_analyzer
        self.collision_predictor = collision_predictor
        self.track_history = track_history
        self.logger = logger
        self.config = config

    async def process_tracks(self, tracks: List[Track]) -> List[TacticalAlert]:
        """
        Asynchronously assesses threats, predicts collisions for high-priority
        tracks, and returns a fused list of tactical alerts.
        """
        self.logger.info(f"Processing {len(tracks)} tracks.")

        # Step 1: Update and prune track history
        active_track_ids = [t.id for t in tracks]
        for track in tracks:
            self.track_history.update(track)
        if self.config.prune_history:
            self.track_history.prune(active_track_ids)

        # Step 2: Concurrently assess threats for all tracks
        threat_assessment_tasks: List[Coroutine] = [
            self._assess_individual_threat(track) for track in tracks
        ]
        assessed_threats: List[Threat] = await asyncio.gather(*threat_assessment_tasks)

        # Step 3: Filter for threats that meet the required level for further analysis
        priority_threats = [
            threat
            for threat in assessed_threats
            if threat
            and threat.threat_level.value
            >= self.config.threat_assessment_threshold.value
        ]

        if not priority_threats:
            self.logger.info("No high-priority threats identified.")
            return []

        self.logger.info(
            f"Identified {len(priority_threats)} priority threats for collision analysis."
        )

        # Step 4: Run collision prediction only on the priority subset
        priority_tracks = [threat.track for threat in priority_threats]
        potential_collisions = self.collision_predictor.predict(priority_tracks)

        # Step 5: Fuse threats and collisions into tactical alerts
        alerts = self._fuse_intelligence(priority_threats, potential_collisions)

        self.logger.info(f"Generated {len(alerts)} tactical alerts.")
        return alerts

    async def _assess_individual_threat(self, track: Track) -> Optional[Threat]:
        """Analyzes a single track, considering its history."""
        # This is where historical analysis would be added.
        # For now, it delegates to the analyzer.
        threat_level = self.threat_analyzer.analyze(track)
        if threat_level != ThreatLevel.LOW:
            return Threat(track, threat_level, track.confidence.value)
        return None

    def _fuse_intelligence(
        self, threats: List[Threat], collisions: List[Collision]
    ) -> List[TacticalAlert]:
        """Combines threat and collision data into actionable alerts."""
        alerts = []
        collision_map = {(c.track1.id, c.track2.id): c for c in collisions}

        for threat in threats:
            # Check if this threat is involved in any predicted collision
            related_collision = None
            for (id1, id2), collision in collision_map.items():
                if threat.track.id in [id1, id2]:
                    related_collision = collision
                    break

            # Urgency can be a complex calculation. Here's a simple example.
            urgency = (
                threat.threat_level.value / len(ThreatLevel) + threat.confidence.value
            )
            if related_collision:
                urgency += 1.0 - (
                    related_collision.time_to_collision / 60.0
                )  # Higher urgency for closer collisions

            alerts.append(
                TacticalAlert(
                    threat=threat,
                    collision=related_collision,
                    urgency=min(1.0, urgency / 2.0),  # Normalize
                )
            )

        # Sort alerts by the highest urgency
        return sorted(alerts, key=lambda a: a.urgency, reverse=True)
