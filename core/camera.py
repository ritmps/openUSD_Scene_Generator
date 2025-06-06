from pxr import UsdGeom, Gf, Usd
import math
import json
import os
import numpy as np

class Camera:
    """Manages camera creation and orientation in a USD stage."""

    def __init__(self, stage, root_path="/World/Cameras"):
        self.stage = stage
        self.root_path = root_path

    def add_camera(self, name="Camera", position=(0, 5, 15), target=None, 
                   projection="perspective",
                   focal_length=35.0, 
                   horizontal_aperture=20.955, vertical_aperture=15.2908,
                   clipping_range=(0.1, 1000.0)):
        """
        Add a camera to the stage, optionally oriented to look at a target.

        Args:
            name (str): Camera name (used as prim name).
            position (tuple): Camera position (x, y, z).
            target (tuple): Optional target point (x, y, z) to look at.
            projection (str): 'perspective' or 'orthographic'.
            focal_length (float): Lens focal length in mm.
            horizontal_aperture (float): Sensor width in mm.
            vertical_aperture (float): Sensor height in mm.
            clipping_range (tuple): Near and far clipping distances.

        Returns:
            UsdGeom.Camera
        """
        path = f"{self.root_path}/{name}"
        cam = UsdGeom.Camera.Define(self.stage, path)

        # Projection mode
        if projection not in ("perspective", "orthographic"):
            raise ValueError("projection must be 'perspective' or 'orthographic'")
        cam.CreateProjectionAttr().Set(projection)

        # Aperture and clip settings
        cam.CreateHorizontalApertureAttr().Set(horizontal_aperture)
        cam.CreateVerticalApertureAttr().Set(vertical_aperture)
        cam.CreateClippingRangeAttr().Set(clipping_range)

        if projection == "perspective":
            cam.CreateFocalLengthAttr().Set(focal_length)

        # Orientation
        if target:
            self._orient_camera_look_at(cam, position, target)
        else:
            cam.AddTranslateOp().Set(Gf.Vec3d(*position))

        return cam

    def generate_orbit_cameras(self, target=(0, 0, 0), radius=10.0, height=5.0,
                                num_views=8, focal_length=35.0, prefix="OrbitCam"):
        """
        Generate an orbiting camera array around a central target.

        Args:
            center (tuple): The point to orbit around (target).
            radius (float): Distance from the center.
            height (float): Fixed camera height.
            num_views (int): Number of views (cameras) in the orbit.
            focal_length (float): Lens focal length in mm.
            prefix (str): Name prefix for camera paths.

        Returns:
            list[str]: List of USD paths to created cameras.
        """
        paths = []
        for i in range(num_views):
            angle = 2 * math.pi * i / num_views
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            position = (x, height, z)
            name = f"{prefix}_{i}"
            self.add_camera(name=name, position=position, target=target, focal_length=focal_length)
            paths.append(f"{self.root_path}/{name}")
        return paths

    def _orient_camera_look_at(self, camera, position, target):
        """
        Rotate camera to look at a target point.

        Args:
            camera (UsdGeom.Camera): The camera prim.
            position (tuple): Position of the camera.
            target (tuple): Target position to look at.
        """
        # # Detect stage up axis and align camera
        # up_axis = UsdGeom.GetStageUpAxis(self.stage)
        # if up_axis == UsdGeom.Tokens.z:
        #     pitch = 90

        camera_pos = Gf.Vec3d(*position)
        target_pos = Gf.Vec3d(*target)

        # Calculate direction vector and normalize
        direction = (target_pos - camera_pos).GetNormalized()

        # Convert direction to yaw (around Y) and pitch (around X) angles
        yaw = math.degrees(math.atan2(-direction[0], -direction[2]))
        pitch = math.degrees(math.asin(direction[1]))

        # Apply transforms to camera
        camera.AddTranslateOp().Set(camera_pos)
        camera.AddRotateYOp().Set(yaw)
        camera.AddRotateXOp().Set(pitch)

        
    def export_camera_metadata(camera_prim, output_path, resolution=(512, 512)):
        """
        Export camera intrinsic and extrinsic parameters to a JSON file.

        Args:
            camera_prim (UsdGeom.Camera): The camera primitive.
            output_path (str): Path to save the JSON metadata.
            resolution (tuple): Image resolution as (width, height).
        """
        # Intrinsic parameters
        focal_length_mm = camera_prim.GetFocalLengthAttr().Get()
        h_aperture_mm = camera_prim.GetHorizontalApertureAttr().Get()
        v_aperture_mm = camera_prim.GetVerticalApertureAttr().Get()
        projection = camera_prim.GetProjectionAttr().Get()
        clipping_range = camera_prim.GetClippingRangeAttr().Get()

        width, height = resolution

        # Derived pixel size (mm per pixel)
        pixel_size_x = h_aperture_mm / width
        pixel_size_y = v_aperture_mm / height

        # Focal lengths in pixels
        fx = focal_length_mm / pixel_size_x
        fy = focal_length_mm / pixel_size_y
        cx = width / 2.0
        cy = height / 2.0
        skew = 0.0  # Assuming no skew

        # Intrinsic matrix K
        K = [
            [fx, skew, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0]
        ]

        # Extrinsic parameters
        xform_cache = UsdGeom.XformCache(Usd.TimeCode.Default())
        world_transform = xform_cache.GetLocalToWorldTransform(camera_prim)
        world_matrix = np.array(world_transform)

        R = world_matrix[:3, :3].tolist()
        T = world_matrix[:3, 3].tolist()

        # Projection matrix P = K * [R | T]
        RT = np.hstack((world_matrix[:3, :3], np.array(world_matrix[:3, 3]).reshape(3, 1)))
        P = (np.dot(K, RT)).tolist()

        # Compile metadata
        metadata = {
            "intrinsic": {
                "focal_length_mm": focal_length_mm,
                "horizontal_aperture_mm": h_aperture_mm,
                "vertical_aperture_mm": v_aperture_mm,
                "pixel_size_mm": {
                    "x": pixel_size_x,
                    "y": pixel_size_y
                },
                "fx": fx,
                "fy": fy,
                "cx": cx,
                "cy": cy,
                "skew": skew,
                "K": K
            },
            "extrinsic": {
                "R": R,
                "T": T
            },
            "projection_matrix": P,
            "resolution": {
                "width": width,
                "height": height
            },
            "projection": projection,
            "clipping_range": clipping_range
        }

        # Save to JSON
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        print(f"[Camera] Metadata exported to: {output_path}")
    