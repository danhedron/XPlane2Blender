import bpy
import math
import mathutils
from ..xplane_helpers import *
from ..xplane_config import *

# Class: XPlaneBone
# Animation/Hierarchy primitive
class XPlaneBone():

    # Constructor: __init__
    #
    # Parameters:
    #   blenderObject - Blender Object
    #   xplaneObject - <XPlaneObject>
    #   parent - (optional) parent <XPlaneAnimBone>
    def __init__(self, blenderObject = None, xplaneObject = None, parent = None):
        self.xplaneObject = xplaneObject
        self.blenderObject = blenderObject
        self.blenderBone = None
        self.parent = parent
        self.children = []

        # nesting level of this bone (used for intendation)
        # TODO: create a getter which dynamically climbs up the tree to get the level?
        self.level = 0

        if self.parent:
            self.level = self.parent.level + 1

        # dict - The keys are the dataref paths and the values are lists of <XPlaneKeyframes>.
        self.animations = {}

    # Method: animated
    # Checks if the object is animated.
    #
    # Returns:
    #   bool - True if object is animated, False if not.
    def animated(self):
        return (hasattr(self,'animations') and len(self.animations)>0)

    # Method: getAnimations
    # Stores all animations of <object> or another Blender object in <animations>.
    #
    # Parameters:
    #   object - (default=None) A Blender object. If given animation of this object will be stored.
    def getAnimations(self,object = None, bone = None):
        debug = getDebug()
        debugger = getDebugger()

        if bone:
            groupName = "XPlane Datarefs "+bone.name
            object = object.data
        else:
            groupName = "XPlane Datarefs"

        if object == None:
            object = self.blenderObject
        #check for animation
        if debug:
            debugger.debug("\t\t checking animations of %s" % object.name)
        if (object.animation_data != None and object.animation_data.action != None and len(object.animation_data.action.fcurves)>0):
            if debug:
                debugger.debug("\t\t animation found")
            #check for dataref animation by getting fcurves with the dataref group
            for fcurve in object.animation_data.action.fcurves:
                if debug:
                    debugger.debug("\t\t checking FCurve %s Group: %s" % (fcurve.data_path,fcurve.group))
                #if (fcurve.group != None and fcurve.group.name == groupName): # since 2.61 group names are not set so we have to check the datapath
                if ('xplane.datarefs' in fcurve.data_path):
                    # get dataref name
                    pos = fcurve.data_path.find('xplane.datarefs[')
                    if pos!=-1:
                      index = fcurve.data_path[pos+len('xplane.datarefs[') : -len('].value')]
                    else:
                        return

                    # old style datarefs with wrong datapaths can cause errors so we just skip them
                    try:
                        index = int(index)
                    except:
                        return

                    # FIXME: removed datarefs keep fcurves, so we have to check if dataref is still there. FCurves have to be deleted correctly.
                    if bone:
                        if index<len(bone.xplane.datarefs):
                            dataref = bone.xplane.datarefs[index].path
                        else:
                            return
                    else:
                        if index<len(object.xplane.datarefs):
                            dataref = object.xplane.datarefs[index].path
                        else:
                            return

                    if debug:
                        debugger.debug("\t\t adding dataref animation: %s" % dataref)

                    if len(fcurve.keyframe_points)>1:
                        # time to add dataref to animations
                        self.animations[dataref] = []
                        if bone:
                            self.datarefs[dataref] = bone.xplane.datarefs[index]
                        else:
                            self.datarefs[dataref] = object.xplane.datarefs[index]

                        # store keyframes temporary, so we can resort them
                        keyframes = []

                        for keyframe in fcurve.keyframe_points:
                            if debug:
                                debugger.debug("\t\t adding keyframe: %6.3f" % keyframe.co[0])
                            keyframes.append(keyframe)

                        # sort keyframes by frame number
                        keyframesSorted = sorted(keyframes, key=lambda keyframe: keyframe.co[0])

                        for i in range(0,len(keyframesSorted)):
                            self.animations[dataref].append(XPlaneKeyframe(keyframesSorted[i],i,dataref,self))

    def getName(self):
        if self.parent == None:
            return '%d ROOT' % self.level
        elif self.blenderBone:
            return '%d Bone: %s' % (self.level, self.blenderBone.name)
        elif self.blenderObject:
            return '%d Object: %s' % (self.level, self.blenderObject.name)

        return 'UNKNOWN'

    def toString(self, indent = ''):
        out = indent + self.getName() + '\n'

        for bone in self.children:
            out += bone.toString(indent + '\t')

        return out

    def __str__(self):
        return self.toString()

    def write(self):
        # TODO: implement
        pass
