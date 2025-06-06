from pxr import UsdLux, Gf, UsdGeom

# -----------------------------------------------------------------------------
# Environment Dome Lighting
# -----------------------------------------------------------------------------

class Environment:
    """Manages environment lighting such as dome lights with HDRI textures."""

    def __init__(self, stage, root_path="/Environment"):
        self.stage = stage
        self.root_path = root_path

    def add_dome_light(self, name="DomeLight", hdri_path=None, intensity=1.0, rotation_y=0.0):
        """
        Add a dome light for environment lighting.

        Args:
            name (str): Name of the dome light prim.
            hdri_path (str): Path to the HDRI texture file.
            intensity (float): Light intensity multiplier.
            rotation_y (float): Y-axis rotation of the dome.

        Returns:
            UsdLux.DomeLight
        """
        path = f"{self.root_path}/{name}"
        dome = UsdLux.DomeLight.Define(self.stage, path)
        if hdri_path:
            dome.CreateTextureFileAttr(hdri_path)
        dome.CreateIntensityAttr(intensity)

        if rotation_y != 0.0:
            dome.AddRotateYOp().Set(rotation_y)

        return dome

# -----------------------------------------------------------------------------
# Direct Lights Manager (Area, Sphere, Disk, Distant, etc.)
# -----------------------------------------------------------------------------

class LightManager:
    """Manages creation and configuration of scene lights (excluding dome/environment)."""

    def __init__(self, stage, root_path="/World/Lights"):
        self.stage = stage
        self.root_path = root_path

    def add_rect_light(self, name="RectLight", intensity=10, color=(1.0, 1.0, 1.0),
                       width=5.0, height=5.0, position=(0, 5, -5), rotation=(0, 45, -45),
                       shaping=None, shadows=None):
        light = UsdLux.RectLight.Define(self.stage, f"{self.root_path}/{name}")
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        light.CreateWidthAttr(width)
        light.CreateHeightAttr(height)
        light.AddTransformOp().Set(self._build_transform(position, rotation))
        self._apply_shaping(light, shaping)
        self._apply_shadows(light, shadows)
        return light

    def add_sphere_light(self, name="SphereLight", intensity=100, radius=1.0,
                         color=(1.0, 1.0, 1.0), position=(0, 5, 0), rotation=(0, 0, 0),
                         shaping=None, shadows=None):
        light = UsdLux.SphereLight.Define(self.stage, f"{self.root_path}/{name}")
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        light.CreateRadiusAttr(radius)
        light.AddTransformOp().Set(self._build_transform(position, rotation))
        self._apply_shaping(light, shaping)
        self._apply_shadows(light, shadows)
        return light

    def add_disk_light(self, name="DiskLight", intensity=50, radius=1.0,
                       color=(1.0, 1.0, 1.0), position=(0, 5, 0), rotation=(90, 0, 0),
                       shaping=None, shadows=None):
        light = UsdLux.DiskLight.Define(self.stage, f"{self.root_path}/{name}")
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        light.CreateRadiusAttr(radius)
        light.AddTransformOp().Set(self._build_transform(position, rotation))
        self._apply_shaping(light, shaping)
        self._apply_shadows(light, shadows)
        return light

    def add_distant_light(self, name="DistantLight", intensity=3000, angle=0.53,
                          color=(1.0, 1.0, 1.0), rotation=(45, -45, 0),
                          shaping=None, shadows=None):
        light = UsdLux.DistantLight.Define(self.stage, f"{self.root_path}/{name}")
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        light.CreateAngleAttr(angle)
        light.AddTransformOp().Set(self._build_transform((0, 0, 0), rotation))
        self._apply_shaping(light, shaping)
        self._apply_shadows(light, shadows)
        return light

    def add_cylinder_light(self, name="CylinderLight", intensity=60, radius=0.5, length=5.0,
                           color=(1.0, 1.0, 1.0), position=(0, 5, 0), rotation=(0, 0, 0),
                           shaping=None, shadows=None):
        light = UsdLux.CylinderLight.Define(self.stage, f"{self.root_path}/{name}")
        light.CreateIntensityAttr(intensity)
        light.CreateColorAttr(color)
        light.CreateRadiusAttr(radius)
        light.CreateLengthAttr(length)
        light.AddTransformOp().Set(self._build_transform(position, rotation))
        self._apply_shaping(light, shaping)
        self._apply_shadows(light, shadows)
        return light

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    def _build_transform(self, translation, rotation):
        t = Gf.Matrix4d().SetTranslate(Gf.Vec3d(*translation))
        rx = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), rotation[0]))
        ry = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(0, 1, 0), rotation[1]))
        rz = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(0, 0, 1), rotation[2]))
        return rz * ry * rx * t

    def _apply_shaping(self, light, shaping):
        if shaping:
            shaping_api = UsdLux.ShapingAPI.Apply(light)
            if "coneAngle" in shaping:
                shaping_api.CreateShapingConeAngleAttr().Set(shaping["coneAngle"])
            if "focus" in shaping:
                shaping_api.CreateShapingConeSoftnessAttr().Set(shaping["focus"])

    def _apply_shadows(self, light, shadows):
        if shadows:
            shadow_api = UsdLux.ShadowAPI.Apply(light)
            if "enable" in shadows:
                shadow_api.CreateShadowEnableAttr().Set(shadows["enable"])
            if "color" in shadows:
                shadow_api.CreateShadowColorAttr().Set(Gf.Vec3f(*shadows["color"]))
            if "distance" in shadows:
                shadow_api.CreateShadowDistanceAttr().Set(shadows["distance"])
