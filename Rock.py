import numpy as np
import procgen.Rock
import dent.Shaders as Shaders
import dent.transforms
import OpenGL.GL as gl

shader = Shaders.getShader('rock', instance=True)

class Rock(object):
  def __init__(self, instance_buffer, instance_count, detail):
    self.position = np.array([0,0.5,0],dtype=float)

    self.shader = shader

    self.meshdata, self.meshindices = procgen.Rock.get_rock_mesh(1,detail)

    self.instance_template = np.zeros(0, dtype=[("model", np.float32, (4, 4))])

    self.renderID = self.shader.setData(self.meshdata,
                                        self.meshindices,
                                        self.instance_template,
                                        instance_buffer)
    self.instance_count = instance_count


  def display(self):
    if self.renderID is None:
      return
    self.shader.draw(gl.GL_TRIANGLES, self.renderID, self.instance_count)
