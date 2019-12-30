import bpy
import os
import inspect
import sys

from io_xplane2blender.tests import *
from io_xplane2blender import xplane_config
from io_xplane2blender.xplane_types import xplane_light

__dirname__ = os.path.dirname(__file__)

class TestParamLightParams(XPlaneTestCase):
    def test_comment_correct(self):
        xplaneFile = xplane_file.createFileFromBlenderRootObject(bpy.data.collections["Layer 1_Scene"])
        light = xplaneFile._bl_obj_name_to_bone["4_comment_contents_preserved_exactly"].xplaneObject
        self.assertTrue(light.comment == "0 spaces, number starts comment with uneven and a   trailing  space ")

    def test_illegal_params_content(self):
        out = self.exportLayer(1)
        self.assertLoggerErrors(3)

runTestCases([TestParamLightParams])

