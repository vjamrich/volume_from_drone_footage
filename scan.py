import os
from math import sin, cos, sqrt, atan2
import Metashape
from datetime import datetime
from dict import *


class Scan:
    def __init__(self, input_location, config):
        self.input = input_location
        self.config = config
        self.photos = os.listdir(self.input)
        self.output = self.config["output path"]
        self.basename = os.path.basename(self.input)
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.project_path = self.output + "\\" + self.basename + "_" + self.timestamp
        self.doc = Metashape.app.document
        self.chunk = None

        # Align photos config
        self.accuracy = ACCURACY[self.config["settings"]["accuracy align photos"]]
        self.threshold = self.config["settings"]["camera quality threshold"]

        # Build dense cloud config
        self.quality_dense = QUALITY[self.config["settings"]["quality build dense cloud"]]
        self.filtering_dense = FILTERING[self.config["settings"]["filtering build dense cloud"]]

        # Build mesh config
        self.quality_mesh = QUALITY[self.config["settings"]["quality build mesh"]]
        config_polycount = self.config["settings"]["polygon count build mesh"]
        if type(config_polycount) == int:
            self.poly_count = config_polycount
        else:
            self.poly_count = POLYCOUNT[config_polycount]

        # Markers config
        self.marker_type = TARGETTYPE[self.config["settings"]["marker type"]]
        self.marker_distance = self.config["settings"]["distance between markers [meters]"]
        self.marker_tolerance = self.config["settings"]["marker detection tolerance"]
        self.size_buffer = 1.1

        # Construct
        self.doc.clear()
        self.create()

        if self.config["operations"]["add photos"]:
            self.add_photos()
            self.doc.save()
        if self.config["operations"]["don't use low quality photos"]:
            self.disabled_cameras = self.estimate_quality()
            self.doc.save()
        if self.config["operations"]["align photos"]:
            self.not_aligned = self.align_photos()
            self.doc.save()
        if self.config["operations"]["detect markers"]:
            self.markers_detected = self.detect_markers()
            if self.markers_detected == 2:
                if self.chunk.markers[0].position is not None and self.chunk.markers[1].position is not None:
                    self.scale()
                    self.transform_chunk()
            self.doc.save()
        if self.config["operations"]["build dense cloud"]:
            self.build_dense()
            self.doc.save()
        if self.config["operations"]["build mesh"]:
            self.build_mesh()
            self.doc.save()
        if self.config["operations"]["close holes in the mesh"]:
            self.close_holes()
            self.volume = self.get_volume()
            self.doc.save()
        self.volume = self.get_volume()
        if self.config["operations"]["output text file with volume"]:
            self.output_report()
            self.doc.save()

        self.doc.save()

    def create(self):
        os.mkdir(self.project_path)
        self.doc.save(path=self.project_path + "\\" + self.basename + ".PSX")
        self.add_chunk()

    def add_chunk(self, name=None):
        self.chunk = self.doc.addChunk()
        if name is not None:
            self.chunk.label = name

    def add_photos(self):
        photo_paths = [self.input+"\\"+photo_name for photo_name in self.photos]
        self.chunk.addPhotos(photo_paths)

    def estimate_quality(self):
        self.chunk.estimateImageQuality()
        disabled_cameras = 0
        for camera in range(len(self.chunk.cameras)):
            quality = float(self.chunk.cameras[camera].meta["Image/Quality"])
            if quality < self.threshold:
                self.chunk.cameras[camera].enabled = False
                disabled_cameras += 1
        return disabled_cameras

    def align_photos(self):
        self.chunk.matchPhotos(accuracy               = self.accuracy,
                               reference_preselection = False,
                               mask_tiepoints         = True)
        self.chunk.alignCameras()
        not_aligned = 0
        for camera in range(len(self.chunk.cameras)):
            if not self.chunk.cameras[camera].transform:
                not_aligned += 1
        return not_aligned

    def detect_markers(self):
        self.chunk.detectMarkers(type      = self.marker_type,
                                 tolerance = self.marker_tolerance,
                                 inverted  = False)
        markers_detected = len(self.chunk.markers)
        return markers_detected

    def scale(self, marker_1 = 0, marker_2 = 1):
        scalebar = self.chunk.addScalebar(self.chunk.markers[marker_1], self.chunk.markers[marker_2])
        scalebar.reference.distance = self.marker_distance
        self.chunk.updateTransform()

    def build_dense(self):
        self.chunk.buildDepthMaps(quality = self.quality_dense,
                                  filter  = self.filtering_dense)

        self.chunk.buildDenseCloud(point_colors = True)

    def build_mesh(self):
        self.chunk.buildModel(face_count    = self.poly_count,
                              vertex_colors = True,
                              quality       = self.quality_mesh)

    def close_holes(self):
        self.chunk.model.closeHoles(level = 100)

    def get_volume(self):
        volume = self.chunk.model.volume()
        return volume

    def transform_chunk(self):
        m1 = self.chunk.markers[0].position
        m2 = self.chunk.markers[1].position

        dist = sqrt(sum([(a - b) ** 2 for a, b in zip(m1, m2)]))
        region_size = (sqrt(2)*dist)/2 * self.size_buffer
        self.chunk.region.size = [region_size, region_size, region_size]
        self.chunk.region.center = (m1[0] + m2[0])/2, (m1[1] + m2[1])/2, (m1[2] + m2[2])/2

        vx, vy, vz = m2 - m1
        angle_x = atan2(sqrt(vy**2 + vz**2), vx)
        angle_y = atan2(sqrt(vz**2 + vx**2), vy)
        angle_z = atan2(sqrt(vx**2 + vy**2), vz)
        
        rot_x_matrix = self._get_rot_matrix("x", angle_x)
        rot_y_matrix = self._get_rot_matrix("y", angle_y)
        rot_z_matrix = self._get_rot_matrix("z", angle_z)

        self.chunk.region.rot = rot_x_matrix * rot_y_matrix * rot_z_matrix

    def _get_rot_matrix(self, axis, radians):
        r = radians
        matrix = None
        if axis == 'z':
            matrix = Metashape.Matrix([[cos(r), -sin(r), 0],
                                       [sin(r),  cos(r), 0],
                                       [0,       0,      1]])

        elif axis == 'y':
            matrix = Metashape.Matrix([[ cos(r), 0, sin(r)],
                                       [ 0,      1, 0     ],
                                       [-sin(r), 0, cos(r)]])

        elif axis == 'x':
            matrix = Metashape.Matrix([[1, 0,       0      ],
                                       [0, cos(r), -sin(r) ],
                                       [0, sin(r),  cos(r) ]])
        return matrix

    def output_report(self):
        f = open(self.project_path + "\\" + self.basename + "_OUTPUT.txt", "w+")
        f.write("Project name: " + self.basename + "\n")
        f.write("Time [YYYY-MM-DD hh:mm:ss]: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S" + "\n"))
        f.write("Volume [cubic meters]: " + str(round(self.volume, 2)) + "\n")
        f.close()
