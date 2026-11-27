# Anechoic Logo

This Godot 4 project renders the Anechoic logo. The iceberg represents the project. Wind carries the person's ideas through the noosphere. The water represents the digital technosphere.

The ocean swells around the midpoint of the image. A cutaway reveals three straight ramps connected by rounded turns inside the ice. Below the waterline, a glass canopy covers the route. A single smooth line in the ice represents an idea without echoes.

From the bottom up, the water shows electricity, building blocks, microcircuits, assembly, and Python and TypeScript. Individual letters ride the waves at the surface.

Edit the iceberg profile and the route in `iceberg.gd`. The scene uses Avenir Next Demi Bold for the wordmark, with a system sans-serif fallback.

The [500 × 500 render](../../anechoic_logo_500.png) is the source for the [512 × 512 logo](../../anechoic_logo.png). In the [64 × 64 icon](../../anechoic_logo_64.png), the larger person stands where the top of the pale A meets the iceberg peak. Both delivery sizes are also at the repository root.

Open `project.godot` and run the project. Use windowed Godot to render the full wordmark or the icon artwork. Resize the icon render to 64 × 64 after export.

```sh
godot --path . --resolution 500x500 -- --render /absolute/path/anechoic_logo_500.png
godot --path . --resolution 500x500 -- --icon --render /absolute/path/anechoic_icon_render.png
```
