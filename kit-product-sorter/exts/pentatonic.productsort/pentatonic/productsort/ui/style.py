import omni.ui as ui
from pathlib import Path

icons_path = Path(__file__).parent.parent.parent.parent / "icons"

gen_ai_style = {
    "HStack": {
        "margin": 3
    },
    "Button.Image::create": {"image_url": f"{icons_path}/plus.svg", "color": 0xFF00B976},
    "Button.Image::properties": {"image_url": f"{icons_path}/cog.svg", "color": 0xFF989898},
    "Button.Image::remove": {"image_url": f"{icons_path}/remove.svg", "color": 0xFF989898},
    "Line": {
        "margin": 3
    },
    "Label": {
        "margin_width": 5
    }
}


guide = """
UI Controls:

1. Gear Icon:
   - Function: Saves environment variables for the application.
   - Usage: Click to save the variables.

2. 3rd Person Toggle:
   - Function: Spawns the user as a 3D person character with a controller.
   - Usage: Click to toggle between 3rd person mode on and off.

3. Isaac Sim Toggle:
   - Function: Changes default variables when running the extension in Isaac Sim.
   - Usage: Click to toggle Isaac Sim mode on and off.

4. Product Type:
   - Function: Selects the main group of products
   - Usage: Select between the types of products to creation your distribution for

5. Material Type:
   - Function: Select between random and custom.
   - Usage: If custom is selected then you are able to select which materials you wish to use for the distribution.

6. Container Type:
   - Function: Select the container type that will house the product.
   - Usage: The container will be used to calculate the fill rate based on the product dimensions.

7. Container Fill %:
   - Function: Select the container fill percentage.
   - Usage: This will calculate the amount for the products to be distrubited in the container.

8. Prompt:
   - Function: Allows the user to add additional instruction to the distrubtion generation.
   - Usage: Enter the desired prompt text.

9. 3D Character Controller UI:
   - Usage: Intended for use with the 3D Character Controller for 3rd person.

10. Apply Button:
   - Function: Adds the users prompt to the generation.
   - Usage: N/A (not functional).

11. Generate & Spawn:
   - Function: Generates the distribution payload to be used with the formulas created or with AI if a key is present.
   - Usage: N/A (not functional).

Other:

1. Add the Crosshair for Spawn Placement:
   - Press the play button and then pause to start any physics/character controller stuff in the scene.

2. Move Around the Scene:
   - In perspective camera mode, move your camera around the scene using the right mouse button to look around and the WASD keyboard controls to move.
   - Place the red circle where you want the object label to be created (this will be the spawn point for the asset when generated).

"""