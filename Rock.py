import numpy as np
import procgen.Rock
import dent.Shaders as Shaders
import dent.transforms
import OpenGL.GL as gl

shader = Shaders.getShader('rock', instance=True)

class Rock(object):
  def __init__(self):
    self.position = np.array([0,0.5,0],dtype=float)

    self.shader = shader

    self.meshdata, self.meshindices = procgen.Rock.get_rock_mesh(1)

    self.instances = np.zeros(0, dtype=[("model", np.float32, (4, 4))])

    self.renderID = None


  def addInstances(self, model):
    t = np.zeros(1, dtype=[("model", np.float32, (4, 4))])
    t[0] = model
    self.instances = np.append(self.instances, t)


  def freeze(self):
    self.renderID = self.shader.setData(self.meshdata,
                                        self.meshindices,
                                        self.instances)


  def display(self):
    if self.renderID is None:
      return
    self.shader.draw(gl.GL_TRIANGLES, self.renderID, len(self.instances))
