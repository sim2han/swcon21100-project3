from OpenGL.GL import *
import OpenGL.GL.shaders
import glm
import numpy as np
import pygame
from pygame.locals import *
from fbxtest import *
from FbxCommon import *
from fbx import *
import FbxLoader

vertex_shader = """
#version 430

layout(location = 0) in vec3 position;
layout(location = 1) in vec4 normal;
layout(location = 2) in vec2 uv;

layout(location = 4) in int matIdx;

layout(location = 5) in ivec4 vertexBoneIds;
layout(location = 7) in vec4 vertexBoneWeights;

const int MAX_MATERIAL_COUNT = 2;
const int MAX_BONES = 64;

uniform vec3 diffuse[MAX_MATERIAL_COUNT];
uniform mat4 mvp;
uniform mat4 bones[MAX_BONES];

out vec3 newColor;

void main() {
    vec4 totalLocalPos = vec4(0.0);

    totalLocalPos += (bones[vertexBoneIds.x] * vec4(position, 1.0)) * vertexBoneWeights.x;
    //gl_Position = mvp * totalLocalPos + vec4(position, 1.0); // Not Work!

    gl_Position = mvp * vec4(position, 1.0);

    newColor = diffuse[matIdx];

    if (vertexBoneIds[0] == 60)
        newColor = vec3(1.0, 1.0, 0.0);
}
"""

fragment_shader = """
#version 430

in vec3 newColor;
out vec4 outColor;

void main() {
    outColor = vec4(newColor, 1.0f);
}
"""

def main():
    # START FBX INITIALIZING
    
    (sdkManager, scene) = InitializeSdkObjects()
    result = LoadScene(sdkManager, scene, "sample.fbx")
    if not result:
        print("Fail to load fbx")
        return
    
    loader = FbxLoader.FbxLoader()
    loader.InitScene(scene)
    loader.InitMesh()
    loader.InitMaterial()
    loader.InitJoints()

    loader.ProcessJointsAndAnimations(loader.meshes[0])
    loader.ProcessJointsAndAnimations(loader.meshes[1])

    vertexArray = loader.GetVertices()
    vertexArray = np.array(vertexArray, dtype=np.float32)
    
    vertexBoneIds = loader.GetVertexBoneIds()
    vertexBoneIds = np.array(vertexBoneIds, dtype=np.int32)
    vertexBoneWeights = loader.GetVertexBoneWeights()
    vertexBoneWeights = np.array(vertexBoneWeights, dtype=np.float32)
    
    uvArray = GetUvArray(scene)

    matidx = loader.GetVerticesMatIdx()
    matidx = np.array(matidx, dtype=np.int32)

    diff = loader.GetDiffuse()
    diff = np.array(diff, dtype=np.float32)
    
    bonePoses = loader.GetBoneMatrices()
    bonePoses = np.array(bonePoses, dtype=np.float32)
    

    # START PYGAME INITIALIZING
    pygame.init()
    surface = pygame.display.set_mode((800, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OPENGL TEST")

    # START OPENGL INITIALIZING
    glEnable(GL_DEPTH_TEST)

    v_shader = OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    f_shader = OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    shader = OpenGL.GL.shaders.compileProgram(v_shader, f_shader)
    
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexArray) * 4, vertexArray, GL_STATIC_DRAW)

    position = 0
    glBindAttribLocation(shader, position, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
    
    vbo2 = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo2)
    glBufferData(GL_ARRAY_BUFFER, len(uvArray) * 4, uvArray, GL_STATIC_DRAW)

    uv = 1
    glBindAttribLocation(shader, uv, "uv")
    glVertexAttribPointer(uv, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(uv)
    
    vbo3 = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo3)
    glBufferData(GL_ARRAY_BUFFER, len(matidx) * 4, matidx, GL_STATIC_DRAW)
    
    mat = 4
    glBindAttribLocation(shader, mat, "matIdx")
    glVertexAttribPointer(mat, 1, GL_FLOAT, GL_FALSE, 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(mat)
    
    vbo5 = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo5)
    glBufferData(GL_ARRAY_BUFFER, len(vertexBoneIds) * 4, vertexBoneIds, GL_STATIC_DRAW)
    
    boneids = 5
    glBindAttribLocation(shader, boneids, "vertexBoneIds")
    glVertexAttribPointer(boneids, 1, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
    glEnableVertexAttribArray(boneids)

    vbo7 = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo7)
    glBufferData(GL_ARRAY_BUFFER, len(vertexBoneWeights) * 4, vertexBoneWeights, GL_STATIC_DRAW)
    
    boneweights = 7
    glBindAttribLocation(shader, boneweights, "vertexBoneWeights")
    glVertexAttribPointer(boneweights, 1, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
    glEnableVertexAttribArray(boneweights)
    

    glUseProgram(shader)

    diffuseLoc = glGetUniformLocation(shader, "diffuse")
    glUniform3fv(diffuseLoc, len(diff) // 3, diff)
    
    boneLoc = glGetUniformLocation(shader, "bones")
    glUniformMatrix4fv(boneLoc, len(bonePoses) // 16, GL_FALSE, bonePoses)
    
    cam = glm.vec3(-20, 20, -20)
    cam_rot = glm.vec3(0.0, 0.0, 0.0)

    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        keys = pygame.key.get_pressed()

        if not keys[pygame.K_LSHIFT]:
            camMoveSpeed = 1.0
            camRotSpeed = 0.1
        else:
            camMoveSpeed = 2.0
            camRotSpeed = 0.1

        if keys[pygame.K_i]:
            cam_rot[1] += camRotSpeed
        if keys[pygame.K_k]:
            cam_rot[1] -= camRotSpeed
        if keys[pygame.K_l]:
            cam_rot[0] += camRotSpeed
        if keys[pygame.K_j]:
            cam_rot[0] -= camRotSpeed

        camForwardVector = glm.vec3(np.cos(cam_rot[0]), np.sin(cam_rot[1]), np.sin(cam_rot[0]))
        
        cameraDirection = camForwardVector
        cameraUp = glm.vec3(0.0, 1.0, 0.0)
        cameraRight = glm.normalize(glm.cross(cameraUp, cameraDirection))
        cameraUp = glm.cross(cameraDirection, cameraRight)

        if keys[pygame.K_w]:
            cam += camForwardVector * camMoveSpeed
        if keys[pygame.K_s]:
            cam -= camForwardVector * camMoveSpeed
        if keys[pygame.K_a]:
            cam += cameraRight * camMoveSpeed
        if keys[pygame.K_d]:
            cam -= cameraRight * camMoveSpeed
        if keys[pygame.K_q]:
            cam[1] += camMoveSpeed
        if keys[pygame.K_e]:
            cam[1] -= camMoveSpeed

        cameraPos = cam

        view = glm.lookAt(cameraPos, cameraPos + cameraDirection, cameraUp)
        proj = glm.perspective(glm.radians(90), 1.0, 0.1, 1000)

        mvp = proj * view;
        mvp = glm.array(mvp)

        mvpLocation = glGetUniformLocation(shader, "mvp")
        glUniformMatrix4fv(mvpLocation, 1, GL_FALSE, mvp.ptr)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #DrawMesh(shader, meshs[0])
        #DrawMesh(shader, meshs[1])
        glDrawArrays(GL_TRIANGLES, 0, len(vertexArray) // 3)

        pygame.display.flip()
        pygame.time.wait(30)

    pygame.quit()




def DrawMesh(shader, pMesh):
    lPolygonCount = pMesh.GetPolygonCount()

    print("Draw Mesh : ", pMesh.GetName())

    # CHECK MATERIAL TYPE
    lIsAllSame = True
    for l in range(pMesh.GetLayerCount()):
        lLayerMaterial = pMesh.GetLayer(l).GetMaterials()
        if lLayerMaterial:
            if lLayerMaterial.GetMappingMode() == FbxLayerElement.EMappingMode.eByPolygon:
                lIsAllSame = False
                break
        
    if lIsAllSame:  
        for l in range(pMesh.GetLayerCount()):
            lLayerMaterial = pMesh.GetLayer(l).GetMaterials()
            if lLayerMaterial.GetMappingMode() == FbxLayerElement.EMappingMode.eAllSame:

                lMaterial = pMesh.GetNode().GetMaterial(lLayerMaterial.GetIndexArray().GetAt(0))
                lMatid = lLayerMaterial.GetIndexArray().GetAt(0)
                diffuse = glm.array(glm.vec3(*lMaterial.Diffuse.Get()))
                diffuseLocation = glGetUniformLocation(shader, "diffuse")
                glUniform3fv(diffuseLocation, 1, diffuse.ptr)

                vertexArray = GetVerticesFromMesh(pMesh)

                vbo = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, vbo)
                glBufferData(GL_ARRAY_BUFFER, len(vertexArray) * 4, vertexArray, GL_STATIC_DRAW)

                position = 0
                glBindAttribLocation(shader, position, "position")
                glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
                glEnableVertexAttribArray(position)

                glDrawArrays(GL_TRIANGLES, 0, len(vertexArray) // 3)

                glBindBuffer(GL_ARRAY_BUFFER, 0)

    else:
        print("Material By Polygon type not supported")
        return



if __name__ == "__main__":
    main()

