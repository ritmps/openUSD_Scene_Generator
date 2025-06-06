from pxr import Usd, UsdRender, UsdGeom, Sdf, Gf
import pathlib

class RenderSettingsManager:
    """Class to manage RenderSettings, RenderProducts, and RenderVars."""

    def __init__(self, stage, render_scope="/Render"):
        self.stage = stage
        self.render_scope = render_scope
        UsdGeom.Scope.Define(stage, render_scope)

    def create_basic_render_settings(self, settings_name, camera_path, resolution=(512, 512), products=[]):
        settings_path = f"{self.render_scope}/{settings_name}"
        settings = UsdRender.Settings.Define(self.stage, settings_path)
        self.stage.SetMetadata("renderSettingsPrimPath", settings_path)
        settings.CreateResolutionAttr().Set(Gf.Vec2i(*resolution))
        settings.CreateCameraRel().SetTargets([Sdf.Path(camera_path)])
        if products:
            settings.CreateProductsRel().SetTargets([Sdf.Path(p) for p in products])
        return settings_path

    def create_render_product(self, name, camera_path, output_path, ordered_vars=None):
        product_path = f"{self.render_scope}/{name}"
        product = UsdRender.Product.Define(self.stage, product_path)
        product.CreateProductNameAttr().Set(str(pathlib.Path(output_path).resolve().as_posix()))
        product.CreateCameraRel().SetTargets([Sdf.Path(camera_path)])
        if ordered_vars:
            product.CreateOrderedVarsRel().SetTargets([Sdf.Path(v) for v in ordered_vars])
        return product_path

    def create_render_var(self, var_name, source_name, data_type="float", source_type=None):
        var_path = f"{self.render_scope}/Vars/{var_name}"
        var = UsdRender.Var.Define(self.stage, var_path)
        var.CreateSourceNameAttr().Set(source_name)
        var.CreateDataTypeAttr().Set(data_type)
        if source_type:
            var.CreateSourceTypeAttr().Set(source_type)
        return var_path
