# Anechoic Logo

This Godot 4 project renders the Anechoic logo. The iceberg represents the project. Three people hold hands on its narrow summit ledge. Wind carries their ideas through the noosphere. The water represents the digital technosphere.

The logo composites a generated [storm-wave texture](storm_waves.png) behind the ice. Godot places pale letter foam along its crest and renders the rest of the scene.

A cutaway reveals a curved walkway with one guardrail and a consistent deck width. The turns approach the edges of the ice. Below the waterline, a frameless glass canopy covers the route.

Tiny atoms and molecules form the bottom layer. Above them, sine waves and lightning bolts represent electricity. Then come microcircuits, assembly, C and Rust, then Python, TypeScript, and Java. Letters from six writing systems form the foam in pale colors, with different fonts, sizes, and angles.

Edit the iceberg profile and the route in `iceberg.gd`. The scene uses Avenir Next Demi Bold for the wordmark, with a system sans-serif fallback.

The [500 × 500 render](../anechoic_logo_500.png) is the source for the [512 × 512 logo](../anechoic_logo.png). The [Favicon project](../../FAVICON/GODOT_PROJECT/README.md) shares the iceberg source and opens the small icon.

Open `project.godot` and run the project. Use windowed Godot to render the full wordmark.

```sh
godot --headless --editor --path . --import
godot --path . --resolution 500x500 -- --render /absolute/path/anechoic_logo_500.png
```
