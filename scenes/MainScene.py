from dent.Scene import Scene
import dent.Texture as Texture
from dent.Object import Object
from dent.RenderStage import RenderStage
from dent.RectangleObjects import RectangleObject, BlankImageObject
from dent.ActionController import ActionController
import dent.Shaders
from dent.Shadows import Shadows
import numpy as np
import dent.transforms
import dent.messaging
import dent.args
import random

import OpenGL.GL as gl
import Rock

class MainScene(Scene):
  def __init__(self):
    super(MainScene, self).__init__()
    gl.glEnable(gl.GL_CULL_FACE)
    self.renderPipeline.stages += [
        RenderStage(render_func=self.display, aux_buffer=True),
        RenderStage(render_func=self.lighting_display   , clear_depth=False  , final_stage=True)]
    self.rock = Rock.Rock()
    self.camera.lockObject = self.rock
    self.camera.lockDistance = 4
    self.camera.move_hook = lambda x: \
      [x[0], max(0.5, x[1]), x[2]]

    self.floor = RectangleObject('floor')
    self.sky = BlankImageObject(0.4, 0.5, 0.6)

    dent.messaging.add_handler('timer', self.timer)

    self.time = 0.

    self.shadows = Shadows(self.render_all, self.rock, rng=5)
    self.shadows.shadowCamera.rotUpDown(0.5)

    self.lighting_rectangle = RectangleObject('lighting')
    self.lighting_rectangle.shader['colormap'] = Texture.COLORMAP_NUM
    self.lighting_rectangle.shader['normalmap'] = Texture.COLORMAP2_NUM
    self.lighting_rectangle.shader['positionmap'] = Texture.COLORMAP3_NUM

    self.add_rocks()

  def add_rocks(self):
    for i in xrange(100):
      t = np.eye(4, dtype=np.float32)
      dent.transforms.yrotate(t, (random.random()-.5)*360)
      dent.transforms.xrotate(t, (random.random()-.5)*30)
      dent.transforms.zrotate(t, (random.random()-.5)*30)
      dent.transforms.translate(t, (random.random()-.5)*100,
                                   0.3,
                                   (random.random()-.5)*100)
      self.rock.addInstances(t)

    self.rock.freeze()


  def timer(self, fps):
    # Simply move the sun around the sky
    sd = np.array(
      [np.sin(self.time),
        0.4,
        np.cos(self.time)])
    dent.Shaders.setUniform('sunDirection', -self.shadows.shadowCamera.direction)
    self.time += 1./fps

    self.shadows.shadowCamera.rotLeftRight(1./fps)
    self.shadows.render()

  def display(self, width, height, **kwargs):
    projection = dent.transforms.perspective(60.0, width/float(height), 0.3, 1e7)
    dent.Shaders.setUniform('projection', projection)

    self.camera.render()
    self.sky.display()
    self.render_all()

  def render_all(self):
    self.floor.display()
    self.rock.display()

  def lighting_display(self, previous_stage, **kwargs):
    previous_stage.displayColorTexture.load()
    previous_stage.displaySecondaryColorTexture.load()
    previous_stage.displayAuxColorTexture.load()
    self.lighting_rectangle.display()
