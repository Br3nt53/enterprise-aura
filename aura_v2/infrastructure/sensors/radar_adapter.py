# aura_v2/infrastructure/sensors/radar_adapter.py
import asyncio
from typing import AsyncIterator, Optional
import numpy as np

from ...domain.entities import Detection, Position3D, Confidence
from ...domain.ports import SensorAdapter

class RadarAdapter(SensorAdapter):
    """
    Real radar sensor integration
    Handles range-doppler processing and CFAR detection
    """
    
    def __init__(self, 
                 device_path: str,
                 sample_rate: int = 1000000,  # 1 MHz
                 range_resolution: float = 0.5,  # meters
                 velocity_resolution: float = 0.1):  # m/s
        
        self.device_path = device_path
        self.sample_rate = sample_rate
        self.range_res = range_resolution
        self.vel_res = velocity_resolution
        
        # Connect to radar hardware
        self._connect()
        
    async def stream(self) -> AsyncIterator[List[Detection]]:
        """Stream detections from radar"""
        
        while True:
            # Read radar data
            raw_data = await self._read_radar_frame()
            
            # Process range-doppler map
            range_doppler = self._process_range_doppler(raw_data)
            
            # CFAR detection
            detections = self._cfar_detect(range_doppler)
            
            # Convert to domain entities
            domain_detections = []
            for det in detections:
                position = self._polar_to_cartesian(
                    det['range'], 
                    det['azimuth'],
                    det['elevation']
                )
                
                detection = Detection(
                    timestamp=datetime.now(),
                    position=Position3D(
                        x=position[0],
                        y=position[1],
                        z=position[2]
                    ),
                    velocity=Velocity3D(
                        vx=det['doppler_velocity'],
                        vy=0,
                        vz=0
                    ),
                    confidence=Confidence(det['snr'] / 100.0),
                    sensor_id='radar_main',
                    metadata={
                        'rcs': det['rcs'],  # Radar cross section
                        'snr': det['snr'],
                        'doppler': det['doppler_velocity']
                    }
                )
                domain_detections.append(detection)
            
            yield domain_detections
            
            # Control update rate
            await asyncio.sleep(0.05)  # 20 Hz
    
    def _process_range_doppler(self, raw_data: np.ndarray) -> np.ndarray:
        """Generate range-doppler map from raw radar data"""
        
        # FFT for range processing
        range_fft = np.fft.fft(raw_data, axis=0)
        
        # FFT for doppler processing  
        doppler_fft = np.fft.fft(range_fft, axis=1)
        
        # Power spectrum
        range_doppler = np.abs(doppler_fft) ** 2
        
        return range_doppler
    
    def _cfar_detect(self, 
                     range_doppler: np.ndarray,
                     pfa: float = 1e-6) -> List[Dict]:
        """
        Constant False Alarm Rate detection
        Industry-standard radar detection algorithm
        """
        
        detections = []
        
        # CFAR parameters
        guard_cells = 4
        training_cells = 16
        
        # Scan through range-doppler map
        for r in range(guard_cells + training_cells, 
                      range_doppler.shape[0] - guard_cells - training_cells):
            for d in range(guard_cells + training_cells,
                          range_doppler.shape[1] - guard_cells - training_cells):
                
                # Cell under test
                cut = range_doppler[r, d]
                
                # Training cells (excluding guard cells)
                training = []
                for i in range(-training_cells-guard_cells, 
                             training_cells+guard_cells+1):
                    for j in range(-training_cells-guard_cells,
                                 training_cells+guard_cells+1):
                        if abs(i) > guard_cells or abs(j) > guard_cells:
                            training.append(range_doppler[r+i, d+j])
                
                # CFAR threshold
                noise_level = np.mean(training)
                threshold = noise_level * (-np.log(pfa))
                
                # Detection
                if cut > threshold:
                    detections.append({
                        'range': r * self.range_res,
                        'doppler_velocity': (d - range_doppler.shape[1]//2) * self.vel_res,
                        'snr': 10 * np.log10(cut / noise_level),
                        'azimuth': 0,  # Would come from antenna array
                        'elevation': 0,
                        'rcs': cut  # Radar cross section
                    })
        
        return detections