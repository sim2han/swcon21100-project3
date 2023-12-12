import fbx
from fbx import FbxLayerElement
from fbx import FbxSurfaceMaterial
from fbx import FbxLayeredTexture
from fbx import FbxTexture
from fbx import FbxCriteria
from fbx import FbxAMatrix
from FbxCommon import *
from DisplayCommon import *
import numpy as np

numTabs = 0

def PrintTabs():
    for i in range(0, numTabs):
        print('  ', end='')

def GetAttribTypeName(type):
    if type == fbx.FbxNodeAttribute.EType.eUnknown:
        return "undientifield"
    elif type == fbx.FbxNodeAttribute.EType.eNull:
        return "null"
    elif type == fbx.FbxNodeAttribute.EType.eMarker:
        return "marker"
    elif type == fbx.FbxNodeAttribute.EType.eSkeleton:
        return "skeleton"
    elif type == fbx.FbxNodeAttribute.EType.eMesh:
        return "mesh"
    elif type == fbx.FbxNodeAttribute.EType.eNurbs:
        return "nurbs"
    elif type == fbx.FbxNodeAttribute.EType.ePatch:
        return "patch"
    elif type == fbx.FbxNodeAttribute.EType.eCamera:
        return "camera"
    elif type == fbx.FbxNodeAttribute.EType.eCameraStereo:
        return "stereo"
    elif type == fbx.FbxNodeAttribute.EType.eCameraSwitcher:
        return "camera switcher"
    elif type == fbx.FbxNodeAttribute.EType.eLight:
        return "light"
    elif type == fbx.FbxNodeAttribute.EType.eOpticalRefernce:
        return "optical reference"
    elif type == fbx.FbxNodeAttribute.EType.eOpticalMarker:
        return "marker"
    elif type == fbx.FbxNodeAttribute.EType.eNurbsCurve:
        return "nurbs curve"
    elif type == fbx.FbxNodeAttribute.EType.eTrimNurbsSurface:
        return "trim nurbs surface"
    elif type == fbx.FbxNodeAttribute.EType.eBoundary:
        return "boundary"
    elif type == fbx.FbxNodeAttribute.EType.eNurbsSurface:
        return "nurbs surface"
    elif type == fbx.FbxNodeAttribute.EType.eShape:
        return "shape"
    elif type == fbx.FbxNodeAttribute.EType.eLODGroup:
        return "lodgroup"
    elif type == fbx.FbxNodeAttribute.EType.eSubDiv:
        return "subdiv"
    else:
        return "Unknown"

def PrintAttribute(pAttribute):
    if not pAttribute:
        return
    
    typeName = GetAttribTypeName(pAttribute.GetAttributeType())
    attrName = pAttribute.GetName()
    print("<attribute type={}, name={}>".format(typeName, attrName))

def PrintNode(node):
    global numTabs
    PrintTabs()
    nodeName = node.GetName()
    translation = node.LclTranslation.Get()
    rotation = node.LclRotation.Get()
    scaling = node.LclScaling.Get()

    string = "<node name={} translation=({}, {}, {}) rotation=({}, {}, {}) scaling=({}, {}, {})>".format(
        nodeName,
        translation[0], translation[1], translation[2],
        rotation[0], rotation[1], rotation[2],
        scaling[0], scaling[1], scaling[2]
    )

    print(string)
    numTabs += 1

    for i in range(0, node.GetNodeAttributeCount()):
        PrintAttribute(node.GetNodeAttributeByIndex(i))

    for j in range(0, node.GetChildCount()):
        PrintNode(node.GetChild(j))
    
    numTabs -= 1
    PrintTabs()
    print("</node>")


def main():
    filepath = "cube.fbx"

    manager = fbx.FbxManager.Create()

    ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
    manager.SetIOSettings(ios)

    importer = fbx.FbxImporter.Create( manager, 'myImporter')

    if not importer.Initialize(filepath, -1, manager.GetIOSettings()):
        print("Call to Initialize() failed")
        print("Error returnd: " + importer.GetStatus().GetErrorString())
        exit(-1)

    scene = fbx.FbxScene.Create(manager, "myScene")
    importer.Import(scene)
    importer.Destroy()

    rootNode = scene.GetRootNode()
    if rootNode:
        for i in range(rootNode.GetChildCount()):
            lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
            if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                lMesh = rootNode.GetChild(i).GetNodeAttribute()
                print("Name : ", rootNode.GetChild(i).GetName())
                print("Point Count : ", lMesh.GetControlPointsCount())

                lPolygonCount = lMesh.GetPolygonCount()
                lControlPoints = lMesh.GetControlPoints()

                print("Polygons")

                vertexId = 0
                for i in range(lPolygonCount):
                    print(" Polygon ", i)

                    # polygon can have multiple vertices. for example, trangle or rectangle...
                    lPolygonSize = lMesh.GetPolygonSize(i)

                    for j in range(lPolygonSize):
                        lControlPointIndex = lMesh.GetPolygonVertex(i, j)

                        print(" coordinates: ", lControlPoints[lControlPointIndex][0],
                              lControlPoints[lControlPointIndex][1],
                              lControlPoints[lControlPointIndex][2])

def GetMatIdxArray(scene):
    matIdxArray = []
    matCount = 0

    rootNode = scene.GetRootNode()
    if rootNode:
        for i in range(rootNode.GetChildCount()):
            lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
            if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                lMesh = rootNode.GetChild(i).GetNodeAttribute()
                lNode = lMesh.GetNode()
                lPolygonCount = lMesh.GetPolygonCount()

                for i in range(lPolygonCount):

                    lPolygonSize = lMesh.GetPolygonSize(i)

                    for j in range(lPolygonSize - 2):
                        matIdxArray.append(matCount)
                        matIdxArray.append(matCount)
                        matIdxArray.append(matCount)
                
                matCount += 1

    return np.array(matIdxArray, dtype=np.int32)

def GetDiffuseArray(scene):
    diffuseArray = []

    rootNode = scene.GetRootNode()
    if rootNode:
        for i in range(rootNode.GetChildCount()):
            lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
            if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                lMesh = rootNode.GetChild(i).GetNodeAttribute()
                lNode = lMesh.GetNode()
                matCount = lNode.GetMaterialCount()

                for j in range(matCount):
                    mat = lNode.GetMaterial(j)
                    diffuseArray.append(mat.Diffuse.Get()[0])
                    diffuseArray.append(mat.Diffuse.Get()[1])
                    diffuseArray.append(mat.Diffuse.Get()[2])
    
    return np.array(diffuseArray, dtype=np.float32)


def GetVertexArray(scene):
    vertexArray = []

    rootNode = scene.GetRootNode()
    if rootNode:
        for i in range(rootNode.GetChildCount()):
            lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
            if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                lMesh = rootNode.GetChild(i).GetNodeAttribute()
                print("Name : ", rootNode.GetChild(i).GetName())
                print("Point Count : ", lMesh.GetControlPointsCount())

                lPolygonCount = lMesh.GetPolygonCount()
                lControlPoints = lMesh.GetControlPoints()

                print("Polygons")

                #vertexId = 0
                for i in range(lPolygonCount):

                    # polygon can have multiple vertices. for example, trangle or rectangle...
                    # but in this case, we use only first three vertices.
                    lPolygonSize = lMesh.GetPolygonSize(i)

                    triArray = []

                    zeroPointIndex = lMesh.GetPolygonVertex(i, 0)
                    for j in range(lPolygonSize - 2):
                        vertexArray.append(lControlPoints[zeroPointIndex][0])
                        vertexArray.append(lControlPoints[zeroPointIndex][1])
                        vertexArray.append(lControlPoints[zeroPointIndex][2])

                        lControlPointIndex = lMesh.GetPolygonVertex(i, j + 1)
                        vertexArray.append(lControlPoints[lControlPointIndex][0])
                        vertexArray.append(lControlPoints[lControlPointIndex][1])
                        vertexArray.append(lControlPoints[lControlPointIndex][2])

                        lControlPointIndex = lMesh.GetPolygonVertex(i, j + 2)
                        vertexArray.append(lControlPoints[lControlPointIndex][0])
                        vertexArray.append(lControlPoints[lControlPointIndex][1])
                        vertexArray.append(lControlPoints[lControlPointIndex][2])

    return np.array(vertexArray, dtype=np.float32)

def GetUvArray(scene):
    uvArray = []

    rootNode = scene.GetRootNode()
    if rootNode:
        for i in range(rootNode.GetChildCount()):
            lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
            if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                lMesh = rootNode.GetChild(i).GetNodeAttribute()

                lPolygonCount = lMesh.GetPolygonCount()
                lControlPoints = lMesh.GetControlPoints()

                vertexId = 0
                for i in range(lPolygonCount):
                    #print(" Polygon ", i)

                    # polygon can have multiple vertices. for example, trangle or rectangle...\
                    lPolygonSize = lMesh.GetPolygonSize(i)

                    controlPointIndices = []
                    for j in range(lPolygonSize - 2):
                        controlPointIndices.append(0)
                        controlPointIndices.append(j + 1)
                        controlPointIndices.append(j + 2)

                    #for j in range(lPolygonSize):
                    for j in controlPointIndices:
                        lControlPointIndex = lMesh.GetPolygonVertex(i, j)

                        for l in range(lMesh.GetLayerCount()):
                            leUV = lMesh.GetLayer(l).GetUVs()
                            if leUV:
                                header = "            Texture UV (on layer %d): " % l 

                                if leUV.GetMappingMode() == FbxLayerElement.EMappingMode.eByControlPoint:
                                    if leUV.GetReferenceMode() == FbxLayerElement.EReferenceMode.eDirect:
                                        #Display2DVector(header, leUV.GetDirectArray().GetAt(lControlPointIndex))
                                        uvArray.append(leUV.GetDirectArray().GetAt(lControlPointIndex)[0])
                                        uvArray.append(leUV.GetDirectArray().GetAt(lControlPointIndex)[1])

                                    elif leUV.GetReferenceMode() == FbxLayerElement.EReferenceMode.eIndexToDirect:
                                        id = leUV.GetIndexArray().GetAt(lControlPointIndex)
                                        #Display2DVector(header, leUV.GetDirectArray().GetAt(id))
                                        uvArray.append(leUV.GetDirectArray().GetAt(id)[0])
                                        uvArray.append(leUV.GetDirectArray().GetAt(id)[1])

                                elif leUV.GetMappingMode() ==  FbxLayerElement.EMappingMode.eByPolygonVertex:
                                    lTextureUVIndex = lMesh.GetTextureUVIndex(i, j)
                                    if leUV.GetReferenceMode() == FbxLayerElement.EReferenceMode.eDirect or \
                                    leUV.GetReferenceMode() == FbxLayerElement.EReferenceMode.eIndexToDirect:
                                        #Display2DVector(header, leUV.GetDirectArray().GetAt(lTextureUVIndex))
                                        uvArray.append(leUV.GetDirectArray().GetAt(lTextureUVIndex)[0])
                                        uvArray.append(leUV.GetDirectArray().GetAt(lTextureUVIndex)[1])
                                
                                elif leUV.GetMappingMode() == FbxLayerElement.EMappingMode.eByPolygon or \
                                    leUV.GetMappingMode() == FbxLayerElement.eAllSame or \
                                    leUV.GetMappingMode() ==  FbxLayerElement.eNone:
                                    # doesn't make much sense for UVs
                                    pass
                    # # end for layer
                    vertexId += 1

    return np.array(uvArray, dtype=np.float32)

def LoadScene():
    pass

def GetMaterialsOnScene(scene):
    mats = []
    rootNode = scene.GetRootNode()
    if rootNode:
        for i in range(rootNode.GetChildCount()):
            lAttributeType = (rootNode.GetChild(i).GetNodeAttribute().GetAttributeType())
            if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                mats.append(*GetMaterials(rootNode.GetChild(i)))

    return mats   

def GetMaterials(node):
    mats = []
    geometry = node.GetNodeAttribute()

    materialCount = 0
    node = None
    if geometry:
        node = geometry.GetNode()
        if node:
            materialCount = node.GetMaterialCount()
    
    for l in range(geometry.GetLayerCount()):
        leMat = geometry.GetLayer(l).GetMaterials()
        if leMat:
            if leMat.GetReferenceMode() == fbx.FbxLayerElement.EReferenceMode.eIndex:
                continue
        
        if materialCount > 0:
            for lCount in range(materialCount):
                mats.append(node.GetMaterial(lCount))

    return mats

def GetMeshsOnScene(pScene):
    meshs = []
    lNode = pScene.GetRootNode()

    if lNode:
        for i in range(lNode.GetChildCount()):
            lChildNode = lNode.GetChild(i)

            if lChildNode.GetNodeAttribute() == None:
                continue
            else:
                lAttributeType = lChildNode.GetNodeAttribute().GetAttributeType()

                if lAttributeType == fbx.FbxNodeAttribute.EType.eMesh:
                    meshs.append(lChildNode.GetNodeAttribute())
    
    return meshs

class Material:
    def __init__(self):
        self.Name = "Default"
        self.Ambient = None
        self.Diffuse = None
        self.Sepcular = None
        self.Emissive = None
        self.Opacity = None
        self.Shininess =  None
        self.Reflectivity = None
        self.ShadingModel = None

def ProcessSkeletonHierarchy(rootNode):
    for i in range(rootNode.GetChildCount()):
        node = rootNode.GetChild(i)
        ProcessSkeletonHierarchyRecursively(node, 0, 0, -1)

class Joint:
    def __init__(self):
        pass

class BlendingIndexWeightPair:
    def __init__(self):
        pass

joints = []
blendingInfo = []
for i in range(100000):
    blendingInfo.append([])

def ProcessSkeletonHierarchyRecursively(iNode, iDepth, myIndex, iParentIndex):
    if iNode.GetNodeAttribute() and iNode.GetNodeAttribute().GetAttributeType() \
        and iNode.GetNodeAttribute().GetAttributeType() == FbxNodeAttribute.EType.eSkeleton:
        currJoint = Joint()
        currJoint.mParentIndex = iParentIndex
        currJoint.mName = iNode.GetName()
        joints.append(currJoint)

    for i in range(iNode.GetChildCount()):
        ProcessSkeletonHierarchyRecursively(iNode.GetChild(i), iDepth+1, len(joints), myIndex)

def ProcessJointsAndAnimations(iNode):
    mesh = iNode.GetMesh()
    numOfDeformers = mesh.GetDeformerCount()

    for deformerIndex in range(numOfDeformers):
        skin = mesh.GetDeformer(deformerIndex)

        if not skin:
            continue

        numOfCluster = skin.GetClusterCount()
        for clusterIndex in range(numOfCluster):
            cluster = skin.GetCluster(clusterIndex)
            jointName = cluster.GetLink().GetName()
            print(jointName)
            #jointIndex = FindJointIndexUsingName(jointName)
            jointIndex = clusterIndex
            globalBindposeInverseMatrix = FbxAMatrix()
            transformMatrix = FbxAMatrix()
            transformLinkMatrix = FbxAMatrix()
            cluster.GetTransformMatrix(transformMatrix)

            cluster.GetTransformLinkMatrix(transformLinkMatrix)

            globalBindposeInverseMatrix = transformLinkMatrix.Inverse() * transformMatrix

            joints[jointIndex].mGlobalBindPoseInverse = globalBindposeInverseMatrix
            joints[jointIndex].mNode = cluster.GetLink()

            print(joints[jointIndex].mGlobalBindPoseInverse)
            PrintFbxAMatrix(joints[jointIndex].mGlobalBindPoseInverse)

            numOfIndices = cluster.GetControlPointIndicesCount()
            currBlendingIndexWeightPair = BlendingIndexWeightPair()
            currBlendingIndexWeightPair.mBlendingIndex = jointIndex
            currBlendingIndexWeightPair.mBlendingIndex = cluster.GetControlPointWeights()
                
            for i in range(numOfIndices):
                #if not blendingInfo[cluster.GetControlPointIndices()[i]]:
                #    blendingInfo[cluster.GetControlPointIndices()[i]] = []
                blendingInfo[cluster.GetControlPointIndices()[i]].append(currBlendingIndexWeightPair)
                
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


def CreateVertexLinkData(pMesh):
    lControlPointCount = pMesh.GetControlPointsCount()
    vertices = []
    for i in range(lControlPointCount):
        v = vertex()
        v.id = i
        vertices.append(v)

    lSkinCount = pMesh.GetDeformerCount(fbx.FbxDeformer.EDeformerType.eSkin)

    for i in range(lSkinCount):
        lClusterCount = pMesh.GetDeformer(i, fbx.FbxDeformer.EDeformerType.eSkin).GetClusterCount()
        for j in range(lClusterCount):
            lCluster = pMesh.GetDeformer(i, fbx.FbxDeformer.EDeformerType.eSkin).GetCluster(j)

            if lCluster.GetLink():
                pass
                #DisplayString("Name: ", lCluster.GetLink().GetName())

            lIndexCount = lCluster.GetControlPointIndicesCount()
            lIndices = lCluster.GetControlPointIndices()
            lWeights = lCluster.GetControlPointWeights()

            for k in range(lIndexCount):
                vertices[lIndices[k]].linkedBones.append((lCluster.GetLink().GetName(), lWeights[k]))

    return vertices


def fbx_trim_keys(scene, start, end, take_buffer=10):
    # Get animation stack and associated layer
    stack = scene.GetCurrentAnimationStack()
    layer = stack.GetSrcObject()

    # Build FbxTimeSpan class for keys that should be saved
    anim_start = FbxTime()
    anim_start.SetFrame(start - take_buffer)
    anim_end = FbxTime()
    anim_end.SetFrame(end + take_buffer)
    anim_range = FbxTimeSpan(anim_start, anim_end)

    # Iterate through all animation nodes in the layer
    for l in range(layer.GetMemberCount()):
        anim_node = layer.GetMember(l)
        # Check node has keys
        if anim_node.IsAnimated():
            # Each node has a curve for every animated attribute
            for c in range(anim_node.GetChannelsCount()):
                anim_curve = anim_node.GetCurve(c)
                anim_curve.KeyModifyBegin()
                # Iterate though every key on a given curve
                for k in reversed(range(anim_curve.KeyGetCount())):
                    key_time = anim_curve.KeyGetTime(k)
                    # Check if key's time is not inside the range to save
                    if not anim_range.IsInside(key_time):
                        anim_curve.KeyRemove(k)

                anim_curve.KeyModifyEnd()

def fbx_name_take(scene, name):
    stack = scene.GetCurrentAnimationStack()
    stack.SetName(name)


def GetVerticesFromMesh(pMesh):
    vertexArray = []

    lPolygonCount = pMesh.GetPolygonCount()
    lControlPoints = pMesh.GetControlPoints()

    for i in range(lPolygonCount):
        lPolygonSize = pMesh.GetPolygonSize(i)

        zeroPointIndex = pMesh.GetPolygonVertex(i, 0)
        for j in range(lPolygonSize - 2):
            vertexArray.append(lControlPoints[zeroPointIndex][0])
            vertexArray.append(lControlPoints[zeroPointIndex][1])
            vertexArray.append(lControlPoints[zeroPointIndex][2])

            lControlPointIndex = pMesh.GetPolygonVertex(i, j + 1)
            vertexArray.append(lControlPoints[lControlPointIndex][0])
            vertexArray.append(lControlPoints[lControlPointIndex][1])
            vertexArray.append(lControlPoints[lControlPointIndex][2])

            lControlPointIndex = pMesh.GetPolygonVertex(i, j + 2)
            vertexArray.append(lControlPoints[lControlPointIndex][0])
            vertexArray.append(lControlPoints[lControlPointIndex][1])
            vertexArray.append(lControlPoints[lControlPointIndex][2])
    
    return np.array(vertexArray, dtype=np.float32)