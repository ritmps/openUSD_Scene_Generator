from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdLux
import math


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
        UsdGeom.SetStageMetersPerUnit(self.stage, 0.01)

        # Create and set default prim at /World
        self.world = UsdGeom.Xform.Define(self.stage, "/World")
        self.stage.SetDefaultPrim(self.world.GetPrim())

    def add_sphere(self, path, radius=1.0, material=None):
        """
        Add a sphere primitive to the scene

        Args:
            path (str): USD path for the new sphere
            radius (float): Sphere radius
            material (str, optional): Path to material to assign

        Returns:
            UsdGeom.Sphere: Created sphere prim.
        """
        sphere = UsdGeom.Sphere.Define(self.stage, path)
        sphere.CreateRadiusAttr().Set(radius)
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

        plane = UsdGeom.Mesh.Define(self.stage, path)
        plane.GetPointsAttr().Set(points)
        plane.GetFaceVertexIndicesAttr().Set(indices)
        plane.GetFaceVertexCountsAttr().Set([3] * len(indices))

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

    def add_camera(self, path, position=(0, 5, 15), target=None, focal_length=35):
        """
        Add a camera to the scene with optional look-at target

        Args:
            path (str): USD path for the new camera.
            position (tuple): (x,y,z) camera position
            target (tuple, optional): (x,y,z) target point to look at
            focal_length (float): Camera lens focal length in mm

        Returns:
            UsdGeom.Camera: Created camera prim
        """
        camera = UsdGeom.Camera.Define(self.stage, path)

        camera.CreateProjectionAttr().Set(UsdGeom.Tokens.perspective)
        camera.CreateFocalLengthAttr().Set(focal_length)
        camera.CreateClippingRangeAttr().Set((0.1, 100000))
        if target:
            self._make_camera_look_at(camera, position, target)
        return camera

    def _make_camera_look_at(self, camera, camera_pos, target_pos):
        """
        Orient camera to look at a target point using Euler angles

        Args:
            camera (UsdGeom.Camera): Camera prim to orient
            camera_pos (tuple): Current camera position (x,y,z)
            target_pos (tuple): Target position to look at (x,y,z)
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
