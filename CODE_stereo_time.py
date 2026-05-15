#!/usr/bin/env python3
import numpy as np
import wave, math

# First, we load the mono source file
INPUT_FILE = "CODE_mono.wav"
OUTPUT_FILE = "CODE_stereo_time.wav"

with wave.open(INPUT_FILE, 'r') as f:
    sample_rate  = f.getframerate()    # 48 000 Hz
    n_frames = f.getnframes()
    raw_bytes = f.readframes(n_frames)

# We convert raw bytes to a float64 numpy array normalised to [-1, 1]
mono = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float64) / 32768.0

# This is the ITD calculator using the spherical head model:
#   ITD = r * (θ + sin(θ)) / c
# where r = head radius (0.0875 m) and c = speed of sound (343 m/s)
# The result tells us how many seconds the sound arrives later to the far ear
HEAD_RADIUS = 0.0875   # meters
SPEED_SOUND = 343.0    # m/s

def compute_itd_samples(source_angle_deg, fs):
    theta = math.radians(source_angle_deg)
    itd_seconds = HEAD_RADIUS * (theta + math.sin(theta)) / SPEED_SOUND
    return round(abs(itd_seconds) * fs)   # convert to integer samples

# We define the four panning positions: 0°, 10° left, 20° left, 30° left
# "Left" = positive angle in counterclockwise convention
panning_angles = [0, 10, 20, 30]

print(f"Sample rate: {sample_rate} Hz\n")
print(f"{'Angle':>8}   {'tL - tR (samples)':>18}   {'tL - tR (ms)':>13}")
print("-" * 46)
for angle in panning_angles:
    samples = compute_itd_samples(angle, sample_rate)
    ms = samples / sample_rate * 1000
    print(f"{angle:>8}°  {samples:>18}   {ms:>13.4f}")

# Finally, we build the 20-second stereo output
# If the source is to the LEFT:  left ear hears first  → right channel is delayed
# If the source is to the RIGHT: right ear hears first → left channel is delayed
# If the source is at the CENTRE: no delay on either channel
stereo_frames = []

for angle in panning_angles:
    delay = compute_itd_samples(angle, sample_rate)
    n = len(mono)
    left  = np.zeros(n)
    right = np.zeros(n)

    if angle > 0: # source is LEFT  → left plays first, right is delayed
        left[:] = mono
        right[delay:] = mono[:n - delay] if delay > 0 else mono
    elif angle < 0: # source is RIGHT → right plays first, left is delayed
        right[:] = mono
        left[delay:] = mono[:n - delay] if delay > 0 else mono
    else: # centre → both channels identical, no delay
        left[:]  = mono
        right[:] = mono

    stereo_frames.append(np.column_stack((left, right)))

# We stack all four segments into one long array
stereo = np.vstack(stereo_frames)

# Then we write the stereo output file, converting back to 16-bit integers
stereo_int16 = (stereo * 32767).astype(np.int16)

with wave.open(OUTPUT_FILE, 'w') as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(sample_rate)
    f.writeframes(stereo_int16.tobytes())

print(f"\nWrote {OUTPUT_FILE}  ({stereo_int16.shape[0] / sample_rate:.1f} s, 2 channels)")