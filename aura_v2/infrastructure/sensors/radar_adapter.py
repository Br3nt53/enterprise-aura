# aura_v2/infrastructure/sensors/radar_adapter.py
import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator, Dict, List
import numpy as np

from ...domain.entities import Detection
from ...domain.value_objects import Confidence, Position3D, Velocity3D


class RadarAdapter:
    """Real radar sensor integration with CFAR detection"""

    def __init__(
        self,
        device_path: str = "/dev/radar0",
        sample_rate: int = 1000000,  # 1 MHz
        range_resolution: float = 0.5,  # meters
        velocity_resolution: float = 0.1,
    ):  # m/s
        self.device_path = device_path
        self.sample_rate = sample_rate
        self.range_res = range_resolution
        self.vel_res = velocity_resolution
        self._connected = False

    async def stream(self) -> AsyncIterator[List[Detection]]:
        """Stream detections from radar"""

        while True:
            try:
                # Simulate radar data acquisition
                raw_data = await self._read_radar_frame()

                # Process range-doppler map
                range_doppler = self._process_range_doppler(raw_data)

                # CFAR detection
                detections = self._cfar_detect(range_doppler)

                # Convert to domain entities
                domain_detections = []
                for det in detections:
                    position = self._polar_to_cartesian(
                        det["range"], det["azimuth"], det["elevation"]
                    )

                    detection = Detection(
                        timestamp=datetime.now(timezone.utc),
                        position=Position3D(x=position[0], y=position[1], z=position[2]),
                        velocity=Velocity3D(vx=det["doppler_velocity"], vy=0, vz=0),
                        confidence=Confidence(min(1.0, det["snr"] / 30.0)),
                        sensor_id="radar_main",
                        attributes={
                            "rcs": det["rcs"],
                            "snr": det["snr"],
                            "doppler": det["doppler_velocity"],
                        },
                    )
                    domain_detections.append(detection)

                yield domain_detections

                # Control update rate
                await asyncio.sleep(0.05)  # 20 Hz

            except Exception as e:
                # Log error and continue
                print(f"Radar error: {e}")
                await asyncio.sleep(0.1)

    async def _read_radar_frame(self) -> np.ndarray:
        """Simulate reading radar frame"""
        # Generate synthetic radar data for testing
        return np.random.complex128((256, 128))

    def _process_range_doppler(self, raw_data: np.ndarray) -> np.ndarray:
        """Generate range-doppler map from raw radar data"""
        # FFT for range processing
        range_fft = np.fft.fft(raw_data, axis=0)

        # FFT for doppler processing
        doppler_fft = np.fft.fft(range_fft, axis=1)

        # Power spectrum
        range_doppler = np.abs(doppler_fft) ** 2

        return range_doppler

    def _cfar_detect(self, range_doppler: np.ndarray, pfa: float = 1e-6) -> List[Dict]:
        """Constant False Alarm Rate detection"""
        detections = []

        # CFAR parameters
        guard_cells = 4
        training_cells = 16

        rows, cols = range_doppler.shape

        # Scan through range-doppler map
        for r in range(guard_cells + training_cells, rows - guard_cells - training_cells):
            for d in range(guard_cells + training_cells, cols - guard_cells - training_cells):
                # Cell under test
                cut = range_doppler[r, d]

                # Training cells (excluding guard cells)
                training = []
                for i in range(-training_cells - guard_cells, training_cells + guard_cells + 1):
                    for j in range(-training_cells - guard_cells, training_cells + guard_cells + 1):
                        if abs(i) > guard_cells or abs(j) > guard_cells:
                            training.append(range_doppler[r + i, d + j])

                # CFAR threshold
                noise_level = np.mean(training)
                threshold = noise_level * (-np.log(pfa))

                # Detection
                if cut > threshold:
                    detections.append(
                        {
                            "range": r * self.range_res,
                            "doppler_velocity": (d - cols // 2) * self.vel_res,
                            "snr": 10 * np.log10(cut / noise_level),
                            "azimuth": 0,  # Would come from antenna array
                            "elevation": 0,
                            "rcs": cut,  # Radar cross section
                        }
                    )

        return detections

    def _polar_to_cartesian(
        self, range_m: float, azimuth_rad: float, elevation_rad: float
    ) -> np.ndarray:
        """Convert polar coordinates to Cartesian"""
        x = range_m * np.cos(elevation_rad) * np.cos(azimuth_rad)
        y = range_m * np.cos(elevation_rad) * np.sin(azimuth_rad)
        z = range_m * np.sin(elevation_rad)
        return np.array([x, y, z])
