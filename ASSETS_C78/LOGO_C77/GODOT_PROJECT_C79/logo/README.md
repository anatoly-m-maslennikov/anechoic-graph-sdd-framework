# Anechoic Logo

This Godot 4 project renders the Anechoic logo. The iceberg represents the project. Wind carries the person's ideas through the noosphere. The water represents the digital technosphere.

The ocean swells around the midpoint of the image. A cutaway reveals a curved walkway with one guardrail. The turns approach the edges of the ice. Below the waterline, a frameless glass canopy covers the route.

Tiny atoms and molecules form the bottom layer. Above them, sine waves and lightning bolts represent electricity. Then come microcircuits, assembly, C and Rust, then Python, TypeScript, and Java. Letters of different sizes form the irregular surface waves.

Edit the iceberg profile and the route in `iceberg.gd`. The scene uses Avenir Next Demi Bold for the wordmark, with a system sans-serif fallback.

The [500 × 500 render](../../anechoic_logo_500.png) is the source for the [512 × 512 logo](../../anechoic_logo.png). In the [64 × 64 icon](../../anechoic_logo_64.png), the larger person stands where the top of the pale A meets the iceberg peak. Both delivery sizes are also at the repository root.

Open `project.godot` and run the project. Use windowed Godot to render the full wordmark or the icon artwork. Resize the icon render to 64 × 64 after export.

```sh
godot --path . --resolution 500x500 -- --render /absolute/path/anechoic_logo_500.png
godot --path . --resolution 500x500 -- --icon --render /absolute/path/anechoic_icon_render.png
```
