from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdLux
import math

class SceneBuilder:
    def __init__(self, stage_path=None):
        if stage_path:
            self.stage = Usd.Stage.CreateNew(stage_path)
        else:
            self.stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.y) # y axis up
        UsdGeom.SetStageMetersPerUnit(self.stage, 0.01) # centimeters

        # Create and set default prim at /World
        self.world = UsdGeom.Xform.Define(self.stage, "/World")
        self.stage.SetDefaultPrim(self.world.GetPrim())
    
    def add_sphere(self, path, radius=1.0, material=None):
        sphere = UsdGeom.Sphere.Define(self.stage, path)
        sphere.CreateRadiusAttr().Set(radius)
        if material:
            self._assign_material(sphere, material)
        return sphere
    
    def add_cube(self, path, size=1.0, material=None):
        cube = UsdGeom.Cube.Define(self.stage, path)
        cube.CreateSizeAttr().Set(size)
        if material:
            self._assign_material(cube, material)
        return cube
    
    def add_plane(self, path, size=10.0, material=None):
        
        points = [(-size, 0, -size), (size,0,-size),  (size,0,size),  (-size,0,size) ]
        indices = [0, 1, 2, 0, 2, 3]

        plane = UsdGeom.Mesh.Define(self.stage, path)
        plane.GetPointsAttr().Set(points)
        plane.GetFaceVertexIndicesAttr().Set(indices)
        plane.GetFaceVertexCountsAttr().Set([3] * len(indices))

        if material:
            self._assign_material(plane, material)
        return plane

    def _assign_material(self, prim, material_path):
        material = UsdShade.Material.Get(self.stage, material_path)
        UsdShade.MaterialBindingAPI.Apply(prim.GetPrim()).Bind(material)
    
    def add_camera(self, path, position=(0, 5, 15), target=None, focal_length = 35):
        camera = UsdGeom.Camera.Define(self.stage, path)
        
        camera.CreateProjectionAttr().Set(UsdGeom.Tokens.perspective)
        camera.CreateFocalLengthAttr().Set(focal_length)
        camera.CreateClippingRangeAttr().Set((0.1,100000))
        if target:
            self._make_camera_look_at(camera, position, target)
        return camera

    def _make_camera_look_at(self, camera, camera_pos, target_pos):
        """Orient to look at target point"""
        camera_pos = Gf.Vec3d(*camera_pos)
        target_pos = Gf.Vec3d(*target_pos)

        # calculate rotation to look at target
        direction = (target_pos - camera_pos).GetNormalized()
        yaw = math.degrees(math.atan2(-direction[0], -direction[2]))
        pitch = math.degrees(math.asin(direction[1]))

        camera.AddTranslateOp().Set(camera_pos)
        camera.AddRotateYOp().Set(yaw)
        camera.AddRotateXOp().Set(pitch)


    def save(self):
        self.stage.GetRootLayer().Save()
        print(f"Stage saved.")
    



class MaterialLibrary:
    def __init__(self, stage):
        self.stage = stage
    
    def create_car_paint(self, name, color=(0.1, 0.2, 0.8)):
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        # Define the shader
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.8)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.2)
        shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(1.0) 
        shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.05)
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        return f"/Materials/{name}"
    
    def create_glass(self, name, color=(0.9, 0.9, 0.9), roughness=0.01, ior=1.5):
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(0.2)
        shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(ior)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        return f"/Materials/{name}"
    
    def create_plastic(self, name, color, roughness):
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        shader.CreateInput("specular", Sdf.ValueTypeNames.Float).Set(0.5)
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        return f"/Materials/{name}"
    
    def create_wood(self, name, base_color=(0.4, 0.2, 0.1), roughness=0.7):
        material = UsdShade.Material.Define(self.stage, f"/Materials/{name}")
        shader = UsdShade.Shader.Define(self.stage, f"/Materials/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(base_color)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        shader.CreateInput("specular", Sdf.ValueTypeNames.Float).Set(0.5)
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        return f"/Materials/{name}"


class Environment:
    def __init__(self, stage):
        self.stage = stage
    
    def set_hdri_lighting(self, hdri_path, intensity=1.0):
        dome_light = UsdLux.DomeLight.Define(self.stage, "/Environment/Light")
        dome_light.CreateTextureFileAttr(hdri_path) 
        dome_light.CreateIntensityAttr(intensity)

        return dome_light