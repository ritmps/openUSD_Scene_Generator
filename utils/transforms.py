from pxr import Gf, UsdGeom

def make_transform_matrix(position, rotation=(0, 0, 0), scale=(1, 1, 1)):
    """Create a 4x4 transformation matrix from position, rotation (XYZ degrees), and scale."""
    translate = Gf.Matrix4d().SetTranslate(Gf.Vec3d(*position))
    rot_x = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), rotation[0]))
    rot_y = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(0, 1, 0), rotation[1]))
    rot_z = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(0, 0, 1), rotation[2]))
    scale_mat = Gf.Matrix4d().SetScale(Gf.Vec3d(*scale))

    return rot_z * rot_y * rot_x * translate * scale_mat

def extract_translation(matrix):
    """Extract translation component from a Gf.Matrix4d."""
    return tuple(matrix.ExtractTranslation())

def compute_world_transform(prim):
    """Compute the world transform of a prim."""
    return UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(UsdGeom.GetStageUpAxis(prim.GetStage()))
