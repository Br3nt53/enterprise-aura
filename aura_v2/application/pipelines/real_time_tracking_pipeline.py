# aura_v2/application/pipelines/real_time_tracking_pipeline.py
import asyncio
from typing import AsyncIterator
from dataclasses import dataclass
import time

from ..use_cases import DetectAndTrackUseCase
from ...infrastructure.monitoring import MetricsCollector
from ...domain.events import EventBus

@dataclass
class PipelineConfig:
    """Configuration for tracking pipeline"""
    max_latency_ms: int = 50
    batch_size: int = 10
    enable_gpu: bool = True
    enable_threat_assessment: bool = True
    enable_collision_prediction: bool = True

class RealTimeTrackingPipeline:
    """
    High-performance real-time tracking pipeline
    Handles 100+ targets at 30+ FPS with <50ms latency
    """
    
    def __init__(self,
                 detect_and_track: DetectAndTrackUseCase,
                 sensor_streams: Dict[str, SensorStream],
                 event_bus: EventBus,
                 metrics: MetricsCollector,
                 config: PipelineConfig):
        self.detect_and_track = detect_and_track
        self.sensor_streams = sensor_streams
        self.event_bus = event_bus
        self.metrics = metrics
        self.config = config
        
        # Performance optimization
        self.detection_queue = asyncio.Queue(maxsize=100)
        self.result_queue = asyncio.Queue(maxsize=100)
        
    async def run(self) -> None:
        """Main pipeline execution"""
        
        # Start sensor data collection
        sensor_tasks = [
            asyncio.create_task(self._collect_sensor_data(name, stream))
            for name, stream in self.sensor_streams.items()
        ]
        
        # Start processing pipeline
        processing_task = asyncio.create_task(self._process_detections())
        
        # Start result handling
        result_task = asyncio.create_task(self._handle_results())
        
        # Monitor performance
        monitor_task = asyncio.create_task(self._monitor_performance())
        
        # Run until cancelled
        try:
            await asyncio.gather(
                *sensor_tasks,
                processing_task,
                result_task,
                monitor_task
            )
        except asyncio.CancelledError:
            # Graceful shutdown
            await self._shutdown()
    
    async def _collect_sensor_data(self, 
                                  sensor_name: str,
                                  stream: SensorStream) -> None:
        """Collect data from individual sensor"""
        
        async for data in stream:
            # Add to processing queue
            await self.detection_queue.put({
                'sensor': sensor_name,
                'data': data,
                'timestamp': time.time()
            })
            
            # Track input rate
            self.metrics.increment(f'sensor.{sensor_name}.detections')
    
    async def _process_detections(self) -> None:
        """Main processing loop"""
        
        batch = []
        last_process_time = time.time()
        
        while True:
            try:
                # Collect batch
                while len(batch) < self.config.batch_size:
                    timeout = self.config.max_latency_ms / 1000.0
                    try:
                        detection = await asyncio.wait_for(
                            self.detection_queue.get(),
                            timeout=timeout
                        )
                        batch.append(detection)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # Process batch
                    start = time.time()
                    
                    # Group by sensor type
                    radar = [d['data'] for d in batch if d['sensor'] == 'radar']
                    lidar = [d['data'] for d in batch if d['sensor'] == 'lidar']
                    camera = [d['data'] for d in batch if d['sensor'] == 'camera']
                    
                    # Execute tracking
                    result = await self.detect_and_track.execute(
                        DetectAndTrackCommand(
                            radar_data=radar,
                            lidar_data=lidar,
                            camera_data=camera,
                            timestamp=datetime.now()
                        )
                    )
                    
                    # Queue result
                    await self.result_queue.put(result)
                    
                    # Metrics
                    latency = (time.time() - start) * 1000
                    self.metrics.histogram('pipeline.latency_ms', latency)
                    self.metrics.gauge('pipeline.active_tracks', len(result.active_tracks))
                    
                    batch.clear()
                    
            except Exception as e:
                self.metrics.increment('pipeline.errors')
                # Log error but continue processing
                await self._handle_error(e)
    
    async def _handle_results(self) -> None:
        """Handle tracking results and generate outputs"""
        
        while True:
            result = await self.result_queue.get()
            
            # Publish events
            for event in result.events:
                await self.event_bus.publish(event)
            
            # Handle threats
            for threat in result.threats:
                await self._handle_threat(threat)
            
            # Update displays/dashboards
            await self._update_displays(result)
    
    async def _handle_threat(self, threat: ThreatAssessment) -> None:
        """Handle detected threats with appropriate actions"""
        
        if threat.threat_level == ThreatLevel.CRITICAL:
            # Immediate action required
            await self._trigger_critical_alert(threat)
            await self._activate_countermeasures(threat)
            
        elif threat.threat_level == ThreatLevel.HIGH:
            # Alert operators
            await self._send_operator_alert(threat)
            
        # Log all threats
        await self._log_threat(threat)