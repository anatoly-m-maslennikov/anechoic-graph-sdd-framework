# Anechoic Studio

The Solarpunk logo is an editable Godot 4 scene. The rooms, partition, glazing, console and instruments are modeled in the same coordinate system. Both lighting variants use the same orthographic camera.

Import `project.godot` in Godot and open `studio.tscn`. Press F6 to view it.

- Drag to orbit. Press Home to return to the logo view.
- Press D for day or N for night.
- Press 1 for frequency spectra, 2 for paired spectrograms, or 3 for the logo displays.

## Render the logo

Run these commands with a normal windowed Godot build. The logo render hides the keyboard help.

```sh
godot --path . -- --render /absolute/path/anechoic-logo-day.png
godot --path . -- --night --render /absolute/path/anechoic-logo-night.png
```

Add `--spectrum` or `--spectrogram` after `--` to export an analysis view.

The logo pairs an idealized sine wave above the window with a noisy spectrogram in the chamber. The analysis views compare the same synthetic vocal sample with and without interference. Both sides use the same scale within each analysis view. To rebuild the textures, run `python3 plots/generate.py`.

The scene tree is editable. To regenerate it from the parametric GDScript sources, run `godot --headless --path . --script res://bake_scene.gd`. This replaces `studio.tscn` with the generated scene.

The potted plant comes from Kenney’s CC0 Furniture Kit. See [asset details](market/SOURCE.md).
