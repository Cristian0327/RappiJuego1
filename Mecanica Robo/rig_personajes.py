"""Build the robbery character FBXs in Blender's background mode."""
from math import pi, sin, sqrt
from pathlib import Path

import bpy
import bmesh
from mathutils import Quaternion, Vector

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
ART = PROJECT / "SourceArt" / "PersonajesVoxel"
OUTPUT = ART / "Rigs"
SOURCE = ART / "Personajes_Bogota_Voxel.blend"

CLIPS = {
    "Walk": ROOT / "outputs/DeliveryArt/AnimationRebuild/Upright/AN_HeroWalk_Rebuilt.blend",
    "Run": ROOT / "outputs/DeliveryArt/AnimationRebuild/Upright/AN_HeroRun_Rebuilt.blend",
}


def sample_clip(path, leg_emphasis, with_contacts=False):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    rig = next(o for o in scene.objects if o.type == "ARMATURE" and o.animation_data and o.animation_data.action)
    first, last = map(round, rig.animation_data.action.frame_range)
    frames = []
    for frame in range(first, last + 1):
        scene.frame_set(frame)
        pose = {
            b.name: b.bone.matrix_local.to_quaternion() @ b.matrix_basis.to_quaternion()
            @ b.bone.matrix_local.to_quaternion().inverted()
            for b in rig.pose.bones
        }
        for name, rotation in pose.items():
            if name.startswith(("thigh_", "calf_")):
                if rotation.w < 0:
                    rotation.negate()
                pose[name] = Quaternion(rotation.axis, rotation.angle * leg_emphasis)
        if with_contacts:
            # Source is authored in centimeters. Nero is enlarged 13% in Unreal.
            pose["contacts"] = {b.name: b.head.copy() / 113 for b in rig.pose.bones}
        frames.append(pose)
    return frames


def make_rig(name):
    data = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")

    def bone(label, head, tail, parent=None):
        item = data.edit_bones.new(label)
        item.head = Vector(head) * .18
        item.tail = Vector(tail) * .18
        if parent:
            item.parent = data.edit_bones[parent]

    bone("root", (0, 0, 0), (0, 0, .5))
    bone("pelvis", (0, 0, 4), (0, 0, 4.45), "root")
    bone("spine_01", (0, 0, 4.45), (0, 0, 5.55), "pelvis")
    bone("spine_02", (0, 0, 5.55), (0, 0, 6.3), "spine_01")
    bone("spine_03", (0, 0, 6.3), (0, 0, 6.65), "spine_02")
    bone("neck_01", (0, 0, 6.65), (0, 0, 7.05), "spine_03")
    bone("head", (0, 0, 7.05), (0, 0, 8.6), "neck_01")
    for side, sign in (("l", 1), ("r", -1)):
        def limb(label, head, tail, parent):
            bone(f"{label}_{side}", (head[0] * sign, *head[1:]),
                 (tail[0] * sign, *tail[1:]), parent)

        limb("clavicle", (.15, 0, 6.55), (1.05, 0, 6.55), "spine_03")
        limb("upperarm", (1.05, 0, 6.55), (1.27, 0, 5.48), f"clavicle_{side}")
        limb("lowerarm", (1.27, 0, 5.48), (1.43, 0, 4.42), f"upperarm_{side}")
        limb("hand", (1.43, 0, 4.42), (1.48, 0, 3.78), f"lowerarm_{side}")
        limb("thigh", (.51, .05, 4), (.51, .05, 2), "pelvis")
        limb("calf", (.51, .05, 2), (.51, .05, .74), f"thigh_{side}")
        limb("foot", (.51, .05, .74), (.51, -.62, .4), f"calf_{side}")
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


def export(path, rig, mesh=None):
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    if mesh:
        mesh.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True,
        object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
        apply_scale_options="FBX_SCALE_ALL", axis_forward="-Y", axis_up="Z",
        bake_anim=mesh is None, bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False, bake_anim_simplify_factor=0, colors_type="LINEAR")


def joint_weights(upper, lower, z, joint, width):
    alpha = max(0.0, min(1.0, (z - joint + width) / (2 * width)))
    alpha = alpha * alpha * (3 - 2 * alpha)
    return [(bone, weight) for bone, weight in ((upper, alpha), (lower, 1 - alpha)) if weight > 0]


def bind_meshes(collection, rig, center, accessory=None):
    meshes = []
    props = list(accessory.objects) if accessory else []
    for mesh in list(collection.objects) + props:
        if mesh.type not in {"MESH", "FONT"}:
            continue
        if mesh.type == "FONT":
            text = mesh
            depsgraph = bpy.context.evaluated_depsgraph_get()
            data = bpy.data.meshes.new_from_object(text.evaluated_get(depsgraph))
            mesh = bpy.data.objects.new(text.name + "_Mesh", data)
            collection.objects.link(mesh)
            mesh.matrix_world = text.matrix_world
            bpy.data.objects.remove(text, do_unlink=True)
        matrix = mesh.matrix_world.copy()
        mesh.data = mesh.data.copy()
        mesh.parent = None
        mesh.matrix_world.identity()
        center_x = matrix.translation.x - center
        leg = (
            mesh not in props
            and mesh.name != "Cintura"
            and abs(center_x) > .25
            and max((matrix @ v.co).z for v in mesh.data.vertices) < 4.05
            and abs(center_x) < 1.02
        )
        sign = 1 if center_x > 0 else -1
        side = "l" if sign > 0 else "r"
        for vertex in mesh.data.vertices:
            vertex.co = matrix @ vertex.co
            vertex.co.x -= center
            if mesh.name.startswith("Dedo del guante"):
                finger_offset = center_x - sign * 1.43
                finger_tip = max(0, 3.89 - vertex.co.z)
                vertex.co.x += finger_offset * finger_tip * .65
            if leg:
                vertex.co.x = sign * max(sign * vertex.co.x, .045)
        if leg and min(v.co.z for v in mesh.data.vertices) < 2 < max(v.co.z for v in mesh.data.vertices):
            topology = bmesh.new()
            topology.from_mesh(mesh.data)
            bmesh.ops.bisect_plane(
                topology, geom=list(topology.verts) + list(topology.edges) + list(topology.faces),
                dist=.0001, plane_co=(0, 0, 2), plane_no=(0, 0, 1),
            )
            topology.to_mesh(mesh.data)
            topology.free()
        colors = mesh.data.color_attributes.new(name="ColoresVoxel", type="FLOAT_COLOR", domain="CORNER")
        for polygon in mesh.data.polygons:
            color = mesh.data.materials[polygon.material_index].diffuse_color
            for loop in polygon.loop_indices:
                colors.data[loop].color = color
        for vertex in mesh.data.vertices:
            point = vertex.co.copy()
            x, _, z = point
            if mesh in props:
                point.x += center - 4.62 - 1.48
                point.y -= .15
                point.z += 2.08
                weights = [("hand_r", 1)]
            elif mesh.name.startswith(("Piercing", "Barba")) or z >= 7.25:
                weights = [("head", 1)]
            elif abs(x) > .94 and 3.4 < z < 6.8 and abs(center_x) > 1.02:
                if z > 6.20:
                    weights = joint_weights(f"clavicle_{side}", f"upperarm_{side}", z, 6.55, .35)
                elif z > 4.95:
                    weights = joint_weights(f"upperarm_{side}", f"lowerarm_{side}", z, 5.48, .44)
                else:
                    weights = joint_weights(f"lowerarm_{side}", f"hand_{side}", z, 4.42, .34)
            elif leg:
                if z > 3.50:
                    weights = joint_weights("pelvis", f"thigh_{side}", z, 4, .52)
                elif z > 1.25:
                    weights = joint_weights(f"thigh_{side}", f"calf_{side}", z, 2, .52)
                else:
                    weights = joint_weights(f"calf_{side}", f"foot_{side}", z, .80, .30)
            elif z > 6.4:
                weights = joint_weights("head", "neck_01", z, 7.05, .20)
            else:
                weights = joint_weights("spine_01", "pelvis", z, 4.48, .40)
            for label, weight in weights:
                group = mesh.vertex_groups.get(label) or mesh.vertex_groups.new(name=label)
                group.add([vertex.index], weight, "REPLACE")
            vertex.co = point * .18
        meshes.append(mesh)
    bpy.ops.object.select_all(action="DESELECT")
    for mesh in meshes:
        mesh.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "SK_" + rig.name
    mesh.parent = rig
    modifier = mesh.modifiers.new("Skeleton", "ARMATURE")
    modifier.object = rig
    assert all(1 <= len(v.groups) <= 2 and abs(sum(g.weight for g in v.groups) - 1) < .001
               for v in mesh.data.vertices)
    leg_bones = {"foot", "calf", "thigh"}
    for edge in mesh.data.edges:
        sides = {label[-1] for i in edge.vertices for g in mesh.data.vertices[i].groups
                 if (label := mesh.vertex_groups[g.group].name)[:-2] in leg_bones}
        assert len(sides) < 2, sides
    assert len({tuple(c.color) for c in mesh.data.color_attributes["ColoresVoxel"].data}) > 12
    return mesh


def pose_rotation(bone, frame):
    rest = bone.bone.matrix_local.to_quaternion()
    delta = frame.get(bone.name)
    return rest.inverted() @ delta @ rest if delta else Quaternion()


def apply_root_offset(rig, frame):
    root = rig.pose.bones["root"]
    root.location = root.bone.matrix_local.to_quaternion().inverted() @ frame.get("root_offset", Vector())


def aim_bone(bone, current_direction, target_direction):
    orientation = bone.matrix.to_quaternion()
    turn = current_direction.rotation_difference(target_direction)
    bone.rotation_quaternion = bone.rotation_quaternion @ orientation.inverted() @ turn @ orientation
    bpy.context.view_layer.update()


def fit_limb(rig, labels, contacts):
    upper, lower, end = (rig.pose.bones[name] for name in labels)
    start = upper.head.copy()
    to_contact = contacts[end.name] - start
    axis = to_contact.normalized()
    upper_length = (lower.head - start).length
    lower_length = (end.head - lower.head).length
    distance = max(abs(upper_length - lower_length) + .001,
                   min(to_contact.length, upper_length + lower_length - .001))
    along = (upper_length ** 2 - lower_length ** 2 + distance ** 2) / (2 * distance)
    guide = contacts[lower.name] - start
    bend = (guide - axis * guide.dot(axis)).normalized()
    joint = start + axis * along + bend * sqrt(max(0, upper_length ** 2 - along ** 2))
    aim_bone(upper, lower.head - upper.head, joint - start)
    aim_bone(lower, end.head - lower.head, start + axis * distance - lower.head)


def fit_vehicle_contacts(rig, frames, mounting=False):
    rig.animation_data_clear()
    for frame in frames:
        contacts = frame.pop("contacts")
        if mounting:
            # Unreal already moves the whole actor sideways from the approach point to the seat.
            lateral = contacts["root"].x
            contacts = {name: value - Vector((lateral, 0, 0)) for name, value in contacts.items()}
        frame["root_offset"] = contacts["pelvis"] - rig.data.bones["pelvis"].head_local
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"
            bone.rotation_quaternion = pose_rotation(bone, frame)
        apply_root_offset(rig, frame)
        bpy.context.view_layer.update()
        for side in ("l", "r"):
            fit_limb(rig, tuple(f"{bone}_{side}" for bone in ("upperarm", "lowerarm", "hand")), contacts)
            fit_limb(rig, tuple(f"{bone}_{side}" for bone in ("thigh", "calf", "foot")), contacts)
        for bone in rig.pose.bones:
            rest = bone.bone.matrix_local.to_quaternion()
            frame[bone.name] = rest @ bone.rotation_quaternion @ rest.inverted()
    rig.pose.bones["root"].location = Vector()


def bake(rig, name, frames, fps=30):
    rig.animation_data_clear()
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, len(frames)
    scene.render.fps = fps
    previous = {}
    for index, frame in enumerate(frames, 1):
        apply_root_offset(rig, frame)
        rig.pose.bones["root"].keyframe_insert("location", frame=index, group="root")
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"
            rotation = pose_rotation(bone, frame)
            if bone.name in previous:
                rotation.make_compatible(previous[bone.name])
            previous[bone.name] = rotation.copy()
            bone.rotation_quaternion = rotation
            bone.keyframe_insert("rotation_quaternion", frame=index, group=bone.name)
    rig.animation_data.action.name = name
    rig.animation_data.action.use_fake_user = True
    scene.frame_set(1)


VEHICLE_CLIPS = {
    "BikePedal": "AN_HeroBikePedal_Fluido.blend",
    "MotoRide": "AN_HeroMotoRide_Rebuilt.blend",
}
vehicle_clips = {
    name: sample_clip(ROOT / "outputs/DeliveryArt/AnimationRebuild" / filename, 1.0, with_contacts=True)
    for name, filename in VEHICLE_CLIPS.items()
}


def mount_frames(frames, seated):
    # Preserve the player's mount motion and match the first riding pose at the handoff.
    tail = min(6, len(frames) - 1)
    if tail:
        for offset in range(1, tail + 1):
            pose = frames[len(frames) - 1 - tail + offset]
            t = offset / tail
            blend = t * t * (3 - 2 * t)
            for bone in (pose.keys() | seated.keys()) - {"root_offset"}:
                pose[bone] = pose.get(bone, Quaternion()).slerp(seated.get(bone, Quaternion()), blend)
            pose["root_offset"] = pose["root_offset"].lerp(seated["root_offset"], blend)
    return frames


mount_clips = {}
for suffix, folder in (("", ""), ("Left", "BothSides/")):
    for vehicle, ride in (("Bike", "BikePedal"), ("Moto", "MotoRide")):
        source = f"{folder}AN_HeroMount{vehicle}{'_Left' if suffix else ''}.blend"
        frames = sample_clip(ROOT / "outputs/DeliveryArt/AnimationRebuild" / source, 1.0, with_contacts=True)
        mount_clips[f"Mount{vehicle}{suffix}"] = (frames, ride)
rayas_walk = sample_clip(ROOT / "outputs/DeliveryArt/AnimationRebuild/Upright/AN_HeroWalk_Rebuilt.blend", 1.05)
for index, pose in enumerate(rayas_walk):
    phase = 2 * pi * index / max(1, len(rayas_walk) - 1)
    stride = sin(phase)
    pose["spine_01"] = Quaternion((1, 0, 0), .17)
    pose["spine_03"] = Quaternion((0, 0, 1), .12 * stride)
    pose["head"] = Quaternion((1, 0, 0), -.16)
    for side, sign in (("l", 1), ("r", -1)):
        swing = sign * stride
        pose[f"upperarm_{side}"] = (
            Quaternion((1, 0, 0), -.56 - .12 * swing)
            @ Quaternion((0, 1, 0), -.39 * sign)
        )
        pose[f"lowerarm_{side}"] = Quaternion((1, 0, 0), -.60 + .11 * swing)
        pose[f"hand_{side}"] = (
            Quaternion((1, 0, 0), .23)
            @ Quaternion((0, 0, 1), -.37 * sign)
        )
OUTPUT.mkdir(exist_ok=True)
clips = {name: sample_clip(path, 1.08 if name == "Walk" else .88) for name, path in CLIPS.items()}
for name, prefix, center in (("Rayas", "01 |", -2.42), ("Hornets", "02 |", 1.83)):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    collection = next(c for c in bpy.data.collections if c.name.startswith(prefix))
    rig = make_rig(name)
    accessory = next((c for c in bpy.data.collections if c.name.startswith("03 |")), None)
    mesh = bind_meshes(collection, rig, center, accessory if name == "Hornets" else None)
    artwork = mesh.data
    mesh.data = artwork.copy()
    mesh.data.materials.clear()
    export(OUTPUT / f"SK_{name}.fbx", rig, mesh)
    exported_mesh = mesh.data
    mesh.data = artwork
    bpy.data.meshes.remove(exported_mesh)
    if name == "Hornets":
        for frames in vehicle_clips.values():
            fit_vehicle_contacts(rig, frames)
        for frames, _ in mount_clips.values():
            fit_vehicle_contacts(rig, frames, mounting=True)
        mounts = {clip: mount_frames(frames, vehicle_clips[ride][0]) for clip, (frames, ride) in mount_clips.items()}
        actor_clips = {**clips, **vehicle_clips, **mounts}
    else:
        actor_clips = {**clips, "Walk": rayas_walk}
    for clip, frames in actor_clips.items():
        bake(rig, f"AN_{name}_{clip}", frames, fps=60 if clip == "BikePedal" else 30)
        export(OUTPUT / f"AN_{name}_{clip}.fbx", rig)
    frames = []
    for frame in range(31):
        wave = sin(frame * 2 * pi / 30)
        effort = .5 + .5 * wave
        # The free hand reaches for the rider. Nero keeps his prop hand below it.
        right_reach = -.28 if name == "Hornets" else -.96
        frames.append({
            "spine_01": Quaternion((1, 0, 0), .13 + .08 * effort),
            "head": Quaternion((1, 0, 0), -.12),
            "thigh_l": Quaternion((1, 0, 0), -.16),
            "calf_l": Quaternion((1, 0, 0), .29),
            "upperarm_l": Quaternion((1, 0, 0), -1.00 - .10 * effort),
            "lowerarm_l": Quaternion((1, 0, 0), -.48 + .13 * effort),
            "upperarm_r": Quaternion((1, 0, 0), right_reach - .08 * effort),
            "lowerarm_r": Quaternion((1, 0, 0), -.44 + .13 * effort),
        })
    if name == "Rayas":
        for pose in frames:
            for side, sign in (("l", 1), ("r", -1)):
                arm = f"upperarm_{side}"
                pose[arm] = pose[arm] @ Quaternion((0, 1, 0), -.27 * sign)
                pose[f"hand_{side}"] = Quaternion((1, 0, 0), .22) @ Quaternion((0, 0, 1), -.30 * sign)
    bake(rig, f"AN_{name}_Prompt", frames)
    export(OUTPUT / f"AN_{name}_Prompt.fbx", rig)
    rig.animation_data_clear()
    for bone in rig.pose.bones:
        bone.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / f"{name}_Rig.blend"))
    print(f"ROBBERY_RIG {name} {len(rig.data.bones)} bones {len(mesh.data.vertices)} vertices")

