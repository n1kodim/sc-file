from dataclasses import dataclass, field
from typing import Dict, List

from scfile.consts import McsaModel, Normalization


def scaled(i: float, scale: float = 1.0, factor: float = Normalization.I16) -> float:
    return (i * scale) / factor

@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0

@dataclass
class Normals:
    i: float = 0.0
    j: float = 0.0
    k: float = 0.0

@dataclass
class Curve:
    u: float = 0.0
    v: float = 0.0

@dataclass
class VertexBone:
    ids: Dict[int, int] = field(default_factory=dict)
    weights: Dict[int, float] = field(default_factory=dict)

@dataclass
class Vertex:
    position: Vector = field(default_factory=Vector)
    texture: Texture = field(default_factory=Texture)
    normals: Normals = field(default_factory=Normals)
    curve: Curve = field(default_factory=Curve)
    bone: VertexBone = field(default_factory=VertexBone)

@dataclass
class Polygon:
    v1: int = 0
    v2: int = 0
    v3: int = 0

@dataclass
class Mesh:
    name: str = "name"
    material: str = "material"
    link_count: int = 0
    vertices: List[Vertex] = field(default_factory=list)
    polygons: List[Polygon] = field(default_factory=list)

    def resize_vertices(self, count: int):
        self.vertices = [Vertex() for _ in range(count)]

    def resize_polygons(self, count: int):
        self.polygons = [Polygon() for _ in range(count)]

@dataclass
class Bone:
    name: str = "bone"
    parent_id: int = McsaModel.ROOT_BONE_ID
    position: Vector = field(default_factory=Vector)
    rotation: Vector = field(default_factory=Vector)

@dataclass
class Skeleton:
    bones: List[Bone] = field(default_factory=list)

@dataclass
class Scale:
    position: float = 1.0
    texture: float = 1.0
    normals: float = 1.0
    unknown: float = 1.0

@dataclass
class Model:
    meshes: List[Mesh] = field(default_factory=list)
    skeleton: Skeleton = field(default_factory=Skeleton)
    scale: Scale = field(default_factory=Scale)
