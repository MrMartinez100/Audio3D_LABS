#!/usr/bin/env python3
import numpy as np
import wave, math

# First, we load the mono source file
INPUT_FILE  = "CODE_mono.wav"
OUTPUT_FILE = "CODE_51_intensity.wav"

with wave.open(INPUT_FILE, 'r') as f:
    sample_rate = f.getframerate()
    n_frames    = f.getnframes()
    raw_bytes   = f.readframes(n_frames)

# We convert raw bytes to a float64 numpy array normalised to [-1, 1]
mono = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float64) / 32768.0

# 5.1 loudspeaker layout: channel order is L-R-C-LFE-Ls-Rs
# LFE (index 3) is a subwoofer — non-directional, we always leave it silent
# Angles: positive = left (counterclockwise), negative = right
SPEAKERS = [
    {"name": "L",   "angle":   30, "index": 0},
    {"name": "R",   "angle":  -30, "index": 1},
    {"name": "C",   "angle":    0, "index": 2},
    {"name": "LFE", "angle": None, "index": 3},  # subwoofer, always silent, this is the ".1" of 5.1
    {"name": "Ls",  "angle":  110, "index": 4},
    {"name": "Rs",  "angle": -110, "index": 5},
]
N_CHANNELS = 6

# This finds the two speakers that bracket the virtual source angle.
# We go around the circle and find the pair whose arc contains the source.
# "Bracketing" means one speaker is CCW and one is CW of the source angle.
DIRECTIONAL = [s for s in SPEAKERS if s["angle"] is not None]

def find_speaker_pair(source_angle):
    # Sort speakers by angle to walk around the circle
    sorted_spk = sorted(DIRECTIONAL, key=lambda s: s["angle"])
    angles = [s["angle"] for s in sorted_spk]

    for i in range(len(sorted_spk)):
        a1 = angles[i]
        a2 = angles[(i + 1) % len(sorted_spk)]

        # Handle the wrap-around gap (e.g. -110° to +110° going through ±180°)
        if a1 > a2:
            if source_angle >= a1 or source_angle <= a2:
                return sorted_spk[i], sorted_spk[(i + 1) % len(sorted_spk)]
        else:
            if a1 <= source_angle <= a2:
                return sorted_spk[i], sorted_spk[(i + 1) % len(sorted_spk)]

    return sorted_spk[0], sorted_spk[1]  # fallback

# This is the Tangent Law gain calculator (same as stereo exercise)
# θ_t is the half-angle between the two active speakers
def tangent_law_gains(source_angle, spk1_angle, spk2_angle):
    # If source is exactly on a speaker, give it all the gain
    if source_angle == spk1_angle:
        return 1.0, 0.0
    if source_angle == spk2_angle:
        return 0.0, 1.0

    # θ_t = half the angular span between the two speakers
    span   = spk2_angle - spk1_angle
    center = (spk1_angle + spk2_angle) / 2.0
    theta_t = math.radians(abs(span) / 2.0)

    # Angle of source relative to the centre of the speaker pair
    theta = math.radians(source_angle - center)

    ratio = math.tan(theta) / math.tan(theta_t)
    g1 = max(0.0, min(1.0, 0.5 * (1.0 + ratio)))
    g2 = max(0.0, min(1.0, 0.5 * (1.0 - ratio)))
    return g1, g2

# We define the four virtual source positions from the assignment
panning_angles = [0, 60, 90, 180]

print("5.1 Intensity Panning — gains per channel")
print(f"{'Angle':>7}  {'L(+30)':>8} {'R(-30)':>8} {'C(0)':>8} {'LFE':>6} {'Ls(+110)':>10} {'Rs(-110)':>10}  Speakers used")
print("-" * 85)

# Finally, we build the 20-second 6-channel output
all_segments = []

for source_angle in panning_angles:
    gains = np.zeros(N_CHANNELS)

    spk1, spk2 = find_speaker_pair(source_angle)
    g1, g2 = tangent_law_gains(source_angle, spk1["angle"], spk2["angle"])

    gains[spk1["index"]] = g1
    gains[spk2["index"]] = g2
    # LFE (index 3) stays at 0 always

    print(f"{source_angle:>7}°  "
          f"{gains[0]:>8.4f} {gains[1]:>8.4f} {gains[2]:>8.4f} "
          f"{gains[3]:>6.4f} {gains[4]:>10.4f} {gains[5]:>10.4f}  "
          f"{spk1['name']} + {spk2['name']}")

    # Build 6-channel frame: each channel is mono * its gain
    segment = np.column_stack([mono * gains[ch] for ch in range(N_CHANNELS)])
    all_segments.append(segment)

# We stack all four segments into one long array
multichannel = np.vstack(all_segments)

# Then we write the 6-channel WAV file, converting back to 16-bit integers
multichannel_int16 = (multichannel * 32767).astype(np.int16)

with wave.open(OUTPUT_FILE, 'w') as f:
    f.setnchannels(N_CHANNELS)
    f.setsampwidth(2)
    f.setframerate(sample_rate)
    f.writeframes(multichannel_int16.tobytes())

print(f"\nWrote {OUTPUT_FILE}  ({multichannel_int16.shape[0] / sample_rate:.1f} s, {N_CHANNELS} channels)")