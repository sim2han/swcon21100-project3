import fbx
import glm
from fbx import FbxAMatrix
from fbx import FbxTime
from fbx import FbxNode
from fbx import FbxNodeAttribute
from FbxCommon import *

class Vertex:
    def __init__(self):
        pass

class Mesh:
    def __init__(self):
        self.vertices = []
        self.polygon = []

class Material:
    def __init__(self):
        self.diffuse = glm.vec3()

class Joint:
    def __init__(self):
        pass

class BlendingIndexWeightPair:
    def __init__(self, index, weight):
        self.index = index
        self.weight = weight

class FbxLoader:
    def __init__(self):
        self.meshes = []
        self.matrials = []
        self.joints = []
        pass

    def InitScene(self, scene):
        self.scene = scene

    def InitMesh(self):
        rootNode = self.scene.GetRootNode()
        if rootNode:
            for i in range(rootNode.GetChildCount()):
                lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
                if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                    mesh = Mesh()
                    lMesh = rootNode.GetChild(i).GetNodeAttribute()

                    mesh.mesh = lMesh
                    mesh.name = rootNode.GetChild(i).GetName()
                    mesh.pointCount = lMesh.GetControlPointsCount()

                    controlPoints = lMesh.GetControlPoints()
                    for j in range(mesh.pointCount):
                        #vertex = Vertex()
                        #vertex.vertex = lMesh.GetControlPoints()[j]
                        mesh.vertices.append(controlPoints[j])
                        controlPoints[j].blendingInfo = []

                    mesh.polygonCount = lMesh.GetPolygonCount()
                    
                    for j in range(mesh.polygonCount):
                        lPolygonSize = lMesh.GetPolygonSize(j)                   
                        for k in range(lPolygonSize - 2):
                            tri = []
                            tri.append(lMesh.GetPolygonVertex(j, 0))
                            tri.append(lMesh.GetPolygonVertex(j, k + 1))
                            tri.append(lMesh.GetPolygonVertex(j, k + 2))
                            mesh.polygon.append(tri)

                    self.meshes.append(mesh)

    def InitJoints(self):
        rootNode = self.scene.GetRootNode()
        for i in range(rootNode.GetChildCount()):
            node = rootNode.GetChild(i)
            self._InitJointsRecursively(node, 0, 0, -1)

    def _InitJointsRecursively(self, iNode, iDepth, myIndex, iParentIndex):
        if iNode.GetNodeAttribute() and iNode.GetNodeAttribute().GetAttributeType() \
            and iNode.GetNodeAttribute().GetAttributeType() == FbxNodeAttribute.EType.eSkeleton:
            currJoint = Joint()
            currJoint.mParentIndex = iParentIndex
            currJoint.mName = iNode.GetName()
            currJoint.node = iNode
            self.joints.append(currJoint)

        for i in range(iNode.GetChildCount()):
            self._InitJointsRecursively(iNode.GetChild(i), iDepth+1, len(self.joints), myIndex)

    def FindJointIndexUsingName(self, name):
        for i in range(len(self.joints)):
            if self.joints[i].mName == name:
                print(name, i)
                return i
        return -1

    def ProcessJointsAndAnimations(self, mesh):
        iNode = mesh.mesh.GetNode()
        lMesh = iNode.GetMesh()
        numOfDeformers = lMesh.GetDeformerCount()

        geometryTrasnform = self.GetGeometryTransformation(iNode)

        for deformerIndex in range(numOfDeformers):
            skin = lMesh.GetDeformer(deformerIndex)

            if not skin:
                continue

            numOfCluster = skin.GetClusterCount()
            for clusterIndex in range(numOfCluster):
                cluster = skin.GetCluster(clusterIndex)
                jointName = cluster.GetLink().GetName()
                jointIndex = self.FindJointIndexUsingName(jointName)

                globalBindposeInverseMatrix = FbxAMatrix()
                transformMatrix = FbxAMatrix()
                transformLinkMatrix = FbxAMatrix()
                cluster.GetTransformMatrix(transformMatrix)
                cluster.GetTransformLinkMatrix(transformLinkMatrix)

                globalBindposeInverseMatrix = transformLinkMatrix.Inverse()

                print(cluster)

                self.joints[jointIndex].mGlobalBindPoseInverse = globalBindposeInverseMatrix
                #self.joints[jointIndex].mGlobalBindPoseInverse = transformLinkMatrix.Inverse()
                #self.joints[jointIndex].mGlobalBindPoseInverse = self.joints[jointIndex].node.EvaluateGlobalTransform().Inverse()
                self.joints[jointIndex].mNode = cluster.GetLink()

                #PrintFbxAMatrix(self.joints[jointIndex].mGlobalBindPoseInverse)

                numOfIndices = cluster.GetControlPointIndicesCount()
                for i in range(numOfIndices):
                    currBlendingIndexWeightPair = BlendingIndexWeightPair(jointIndex, cluster.GetControlPointWeights()[i])
                    currBlendingIndexWeightPair.mBlendingIndex = jointIndex
                    currBlendingIndexWeightPair.mBlendingWeight = cluster.GetControlPointWeights()[i]    
                    mesh.vertices[cluster.GetControlPointIndices()[i]].blendingInfo.append(currBlendingIndexWeightPair)
                """
                # Now do some animation things
                currAnimStack = self.scene.GetSrcObject(0)
                animStackName = currAnimStack.GetName()
                self.AnimationName = animStackName
                takeInfo = self.scene.GetTakeInfo(animStackName)
                start = takeInfo.mLocalTimeSpan.GetStart()
                end = takeInfo.mLocalTimeSpan.GetStop()
                self.animationLength = end.GetFrameCount(FbxTime.eFrames24) - start.GetFrame(FbxTime.eFrames24)
                #currAnim = self.joints[jointIndex].mAnimation
                """

    def GetGeometryTransformation(self, iNode):
        lT = iNode.GetGeometricTranslation(FbxNode.EPivotSet.eSourcePivot)
        lr = iNode.GetGeometricRotation(FbxNode.EPivotSet.eSourcePivot)
        ls = iNode.GetGeometricScaling(FbxNode.EPivotSet.eSourcePivot)
        return FbxAMatrix(lT, lr, ls)

    def GetBoneMatrices(self):
        self.joints[0].mNode.EvaluateGlobalTransform()

        v = []
        for i in range(len(self.joints)):
            joint = self.joints[i]
            v += FbxAMatrix2Array(joint.mGlobalBindPoseInverse)
            #m = FbxAMatrix()
            #mat = joint.node.GetTransformLinkMatrix(m)
            #v += FbxAMatrix2Array(mat)
        return v

    def InitMaterial(self):
            for i in range(len(self.meshes)):
                for vertex in self.meshes[i].vertices:
                    vertex.matIdx = i

            for i in range(len(self.meshes)):
                lNode = self.meshes[i].mesh.GetNode()
                for j in range(lNode.GetMaterialCount()):
                    mat = Material()
                    mat.material = lNode.GetMaterial(j)
                    mat.diffuse = mat.material.Diffuse.Get()
                    self.matrials.append(mat)
    
    def GetVertices(self):
        v = []
        for mesh in self.meshes:
            controlPoints = mesh.mesh.GetControlPoints()
            for poly in mesh.polygon:
                for idx in poly:
                    v.append(controlPoints[idx][0])
                    v.append(controlPoints[idx][1])
                    v.append(controlPoints[idx][2])
        return v
    
    def GetVerticesMatIdx(self):
        v = []
        matIdx = 0
        for mesh in self.meshes:
            controlPointsCount = mesh.mesh.GetControlPointsCount()
            for poly in mesh.polygon:
                for idx in poly:
                    v.append(matIdx)
            matIdx += 1
        return v

    def GetDiffuse(self):
        v = []
        for mat in self.matrials:
            diff = mat.material.Diffuse.Get()
            v += diff
        return v
    
    def GetVertexBoneIds(self):
        v = []
        for mesh in self.meshes:
            for poly in mesh.polygon:
                for idx in poly:
                    blendingInfo = mesh.vertices[idx].blendingInfo
                    for i in range(4):
                        if i >= len(blendingInfo):
                            v.append(0)
                        else:
                            v.append(blendingInfo[i].index)
        return v

    def GetVertexBoneWeights(self):
        v = []
        for mesh in self.meshes:
            for poly in mesh.polygon:
                for idx in poly:
                    blendingInfo = mesh.vertices[idx].blendingInfo
                    for i in range(4):
                        if i >= len(blendingInfo):
                            v.append(0)
                        else:
                            v.append(blendingInfo[i].weight)
        return v


def PrintFbxAMatrix(mat):
    for i in range(4):
        for j in range(4):
            print(mat.Get(i, j), end=' ')
        print()

def FbxAMatrix2Array(mat):
    arr = []
    for i in range(16):
        arr.append(mat.Get(i // 4, i % 4))
    return arr

