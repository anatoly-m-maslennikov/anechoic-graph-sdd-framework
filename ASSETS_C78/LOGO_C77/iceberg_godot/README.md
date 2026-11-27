# Anechoic Iceberg

This separate Godot 4 project renders the medium iceberg logo. The profile camera places the waterline halfway up the image. Smooth wind trails sit above the water. Quantized signal noise fills the water around the iceberg.

Edit the iceberg profile and the spiral in `iceberg.gd`. The scene uses Avenir Next Demi Bold for the wordmark, with a system sans-serif fallback.

Open `project.godot` and run the project, or export the 500 × 500 PNG with a windowed Godot executable.

```sh
godot --path . --resolution 500x500 -- --render /absolute/path/anechoic_logo_iceberg_medium.png
```
