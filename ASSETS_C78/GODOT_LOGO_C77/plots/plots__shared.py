"""Render the studio's four signal plots from a deterministic synthetic sample."""
from math import cos, exp, floor, log10, sin, sqrt, tau
from pathlib import Path
from random import Random
import struct
import sys
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


DAY_BACKGROUND = (250, 248, 241)
DAY_CLEAN_HEATMAP = (
    (0.00, DAY_BACKGROUND),
    (0.35, (205, 230, 222)),
    (0.65, (88, 163, 153)),
    (1.00, (12, 67, 70)),
)
DAY_NOISY_HEATMAP = (
    (0.00, DAY_BACKGROUND),
    (0.25, (235, 223, 235)),
    (0.50, (192, 143, 190)),
    (0.75, (148, 73, 142)),
    (1.00, (69, 26, 83)),
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


def render(path, pixel, grid=True, day=False):
    def canvas(x, y):
        if x in (LEFT, RIGHT) and TOP <= y <= BOTTOM or y in (TOP, BOTTOM) and LEFT <= x <= RIGHT:
            return (189, 207, 199) if day else (49, 85, 93)
        if LEFT < x < RIGHT and TOP < y < BOTTOM:
            rgb = pixel(x, y)
            grid_color = (165, 189, 179) if day else (105, 147, 147)
            return mix(rgb, grid_color, 0.22) if grid and (x in GRID_X or y in GRID_Y) else rgb
        return DAY_BACKGROUND if day else (7, 17, 23)

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


def render_logo_signals(out, suffix, day, noisy_samples, noisy_heatmap):
    middle = (TOP + BOTTOM) / 2
    height = BOTTOM - TOP
    width = RIGHT - LEFT
    peak = max(map(abs, noisy_samples))
    points = 47
    stride = len(noisy_samples) // points
    amplitudes = [
        max(noisy_samples[start : start + stride], key=abs) / peak
        for start in range(0, points * stride, stride)
    ]
    dirty_y = [middle - 0.36 * height * amplitude for amplitude in amplitudes]
    clean_ink, noisy_ink = ((12, 72, 75), (84, 20, 61)) if day else ((176, 255, 245), (255, 222, 137))
    clean_edge, noisy_edge = ((249, 254, 249), (255, 246, 236)) if day else ((10, 49, 56), (36, 12, 40))
    noisy_palette = DAY_NOISY_HEATMAP if day else CHAMBER_HEATMAP
    background = DAY_BACKGROUND if day else (8, 12, 28)

    def stroke(back, distance, edge, ink):
        halo = max(0.0, min(1.0, (8.0 - distance) / 2.0))
        core = max(0.0, min(1.0, (4.4 - distance) / 1.4))
        return mix(mix(back, edge, halo), ink, core)

    def clean_signal(x, y):
        # The idealized sine is a single narrow band in the background.
        band = exp(-((y - (TOP + 0.75 * height)) / 8.5) ** 2)
        base = DAY_BACKGROUND if day else (7, 18, 24)
        signal_band = (112, 183, 167) if day else (27, 112, 100)
        back = mix(base, signal_band, 0.53 * band)
        trace_y = middle - 0.24 * height * sin(tau * 2.75 * (x - LEFT) / width)
        return stroke(back, abs(y - trace_y), clean_edge, clean_ink)

    def noisy_signal(x, y):
        position = (x - LEFT) * (len(dirty_y) - 1) / width
        i = min(len(dirty_y) - 2, floor(position))
        trace_y = interpolate(dirty_y, position)
        slope = (dirty_y[i + 1] - dirty_y[i]) * (len(dirty_y) - 1) / width
        distance = abs(y - trace_y) / sqrt(1 + slope * slope)
        frame = min(FRAMES - 1, (x - LEFT) * FRAMES // width)
        frequency = ((BOTTOM - y) / height) ** 1.55 * (BINS - 1)
        back = mix(background, color(interpolate(noisy_heatmap[frame], frequency), noisy_palette), 0.65)
        return stroke(back, distance, noisy_edge, noisy_ink)

    render(out / f"clean-signal{suffix}.png", clean_signal, day=day)
    render(out / f"noisy-signal{suffix}.png", noisy_signal, day=day)


def main(day=False):
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
        if day:
            return mix(mix(DAY_BACKGROUND, (126, 188, 176), glow), (12, 72, 75), core)
        return mix(mix((5, 24, 29), (15, 139, 145), glow), (178, 255, 248), core)

    suffix = "-day" if day else ""
    if not day:
        render(out / "clean-wave.png", wave, grid=False)

    for name, matrix, average in zip(("clean", "noisy"), frames, averages):
        trace = [level(power, spectrum_reference) for power in average]
        heatmap = [[level(power, spectrogram_reference) for power in row] for row in matrix]
        palette = (DAY_CLEAN_HEATMAP if name == "clean" else DAY_NOISY_HEATMAP) if day else (CLEAN_HEATMAP if name == "clean" else CHAMBER_HEATMAP)

        def spectrum(x, y):
            bin_step = (BINS - 1) / (RIGHT - LEFT)
            heights = [interpolate(trace, (x + dx - LEFT) * bin_step) for dx in (-0.5, 0.5)]
            height = sum(heights) / 2
            upper = BOTTOM - max(heights) * (BOTTOM - TOP)
            lower = BOTTOM - min(heights) * (BOTTOM - TOP)
            if upper - 0.85 <= y <= lower + 0.85:
                if day:
                    return (12, 72, 75) if name == "clean" else (91, 38, 105)
                return color(0.64 + 0.28 * height)
            if y > lower:
                if day:
                    return mix(DAY_BACKGROUND, (80, 159, 147) if name == "clean" else (168, 103, 161), 0.28)
                return mix(PALETTE[0][1], color(0.56 + 0.10 * height), 0.39)
            return DAY_BACKGROUND if day else PALETTE[0][1]

        def spectrogram(x, y):
            frame = min(FRAMES - 1, (x - LEFT) * FRAMES // (RIGHT - LEFT))
            relative_height = (BOTTOM - y) / (BOTTOM - TOP)
            bin_index = relative_height ** 1.55 * (BINS - 1)
            return color(interpolate(heatmap[frame], bin_index), palette)

        render(out / f"{name}-spectrum{suffix}.png", spectrum, day=day)
        render(out / f"{name}-spectrogram{suffix}.png", spectrogram, day=day)

    noisy_heatmap = [[level(power, spectrogram_reference) for power in row] for row in frames[1]]
    render_logo_signals(out, suffix, day, noisy, noisy_heatmap)


if __name__ == "__main__":
    main(day="--day" in sys.argv[1:])
