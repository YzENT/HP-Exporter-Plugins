# NFSHPR Exporter Plugins

This plugin is made to ease the process of exporting models for the game Need for Speed™ Hot Pursuit Remastered


### Prerequisites

- [Blender (v3.6)](https://www.blender.org/download/releases/3-6/)

### Installation

Head to `Edit > Preferences > Addons > Install` and install the zip file under releases without unzipping.

### Functions

- Vehicle
	- Preparing Collection
		- This creates a scene collection for the vehicle you wish to export for, while importing all the default textures used in `VEHICLETEX.BIN`.
		
    - Assigning empties
    	- This assigns the required transformation for the empties for each available mesh in the scene. Note that only the selected meshes will be assigned a parent.

	- Material Template
		- This is a collection of material templates with pre-tuned values to assign materials easier. Image nodes under shader editor will be created for each material depending on what type of textures they use. Please refer to `Extras\Basic Vehicle Shader Documentation.pdf` to check what each layer of UV each texture is on.

	- `Badge` - Material for vehicle badges, which supports transparency (DXT5).
	- `Glass` - Material for vehicle glass, mostly used for headlights or any other irrelevant glasses.
	- `GlassRed` - Material for taillight glass, which is red in colour.
	- `GlassLivery` - Material for glass that should include livery editing, mostly used on windshields and side windows.
	- `GlassSurround` - Material for glass that supports livery editing too, mainly used on sides of windshield as they generate a darker colour.
	- `Grille` - Material for grille of vehicles, which supports transparency (DXT5).
	- `Interior` - Material for interior, does not support transparency (DXT1).
	- `InteriorEmissive` - Material for interior dashboards, mainly used to light up the dashboard when headlights are toggled.
	- `Lights` - Material for lights.
	- `MetalChrome` - Material for chrome looking meshes.
	- `MetalColorable` - Material for vehicle paint, which supports livery editing.
	- `MetalHalfLivery` - Material for vehicle that should have a layer of wrap on top of it, transparency areas would be the vehicle paint.
	- `MetalLiveryCarbon` - Material for carbon fiber.
	- `MetalLiveryGloss` - Material for gloss looking diffuse.
	- `MetalLiveryMatte` - Material for matte looking diffuse.
	- `MetalSecondaryColouredLivery` - Material for vehicles that have secondary colour settings (Viper ACR, Ford GT, etc..), which also supports livery editing.
	- `OpaqueDULL` - Material for dull looking diffuse.
	- `PlasticBlack` - Material for black looking meshes.
	- `Mirror` - Material for side mirrors.
	- `PlateRacer/PlateCop` - Material for license plate
	- `Interior_Badge` - Material for interior with badges, which supports transparency (DXT5).

## Special Thanks

Special thanks to ModularCV for providing the initial template for `Livery UV Template.png` and material settings.
