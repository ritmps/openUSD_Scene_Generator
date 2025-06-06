from pxr import Usd, UsdGeom, Gf
import math

def animate_camera(camera_prim, frame_positions, frame_targets=None):
    """
    Animate a camera over time by setting position and orientation per frame.

    Args:
        camera_prim (UsdGeom.Camera): Camera prim to animate.
        frame_positions (dict): Mapping frame -> position (x, y, z).
        frame_targets (dict, optional): Mapping frame -> target (x, y, z) to look at.
    """
    xformable = UsdGeom.Xformable(camera_prim)

    # Safely retrieve or add xform ops
    translate_op = _get_or_add_op(xformable, 'translate')
    rotate_x_op = _get_or_add_op(xformable, 'rotateX')
    rotate_y_op = _get_or_add_op(xformable, 'rotateY')

    for frame, pos in frame_positions.items():
        translate_op.Set(Gf.Vec3d(*pos), Usd.TimeCode(frame))

        if frame_targets and frame in frame_targets:
            direction = Gf.Vec3d(*frame_targets[frame]) - Gf.Vec3d(*pos)
            direction.Normalize()
            yaw = math.degrees(math.atan2(-direction[0], -direction[2]))
            pitch = math.degrees(math.asin(direction[1]))

            rotate_y_op.Set(yaw, Usd.TimeCode(frame))
            rotate_x_op.Set(pitch, Usd.TimeCode(frame))

def _get_or_add_op(xformable, op_type):
    """
    Get existing xform op if it exists, or add a new one.

    Args:
        xformable (UsdGeom.Xformable): The camera as a transformable prim.
        op_type (str): 'translate', 'rotateX', or 'rotateY'.

    Returns:
        UsdGeom.XformOp
    """
    attr_name = f'xformOp:{op_type}'
    prim = xformable.GetPrim()
    if prim.HasAttribute(attr_name):
        return prim.GetAttribute(attr_name)
    
    if op_type == 'translate':
        return prim.AddTranslateOp()
    elif op_type == 'rotateX':
        return prim.AddRotateXOp()
    elif op_type == 'rotateY':
        return prim.AddRotateYOp()
    else:
        raise ValueError(f"Unsupported op_type: {op_type}")

def generate_orbit_path(center, radius, height, frame_range):
    """
    Generate positions and targets for a camera orbiting a center point.

    Args:
        center (tuple): (x, y, z) target center
        radius (float): Orbit radius
        height (float): Y-axis height of the camera
        frame_range (tuple): (start_frame, end_frame)

    Returns:
        (dict, dict): frame_positions, frame_targets
    """
    frame_positions = {}
    frame_targets = {}
    start, end = frame_range
    center = Gf.Vec3d(*center)

    for frame in range(start, end + 1):
        angle = math.radians(360 * (frame - start) / (end - start + 1))
        x = center[0] + math.sin(angle) * radius
        z = center[2] + math.cos(angle) * radius
        y = height
        frame_positions[frame] = (x, y, z)
        frame_targets[frame] = tuple(center)

    return frame_positions, frame_targets
