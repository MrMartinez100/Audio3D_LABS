#!/usr/bin/env python3
import numpy as np
import wave, struct, math

# First, we load the mono source file (5 seconds of a pad sound at 48 kHz, 16-bit PCM)
INPUT_FILE = "CODE_mono.wav"
OUTPUT_FILE = "CODE_stereo_intensity.wav"

with wave.open(INPUT_FILE, 'r') as f:
    sample_rate   = f.getframerate()          
    n_frames = f.getnframes()            
    sample_width  = f.getsampwidth()         
    raw_bytes = f.readframes(n_frames)

# WE convert raw bytes to a float64 numpy array normalised to [-1, 1]
mono = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float64) / 32768.0

# this is the tangent-law gain calculator
SPEAKER_HALF_ANGLE = 30.0   # θ_t  (degrees) – half the stereo aperture

def tangent_law_gains(source_angle_deg):
    theta_t = math.radians(SPEAKER_HALF_ANGLE)
    theta = math.radians(source_angle_deg)

    # Solve: ratio = tan(θ) / tan(θ_t)
    ratio = math.tan(theta) / math.tan(theta_t)

    gL = 0.5 * (1.0 + ratio)
    gR = 0.5 * (1.0 - ratio)

    # Clamp to [0, 1] (handles exact ±30° cases safely)
    gL = max(0.0, min(1.0, gL))
    gR = max(0.0, min(1.0, gR))

    return gL, gR # Returns (gLeft, gRight) for a virtual source at source_angle_deg.

# Then we define the four panning positions : 0°, 10° right, 20° right, 30° right
# NOtice that "right" = negative angle in our counterclockwise convention
panning_angles = [0, -10, -20, -30] 

print("Gains for each position:")
print(f"{'Angle':>8}   {'gLeft':>8}   {'gRight':>8}")
print("-" * 32)
for angle in panning_angles:
    gL, gR = tangent_law_gains(angle)
    print(f"{angle:>8}°  {gL:>8.4f}   {gR:>8.4f}")

# Finally, build the 20-second stereo output 
stereo_frames = []   # list of (left_sample, right_sample) tuples

for angle in panning_angles:
    gL, gR = tangent_law_gains(angle)
    left_channel = mono * gL
    right_channel = mono * gR
    stereo_frames.append(np.column_stack((left_channel, right_channel)))

# we stack all four segments into one long array  
stereo = np.vstack(stereo_frames)  

# then we write the stereo output file 
# we convert back to 16-bit integers
stereo_int16 = (stereo * 32767).astype(np.int16)

with wave.open(OUTPUT_FILE, 'w') as f:
    f.setnchannels(2)
    f.setsampwidth(2)         
    f.setframerate(sample_rate)
    f.writeframes(stereo_int16.tobytes())

print(f"\nWrote {OUTPUT_FILE}  ({stereo_int16.shape[0] / sample_rate:.1f} s, 2 channels)")