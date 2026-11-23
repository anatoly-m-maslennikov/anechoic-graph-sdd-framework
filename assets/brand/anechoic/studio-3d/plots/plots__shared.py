"""Render the studio's four signal plots from a deterministic synthetic sample."""
from math import cos, exp, floor, log10, sin, sqrt, tau
from pathlib import Path
from random import Random
import struct
import zlib

WIDTH, HEIGHT = 400, 240
LEFT, TOP, RIGHT, BOTTOM = 15, 12, 389, 226
GRID_X = {round(LEFT + tick * (RIGHT - LEFT) / 8) for tick in range(1, 8)}
GRID_Y = {round(TOP + tick * (BOTTOM - TOP) / 6) for tick in range(1, 6)}
RATE, WINDOW, BINS, FRAMES = 9600, 384, 144, 116
FLOOR_DB = -55
PALETTE = (
    (0.00, (7, 18, 24)),
    (0.23, (10, 33, 42)),
    (0.42, (13, 76, 84)),
    (0.60, (32, 151, 146)),
    (0.76, (94, 211, 184)),
    (0.88, (242, 127, 107)),
    (1.00, (255, 207, 142)),
)
CHAMBER_HEATMAP = (
    (0.00, (8, 5, 24)),
    (0.25, (22, 8, 49)),
    (0.45, (73, 14, 99)),
    (0.60, (175, 32, 103)),
    (0.72, (243, 100, 49)),
    (0.85, (255, 174, 48)),
    (1.00, (255, 237, 136)),
)
CLEAN_HEATMAP = (
    (0.00, (7, 18, 24)),
    (0.48, (12, 58, 65)),
    (0.70, (27, 155, 158)),
    (1.00, (157, 252, 226)),
)


def mix(a, b, amount):
    return tuple(round(p + (q - p) * amount) for p, q in zip(a, b))


def color(level, palette=PALETTE):
    for (start, a), (end, b) in zip(palette, palette[1:]):
        if level <= end:
            return mix(a, b, (level - start) / (end - start))
    return palette[-1][1]


def sample():
    rng = Random(555)
    phase = 0
    clean, noisy = [], []
    for i in range(RATE * 2):
        time = i / RATE
        pitch = 126 + 22 * sin(tau * 0.87 * time) + 5 * sin(tau * 3.9 * time)
        phase += tau * pitch / RATE
        envelope = sum(
            amp * exp(-((time - center) / width) ** 4)
            for center, width, amp in ((0.34, 0.26, 0.82), (1.01, 0.22, 0.95), (1.63, 0.27, 0.79))
        )
        formant = 570 + 240 * sin(tau * 0.68 * time)
        signal = 0.22 * sin(phase)
        for h in range(2, 28):
            hz = h * pitch
            gain = (
                0.11 * exp(-((hz - formant) / 250) ** 2)
                + 0.064 * exp(-((hz - (1570 + 210 * sin(tau * 0.61 * time))) / 310) ** 2)
                + 0.022 * exp(-((hz - 2740) / 360) ** 2)
            )
            signal += gain * sin(h * phase + h * h * 0.39)
        voiced = signal * envelope * (0.9 + 0.1 * cos(tau * 7 * time))
        clean.append(voiced)
        bursts = sum(
            amp * exp(-((time - center) / width) ** 2)
            * sin(tau * (frequency * time + 130 * time * time))
            for center, width, amp, frequency in (
                (0.43, 0.035, 0.10, 1950),
                (1.18, 0.055, 0.13, 2400),
                (1.72, 0.040, 0.11, 1750),
            )
        )
        noisy.append(voiced + bursts + rng.gauss(0, 0.035))
    return clean, noisy


def power_spectra(samples):
    window = [0.5 - 0.5 * cos(tau * i / (WINDOW - 1)) for i in range(WINDOW)]
    kernels = [
        [weight * complex(cos(tau * i * k / WINDOW), -sin(tau * i * k / WINDOW))
         for i, weight in enumerate(window)]
        for k in range(1, BINS + 1)
    ]
    result = []
    for series in samples:
        frames = []
        for frame in range(FRAMES):
            start = round(frame * (len(series) - WINDOW) / (FRAMES - 1))
            segment = series[start:start + WINDOW]
            frames.append([
                abs(sum(value * weight for value, weight in zip(segment, kernel))) ** 2
                for kernel in kernels
            ])
        result.append(frames)
    return result


def level(power, reference):
    db = 10 * log10(max(power / reference, 1e-12))
    return max(0, min(1, (db - FLOOR_DB) / -FLOOR_DB))


def interpolate(values, position):
    index = floor(position)
    fraction = position - index
    return values[index] * (1 - fraction) + values[min(index + 1, len(values) - 1)] * fraction


def render(path, pixel, grid=True):
    def canvas(x, y):
        if x in (LEFT, RIGHT) and TOP <= y <= BOTTOM or y in (TOP, BOTTOM) and LEFT <= x <= RIGHT:
            return (49, 85, 93)
        if LEFT < x < RIGHT and TOP < y < BOTTOM:
            rgb = pixel(x, y)
            return mix(rgb, (105, 147, 147), 0.22) if grid and (x in GRID_X or y in GRID_Y) else rgb
        return (7, 17, 23)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    data = b"".join(
        b"\0" + bytes(component for x in range(WIDTH) for component in canvas(x, y))
        for y in range(HEIGHT)
    )
    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(data, 9)) + chunk(b"IEND", b"")
    )


def main():
    out = Path(__file__).resolve().parent
    clean, noisy = sample()
    frames = power_spectra((clean, noisy))
    averages = [[sum(column) / FRAMES for column in zip(*matrix)] for matrix in frames]
    spectrum_reference = max(map(max, averages))
    spectrogram_reference = max(max(row) for matrix in frames for row in matrix)
    assert spectrum_reference > 0 and sum(averages[1][112:]) > sum(averages[0][112:]) * 3

    def wave(x, y):
        center = (TOP + BOTTOM) / 2
        height = center - 0.23 * (BOTTOM - TOP) * sin(tau * 2.75 * (x - LEFT) / (RIGHT - LEFT))
        distance = abs(y - height)
        glow = 0.45 * exp(-(distance / 12) ** 2)
        core = exp(-(distance / 3.8) ** 4)
        return mix(mix((5, 24, 29), (15, 139, 145), glow), (178, 255, 248), core)

    render(out / "clean-wave.png", wave, grid=False)

    for name, matrix, average in zip(("clean", "noisy"), frames, averages):
        trace = [level(power, spectrum_reference) for power in average]
        heatmap = [[level(power, spectrogram_reference) for power in row] for row in matrix]
        palette = CLEAN_HEATMAP if name == "clean" else CHAMBER_HEATMAP

        def spectrum(x, y):
            bin_step = (BINS - 1) / (RIGHT - LEFT)
            heights = [interpolate(trace, (x + dx - LEFT) * bin_step) for dx in (-0.5, 0.5)]
            height = sum(heights) / 2
            upper = BOTTOM - max(heights) * (BOTTOM - TOP)
            lower = BOTTOM - min(heights) * (BOTTOM - TOP)
            if upper - 0.85 <= y <= lower + 0.85:
                return color(0.64 + 0.28 * height)
            if y > lower:
                return mix(PALETTE[0][1], color(0.56 + 0.10 * height), 0.39)
            return PALETTE[0][1]

        def spectrogram(x, y):
            frame = min(FRAMES - 1, (x - LEFT) * FRAMES // (RIGHT - LEFT))
            relative_height = (BOTTOM - y) / (BOTTOM - TOP)
            bin_index = relative_height ** 1.55 * (BINS - 1)
            return color(interpolate(heatmap[frame], bin_index), palette)

        render(out / f"{name}-spectrum.png", spectrum)
        render(out / f"{name}-spectrogram.png", spectrogram)


if __name__ == "__main__":
    main()
