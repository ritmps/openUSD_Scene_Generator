from pxr import Usd, UsdGeom, UsdShade, Gf

class SceneBuilder:
    """ Main class for building openUSD scenes. """

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
        UsdGeom.SetStageMetersPerUnit(self.stage, 0.01) # centimeter scale

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
    
    def add_cube(self, path, size=1.0, material=None, position=(0, 0, 0)):
        """
        Add a cube primitive to the scene

        Args:
            path (str): USD path for the new cube
            size (float): Length of each edge
            material (str, optional): Path to material to assign
            position (tuple): XYZ coordinates

        Returns:
            UsdGeom.Cube: Created cube prim.
        """
        cube = UsdGeom.Cube.Define(self.stage, path)
        cube.CreateSizeAttr().Set(size)
        UsdGeom.XformCommonAPI(cube).SetTranslate(position)
        if material:
            self._assign_material(cube, material)
        return cube
    
    def add_plane(self, path, size=10.0, material=None, position=(0, 0, 0)):
        """
        Add a rectangular plane (as a mesh) to the scene

        Args:
            path (str): USD path for the new plane
            size (float): Length of each side
            material (str, optional): Path to material to assign
            position (tuple): XYZ coordinates

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
        UsdGeom.XformCommonAPI(plane).SetTranslate(position)

        if material:
            self._assign_material(plane, material)
        return plane
    
    def add_external_asset(self, path, asset_path, position=(0, 0, 0), reference=True, material=None):
        """
        Mount an external USD asset into the scene using reference or payload.

        Args:
            path (str): Path to mount in stage (e.g., /World/Chair)
            asset_path (str): Path to external .usd file
            position (tuple): Translation
            reference (bool): Use reference (True) or payload (False)
            material (str, optional): Path to a UsdShade.Material to bind to the external asset
        """
        prim = self.stage.DefinePrim(path, "Xform")
        if reference:
            prim.GetReferences().AddReference(asset_path)
        else:
            prim.SetPayload(asset_path)
        UsdGeom.XformCommonAPI(prim).SetTranslate(position)
        # Optionally bind material
        if material:
            self._assign_material(prim, material)
            
        return prim


    def _assign_material(self, prim, material_path):
        """
        Internal method to assign a material to a prim.

        Args:
            prim (Usd.Prim): Primitive to assign material to
            material_path (str): Path to material in the stage
        """
        material = UsdShade.Material.Get(self.stage, material_path)
        UsdShade.MaterialBindingAPI.Apply(prim.GetPrim()).Bind(material)

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
    
    def print_stage(self):
        """
        Print the USD file in ASCII format.
        """
        print(self.stage.ExportToString())

    def get_stage(self):
        """Return the current stage object (for access by other modules)."""
        return self.stage
