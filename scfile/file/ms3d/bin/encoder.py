from scfile.consts import McsaModel
from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder

from scfile.enums import StructFormat as F
from scfile.utils.model import Polygon, Vertex


class Ms3dBinEncoder(FileEncoder[ModelData]):
    def serialize(self):
        self.model = self.data.model
        self.meshes = self.data.model.meshes
        self.flags = self.data.model.flags

        self.model.ensure_unique_names()
        self.model.convert_polygons_to_global()

        self._add_header()
        self._add_vertices()
        self._add_triangles()
        self._add_groups()
        self._add_materials()
        self._add_joints()

    def _add_header(self):
        self.b.writes("MS3D000000")  # 10 bytes signature
        self.b.writeb(F.I32, 0x4)  # version

    def _add_vertices(self):
        total_vertices = sum(mesh.count.vertices for mesh in self.model.meshes)
        self.b.writeb(F.U16, total_vertices)

        for mesh in self.meshes:
            for v in mesh.vertices:
                pos = v.position

                self.b.writeb(F.I8, 0)  # flags
                self.b.writeb(F.F32 * 3, pos.x, pos.y, pos.z)  # position
                self.b.writeb(F.I8, -1)  # bone id
                self.b.writeb(F.U8, 0xFF)  # reference count (?)

    def _add_triangles(self):
        total_polygons = sum(mesh.count.polygons for mesh in self.model.meshes)
        self.b.writeb(F.U16, total_polygons)

        for index, mesh in enumerate(self.meshes):
            for p, gp in zip(mesh.polygons, mesh.global_polygons):
                self.b.writeb(F.U16, 0)  # flags

                self._add_indices(gp)

                v1 = mesh.vertices[p.a]
                v2 = mesh.vertices[p.b]
                v3 = mesh.vertices[p.c]

                self._add_normals(v1)
                self._add_normals(v2)
                self._add_normals(v3)
                self._add_textures(v1, v2, v3)

                self.b.writeb(F.U8, 1)  # smoothing group
                self.b.writeb(F.U8, index)  # group index

    def _add_indices(self, p: Polygon):
        self.b.writeb(F.U16 * 3, p.a, p.b, p.c)

    def _add_normals(self, v: Vertex):
        self.b.writeb(F.F32 * 3, v.normals.x, v.normals.y, v.normals.z)

    def _add_textures(self, v1: Vertex, v2: Vertex, v3: Vertex):
        self.b.writeb(F.F32 * 3, v1.texture.u, v2.texture.u, v3.texture.u)
        self.b.writeb(F.F32 * 3, v1.texture.v, v2.texture.v, v3.texture.v)

    def _add_groups(self):
        self.b.writeb(F.U16, len(self.meshes))  # groups count

        offset = 0

        for index, mesh in enumerate(self.meshes):
            self.b.writeb(F.U8, 0)  # flags
            self.b.write(self._fixedlen(mesh.name))  # group name

            self.b.writeb(F.U16, mesh.count.polygons)  # triangles count

            for p in range(len(mesh.polygons)):
                self.b.writeb(F.U16, p + offset)  # triangles indexes

            self.b.writeb(F.I8, index)  # material index

            offset += len(mesh.polygons)

    def _add_materials(self):
        self.b.writeb(F.U16, len(self.meshes))  # materials count

        for mesh in self.meshes:
            self.b.write(self._fixedlen(mesh.material))  # material name
            self.b.writeb(F.F32 * 4, 0.2, 0.2, 0.2, 1.0)  # ambient rgba
            self.b.writeb(F.F32 * 4, 0.8, 0.8, 0.8, 1.0)  # diffuse rgba
            self.b.writeb(F.F32 * 4, 0.0, 0.0, 0.0, 1.0)  # specular rgba
            self.b.writeb(F.F32 * 4, 0.0, 0.0, 0.0, 1.0)  # emissive rgba
            self.b.writeb(F.F32, 0.0)  # shininess
            self.b.writeb(F.F32, 1.0)  # transparency
            self.b.writeb(F.I8, 1)  # mode
            self.b.writen(count=128, size=1)  # texture
            self.b.writen(count=128, size=1)  # alphamap

    def _add_joints(self):
        self.b.writeb(F.F32, 24)  # fps
        self.b.writeb(F.F32, 1)  # current frame
        self.b.writeb(F.F32, 30)  # total frames

        skeleton = self.model.skeleton

        self.b.writeb(F.U16, len(skeleton.bones))

        for bone in skeleton.bones:
            self.b.writeb(F.U8, 0)  # flags
            self.b.write(self._fixedlen(bone.name))  # bone name

            parent = skeleton.bones[bone.parent_id].name
            parent_name = parent if bone.parent_id != McsaModel.ROOT_BONE_ID else ""

            self.b.write(self._fixedlen(parent_name))  # parent name

            rot = bone.rotation
            pos = bone.position
            self.b.writeb(F.F32 * 3, rot.x, rot.y, rot.z)  # rotation
            self.b.writeb(F.F32 * 3, pos.x, pos.y, pos.z)  # position

            self.b.writeb(F.U16, 0)  # count keyframes rotation
            self.b.writeb(F.U16, 0)  # count keyframes transition

    def _fixedlen(self, name: str) -> bytes:
        return name.encode("utf-8").ljust(32, b"\x00")
