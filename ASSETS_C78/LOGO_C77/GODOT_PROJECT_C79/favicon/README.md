# Anechoic Favicon

Open `project.godot` in Godot 4 to preview the compact icon. Three people stand above the pale A. The wider iceberg frames the letter, with a faint route between the air and water.

This project shares the iceberg script and shaders with the [Logo project](../logo/README.md) through relative symbolic links. Keep both projects in the same checkout with symbolic links enabled.

Use windowed Godot to render at 500 × 500, then resize to 64 × 64 with Lanczos resampling. The approved [64 × 64 PNG](../../anechoic_logo_64.png) is also at the repository root.

```sh
godot --path . --resolution 500x500 -- --render /absolute/path/anechoic_icon_render.png
```
