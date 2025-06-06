from pxr import UsdShade, Sdf

class MaterialLibrary:
    """Defines reusable materials using UsdPreviewSurface, MaterialX, or RenderMan (PxrSurface)."""

    def __init__(self, stage):
        self.stage = stage
        self.root_path = "/Materials"
        UsdShade.Material.Define(self.stage, self.root_path)

    # -------------------
    # UsdPreviewSurface Materials
    # -------------------

    def create_car_paint(self, name, color=(0.1, 0.2, 0.8)):
        return self._create_material(
            name,
            params={
                "diffuseColor": color,
                "metallic": 1.0,
                "roughness": 0.2,
                "clearcoat": 0.5,
                "clearcoatRoughness": 0.1,
            }
        )

    def create_glass(self, name, color=(0.9, 0.9, 0.9), roughness=0.01, ior=1.5):
        return self._create_material(
            name,
            params={
                "diffuseColor": color,
                "opacity": 0.2,
                "ior": ior,
                "roughness": roughness,
            }
        )

    def create_plastic(self, name, color=(0.8, 0.2, 0.2), roughness=0.3):
        return self._create_material(
            name,
            params={
                "diffuseColor": color,
                "metallic": 0.0,
                "roughness": roughness,
                "specular": 0.5,
            }
        )

    def create_wood(self, name, base_color=(0.4, 0.2, 0.1), roughness=0.7):
        return self._create_material(
            name,
            params={
                "diffuseColor": base_color,
                "metallic": 0.0,
                "roughness": roughness,
                "specular": 0.5,
            }
        )

    # -------------------
    # RenderMan (PxrSurface) Materials
    # -------------------

    def create_renderman_metal(self, name, diffuse=(0.1, 0.1, 0.1), specular_edge=(1.0, 1.0, 1.0), roughness=0.1):
        return self._create_material(
            name,
            shader_id="PxrSurface",
            params={
                "diffuseColor": diffuse,
                "specularFaceColor": specular_edge,
                "specularEdgeColor": specular_edge,
                "specularRoughness": roughness,
                "presence": 1.0
            }
        )

    def create_renderman_glass(self, name, glass_color=(0.7, 0.8, 1.0), roughness=0.02):
        return self._create_material(
            name,
            shader_id="PxrSurface",
            params={
                "glassColor": glass_color,
                "specularModelType": 1,  # Beckmann
                "refractiveIndex": 1.5,
                "specularRoughness": roughness,
                "presence": 1.0
            }
        )

    # -------------------
    # MaterialX Integration
    # -------------------

    def create_materialx_reference(self, name, mtlx_path):
        """
        Create a MaterialX-based material and bind it to a UsdShade.Material.

        Args:
            name (str): Name to use in the USD stage
            mtlx_path (str): File path to the MaterialX (.mtlx) file

        Returns:
            str: USD path to the material (e.g. /Materials/MyMtlxMat)
        """
        material_path = f"{self.root_path}/{name}"
        shader_path = f"{material_path}/Shader"

        material = UsdShade.Material.Define(self.stage, material_path)
        shader = UsdShade.Shader.Define(self.stage, shader_path)
        shader.CreateIdAttr("MaterialX")
        shader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(mtlx_path)
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        return material_path

    # -------------------
    # Internal Helpers
    # -------------------

    def _create_material(self, name, params, shader_id="UsdPreviewSurface"):
        """
        Generic material creation using any shader ID (e.g., UsdPreviewSurface, PxrSurface).

        Args:
            name (str): Material name
            params (dict): Shader parameters
            shader_id (str): Shader type ID

        Returns:
            str: USD path to the created material
        """
        material_path = f"{self.root_path}/{name}"
        shader_path = f"{material_path}/Shader"

        material = UsdShade.Material.Define(self.stage, material_path)
        shader = UsdShade.Shader.Define(self.stage, shader_path)
        shader.CreateIdAttr(shader_id)

        for param, value in params.items():
            input_type = self._get_type(value)
            shader.CreateInput(param, input_type).Set(value)

        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        return material_path

    def _get_type(self, value):
        """Infer Sdf type name from Python value."""
        if isinstance(value, float):
            return Sdf.ValueTypeNames.Float
        if isinstance(value, int):
            return Sdf.ValueTypeNames.Int
        if isinstance(value, tuple) and len(value) == 3:
            return Sdf.ValueTypeNames.Color3f
        if isinstance(value, str):
            return Sdf.ValueTypeNames.Token
        raise TypeError(f"Unsupported shader input type: {value}")
