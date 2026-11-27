# Anechoic Logo

This Godot 4 project renders the Anechoic logo. The iceberg represents the project. Wind carries the person's ideas through the noosphere. The digital technosphere spans interfaces and models near the waterline and microelectronics at depth.

The profile camera places the waterline halfway up the image. A continuous cutaway reveals the guardrailed route just inside the ice wall. Below the waterline, a glass canopy covers the route. A single smooth line in the ice represents an idea without echoes.

The water has three layers. Loose pixel currents sit near the surface, fine circuit traces run below them, and tightly packed rows of larger pixels form the base.

Edit the iceberg profile and the spiral in `iceberg.gd`. The scene uses Avenir Next Demi Bold for the wordmark, with a system sans-serif fallback.

The [500 × 500 render](../../anechoic_logo_500.png) is the source for the [512 × 512 logo](../../anechoic_logo.png). A pale A spans the [64 × 64 icon](../../anechoic_logo_64.png), with the person standing on its apex. Both delivery sizes are also at the repository root.

Open `project.godot` and run the project. Use windowed Godot to render the full wordmark or the icon artwork. Resize the icon render to 64 × 64 after export.

```sh
godot --path . --resolution 500x500 -- --render /absolute/path/anechoic_logo_500.png
godot --path . --resolution 500x500 -- --icon --render /absolute/path/anechoic_icon_render.png
```
