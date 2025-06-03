from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdLux, UsdRender
import math
import pathlib


class SceneBuilder:
    """Main class for building USD scenes, handling geometry, cameras, and environment lighting"""

    def __init__(self, stage_path=None):
        """
        Initialize a new USD stage

        Args:
            stage_path (str, optional): Path to save USD file. If None, creates in-memory stage.
        """
        # Create new stage (either on disk or in memory)
        if stage_path:
            self.stage = Usd.Stage.CreateNew(stage_path)
        else:
            self.stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.y)
        UsdGeom.SetStageMetersPerUnit(self.stage, 0.01) # centimeter

        # Create and set default prim at /World
        self.world = UsdGeom.Xform.Define(self.stage, "/World")
        self.stage.SetDefaultPrim(self.world.GetPrim())

    def add_sphere(self, path, radius=1.0, material=None, position=(0, 0, 0)):
        """
        Add a sphere primitive to the scene

        Args:
            path (str): USD path for the new sphere
            radius (float): Sphere radius
            material (str, optional): Path to material to assign
            position (tuple): XYZ position of the sphere

        Returns:
            UsdGeom.Sphere: Created sphere prim.
        """
        sphere = UsdGeom.Sphere.Define(self.stage, path)
        sphere.CreateRadiusAttr().Set(radius)
        UsdGeom.XformCommonAPI(sphere).SetTranslate(position)
        if material:
            self._assign_material(sphere, material)
        return sphere

    def add_cube(self, path, size=1.0, material=None):
        """
        Add a cube primitive to the scene

        Args:
            path (str): USD path for the new cube
            size (float): Length of each edge
            material (str, optional): Path to material to assign

        Returns:
            UsdGeom.Sphere: Created cube prim.
        """
        cube = UsdGeom.Cube.Define(self.stage, path)
        cube.CreateSizeAttr().Set(size)
        if material:
            self._assign_material(cube, material)
        return cube

    def add_plane(self, path, size=10.0, material=None):
        """
        Add a rectangular plane (as a mesh) to the scene

        Args:
            path (str): USD path for the new plane
            size (float): Length of each side
            material (str, optional): Path to material to assign

        Returns:
            UsdGeom.mesh: Created plane mesh
        """
        # Define vertices for a quad mesh
        points = [
            (-size, 0, -size),
            (size, 0, -size),
            (size, 0, size),
            (-size, 0, size),
        ]

        # Triangle indices (2 triangles forming a quad)
        indices = [0, 1, 2, 0, 2, 3]
        face_vertex_counts = [3, 3]  # Two triangles

        plane = UsdGeom.Mesh.Define(self.stage, path)
        plane.GetPointsAttr().Set(points)
        plane.GetFaceVertexIndicesAttr().Set(indices)
        plane.GetFaceVertexCountsAttr().Set(face_vertex_counts)

        if material:
            self._assign_material(plane, material)
        return plane

    def _assign_material(self, prim, material_path):
        """
        Internal method to assign a material to a prim.

        Args:
            prim (Usd.Prim): Primitive to assign material to
            material_path (str): Path to material in the stage
        """
        material = UsdShade.Material.Get(self.stage, material_path)
        UsdShade.MaterialBindingAPI.Apply(prim.GetPrim()).Bind(material)
    
    def print_stage(self):
        """
        Print the USD file in ASCII format.
        """
        print(self.stage.ExportToString())

    def save(self, path=None):
        """
        Save the USD stage to disk

        Args:
            path (str, optional): File path to save to. If None, saves existing file.
        """
        if path:
            self.stage.GetRootLayer().Export(path)
            print(f"Stage exported to {path}")
        else:
            self.stage.GetRootLayer().Save()
            print("Stage saved in place.")


class MaterialLibrary:
    """Class for creating and managing USD materials"""

    def __init__(self, stage):
        """
        Initialize material library

        Args:
            stage (Usd.Stage): USD stage to create materials in
        """
        self.stage = stage

    def create_car_paint(self, name, color=(0.1, 0.2, 0.8)):
        """
        Create a car paint material with metallic flake appearance

        Args:
            name (str): Name for the new material
            color (tuple): Base color (RGB 0-1)

        Returns:
            str: Path to created material
        """
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")

        # Create shader using UsdPreviewSurface
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")

        # Set material properties for car paint
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(1.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.2)
        shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(0.5)
        shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.1)

        # Connect shader to material output
        material.CreateSurfaceOutput().ConnectToSource(
            shader.ConnectableAPI(), "surface"
        )
        return f"/Materials/{name}"

    def create_glass(self, name, color=(0.9, 0.9, 0.9), roughness=0.01, ior=1.5):
        """
        Create a glass material

        Args:
            name (str): Name for the new material
            color (tuple): Glass tint color (RGB 0-1)
            roughness (float): Surface roughness (0-1)
            ior (float): Index of refraction

        Returns:
            str: Path to created material
        """
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(0.2)
        shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(ior)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        material.CreateSurfaceOutput().ConnectToSource(
            shader.ConnectableAPI(), "surface"
        )
        return f"/Materials/{name}"

    def create_plastic(self, name, color=(0.8, 0.2, 0.2), roughness=0.3):
        """
        Create a plastic material

        Args:
            name (str): Name for the new material
            color (tuple): Plastic color (RGB 0-1)
            roughness (float): Surface roughness (0-1)

        Returns:
            str: Path to created material
        """
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        shader.CreateInput("specular", Sdf.ValueTypeNames.Float).Set(0.5)
        material.CreateSurfaceOutput().ConnectToSource(
            shader.ConnectableAPI(), "surface"
        )
        return f"/Materials/{name}"

    def create_wood(self, name, base_color=(0.4, 0.2, 0.1), roughness=0.7):
        """
        Create a wood material

        Args:
            name (str): Name for the new material
            base_color (tuple): Wood base color (RGB 0-1)
            roughness (float): Surface roughness (0-1)

        Returns:
            str: Path to created material
        """
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(base_color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        shader.CreateInput("specular", Sdf.ValueTypeNames.Float).Set(0.5)
        material.CreateSurfaceOutput().ConnectToSource(
            shader.ConnectableAPI(), "surface"
        )
        return f"/Materials/{name}"


class Environment:
    """Class for managing scene environment and lighting"""

    def __init__(self, stage):
        """
        Initialize environment system

        Args:
            stage (Usd.Stage): USD stage to add lighting to
        """
        self.stage = stage

    def set_hdri_lighting(self, hdri_path, intensity=1.0):
        """
        Set up HDRI environment lighting

        Args:
            hdri_path (str): Path to HDRI image file
            intensity (float): Light intensity multiplier

        Returns:
            UsdLux.DomeLight: Created dome light
        """
        dome_light = UsdLux.DomeLight.Define(self.stage, "/Environment/Light")
        dome_light.CreateTextureFileAttr(hdri_path)
        dome_light.CreateIntensityAttr(intensity)
        return dome_light

class LightManager:
    """Class for adding lights to the USD scene."""

    def __init__(self, stage):
        """
        Initialize the LightManager with a USD stage.
        
        Args:
            stage (Usd.Stage): The USD stage to operate on.
        """
        self.stage = stage

    def add_area_light(self, path="/World/AreaLight", intensity=5, color=(1.0, 1.0, 1.0), width=5.0, height=5.0, position=(0, 5, -5), rotation=(0, 45, -45)):
        """
        Add a rectangle area light to the scene.

        Args:
            path (str): USD path for the light prim.
            intensity (float): Light intensity.
            color (tuple): RGB color.
            width (float): Width of the light source.
            height (float): Height of the light source.
            position (tuple): XYZ position of the light.
            rotation (tuple): XYZ rotation angles in degrees.

        Returns:
            UsdLux.RectLight: The created area light prim.
        """
        light = UsdLux.RectLight.Define(self.stage, path)
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        light.CreateWidthAttr(width)
        light.CreateHeightAttr(height)

        # Build transformation matrix
        translate_mat = Gf.Matrix4d().SetTranslate(Gf.Vec3d(*position))
        rot_x = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), rotation[0]))
        rot_y = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(0, 1, 0), rotation[1]))
        rot_z = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(0, 0, 1), rotation[2]))

        final_transform = rot_z * rot_y * rot_x * translate_mat  # Rz * Ry * Rx * T

        xform = light.AddTransformOp()
        xform.Set(final_transform)

        return light
        
    def add_distant_light(self, path="/World/DistantLight", intensity=1000, color=(1.0, 1.0, 1.0)):
        """
        Add a distant light (like the sun) to the scene.

        Args:
            path (str): USD path for the light prim.
            intensity (float): Light intensity.
            color (tuple): RGB color.

        Returns:
            UsdLux.DistantLight: The created light prim.
        """
        light = UsdLux.DistantLight.Define(self.stage, path)
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        return light

class Camera:
    """Class for managing camera creation and editing in USD scenes."""

    def __init__(self, stage):
        """
        Initialize the Camera system with a USD stage.

        Args:
            stage (Usd.Stage): USD stage to add cameras to.
        """
        self.stage = stage
    
    def add_camera(self, path, position = (0, 5, 15), target=None, focal_length=35):
        """
        Add a camera to the scene with optional look-at target.

        Args:
            path (str): USD path for the new camera.
            position (tuple): (x, y, z) camera position.
            target (tuple, optional): (x, y, z) target point to look at.
            focal_length (float): Camera lens focal length in mm.

        Returns:
            UsdGeom.Camera: Created camera prim.
        """
        camera = UsdGeom.Camera.Define(self.stage, path)
        camera.CreateProjectionAttr().Set(UsdGeom.Tokens.perspective)
        camera.CreateFocalLengthAttr().Set(focal_length)
        camera.CreateClippingRangeAttr().Set((0.1, 100000))

        if target:
            self._make_camera_look_at(camera, position, target)
        else:
            camera.AddTranslateOp().Set(Gf.Vec3d(*position))

        return camera

    def  _make_camera_look_at(self, camera, camera_pos, target_pos):
        """
        Orient camera to look at a target point using Euler angles.

        Args:
            camera (UsdGeom.Camera): Camera prim to orient.
            camera_pos (tuple): Current camera position (x, y, z).
            target_pos (tuple): Target position to look at (x, y, z).
        """
        camera_pos = Gf.Vec3d(*camera_pos)
        target_pos = Gf.Vec3d(*target_pos)

        # Calculate direction vector and normalize
        direction = (target_pos - camera_pos).GetNormalized()

        # Convert direction to yaw (around Y) and pitch (around X) angles
        yaw = math.degrees(math.atan2(-direction[0], -direction[2]))
        pitch = math.degrees(math.asin(direction[1]))

        # Apply transforms to camera
        camera.AddTranslateOp().Set(camera_pos)
        camera.AddRotateYOp().Set(yaw)
        camera.AddRotateXOp().Set(pitch)

class RenderSettingsManager:
    """Class to manage RenderSettings, RenderProducts, and RenderVars."""

    def __init__(self, stage, render_scope="/Render"):
        """
        Initialize the render settings manager.

        Args:
            stage (Usd.Stage): The USD stage to operate on.
            render_scope (str): Path under which to organize render-related prims.
        """
        self.stage = stage
        self.render_scope = render_scope

        # Create a Scope to group all rendering-related prims under /Render
        UsdGeom.Scope.Define(stage, render_scope)

    def create_basic_render_settings(self, settings_name, camera_path, resolution=(512, 512), products=[]):
        """
        Create a RenderSettings prim and link it to products and a camera.

        Args:
            settings_name (str): Name of the RenderSettings prim.
            camera_path (str): Path to the Camera prim to use.
            resolution (tuple): Output resolution (width, height).
            products (list): List of paths to RenderProduct prims.

        Returns:
            str: Path to the created RenderSettings prim.
        """
        settings_path = f"{self.render_scope}/{settings_name}"

        # Define the RenderSettings prim at the desired path
        settings = UsdRender.Settings.Define(self.stage, settings_path)

        self.stage.SetMetadata("renderSettingsPrimPath", settings_path)

        # Set the image resolution
        settings.CreateResolutionAttr().Set(Gf.Vec2i(*resolution))

        # Link the camera
        settings.CreateCameraRel().SetTargets([Sdf.Path(camera_path)])

        # Optionally link to output products (images, depth maps, etc.)
        if products:
            settings.CreateProductsRel().SetTargets([Sdf.Path(p) for p in products])

        return settings_path

    def create_render_product(self, name, camera_path, output_path, ordered_vars=None):
        """
        Create a RenderProduct (e.g. a color image or depth map).

        Args:
            name (str): Name of the RenderProduct prim.
            camera_path (str): Path to the camera this product uses.
            output_path (str): File path for the rendered output (e.g., "./renders/depth.exr").
            ordered_vars (list): Paths to RenderVar prims that define the output channels.

        Returns:
            str: Path to the created RenderProduct prim.
        """
        product_path = f"{self.render_scope}/{name}"
        # Define the RenderProduct prim
        product = UsdRender.Product.Define(self.stage, product_path)

        # Set the output filename (convert to POSIX style for USD compatibility)
        # product.CreateProductNameAttr().Set(str(pathlib.Path(output_path).as_posix()))
        product.CreateProductNameAttr().Set(str(pathlib.Path(output_path).resolve().as_posix()))

        # Attach the product to a camera
        product.CreateCameraRel().SetTargets([Sdf.Path(camera_path)])

        # Link to the ordered list of render variables (AOVs, LPEs, etc.)
        if ordered_vars:
            product.CreateOrderedVarsRel().SetTargets([Sdf.Path(v) for v in ordered_vars])
        return product_path

    def create_render_var(self, var_name, source_name, data_type="float", source_type=None):
        """
        Create a RenderVar to define a data output channel (like color, depth, normals).

        Args:
            var_name (str): Name of the RenderVar prim.
            source_name (str): Source token or LPE string (e.g., "Ci", "depth", or "C<RD>[<L.>O]").
            data_type (str): Data type for the output ("float", "int", etc.).
            source_type (str, optional): How to interpret source_name (e.g., "lpe").

        Returns:
            str: Path to the created RenderVar prim.
        """
        var_path = f"{self.render_scope}/Vars/{var_name}"

        # Define the RenderVar prim at the path
        var = UsdRender.Var.Define(self.stage, var_path)

        # Tell the renderer what value to output (e.g., "Ci" for color, "depth" for z-buffer)
        var.CreateSourceNameAttr().Set(source_name)

        # Specify the data type (e.g., float, int)
        var.CreateDataTypeAttr().Set(data_type)

        # Optionally specify the type of source ("lpe" for light path expression, etc.)
        if source_type:
            var.CreateSourceTypeAttr().Set(source_type)

        return var_path