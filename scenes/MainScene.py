import RockPlacement
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
        RenderStage(render_func=self.display),
        RenderStage(render_func=self.lighting_display   , clear_depth=False  , final_stage=True)]

    RockPlacement.initialise([3*3,9*9,21*21,51*51])
    self.rock_lod_0 = Rock.Rock(RockPlacement.output_buffers[0], 9,35)
    self.rock_lod_1 = Rock.Rock(RockPlacement.output_buffers[1], 81,14)
    self.rock_lod_2 = Rock.Rock(RockPlacement.output_buffers[2], 400,7)
    self.rock_lod_3 = Rock.Rock(RockPlacement.output_buffers[3], 51*51,4)
    self.camera.lockObject = self.rock_lod_0
    self.camera.lockDistance = 4
    self.camera.move_hook = lambda x: \
      [x[0], max(0.5, x[1]), x[2]]
    self.camera.speed = 50.

    self.floor = RectangleObject('floor')
    self.sky = BlankImageObject(0.4, 0.5, 0.6)

    dent.messaging.add_handler('timer', self.timer)
    dent.messaging.add_handler('keyboard', self.key)

    self.time = 0.
    self.timercount = 0

    self.shadows = Shadows(self.render_all, self.camera, rng=5)
    self.shadows.shadowCamera.rotUpDown(0.5)

    self.lighting_rectangle = RectangleObject('lighting')
    self.lighting_rectangle.shader['colormap'] = Texture.COLORMAP_NUM
    self.lighting_rectangle.shader['normalmap'] = Texture.COLORMAP2_NUM
    self.lighting_rectangle.shader['positionmap'] = Texture.COLORMAP3_NUM

  def timer(self, fps):
    self.time += 1./fps
    self.timercount += 1

    if self.timercount % 5 == 0:
      counts = RockPlacement.update(self.camera.position)
      self.rock_lod_0.instance_count = counts[0]
      self.rock_lod_1.instance_count = counts[1]
      self.rock_lod_2.instance_count = counts[2]
      self.rock_lod_3.instance_count = counts[3]
    # Simply move the sun around the sky
    sd = np.array(
      [np.sin(self.time),
        0.4,
        np.cos(self.time)])
    dent.Shaders.setUniform('sunDirection', -self.shadows.shadowCamera.direction)

    self.shadows.shadowCamera.rotLeftRight(1./fps)
    self.shadows.render()

  def key(self, key):
    if key == 'l':
      print "D"
      if self.camera.lockObject:
        self.camera.lockObject = None
      else:
        self.camera.lockObject = self.rock_lod_0

  def display(self, width, height, **kwargs):
    projection = dent.transforms.perspective(60.0, width/float(height), 0.3, 1e7)
    dent.Shaders.setUniform('projection', projection)

    self.camera.render()
    self.sky.display()
    self.render_all()

  def render_all(self):
    self.floor.display()
    self.rock_lod_0.display()
    self.rock_lod_1.display()
    self.rock_lod_2.display()
    self.rock_lod_3.display()

  def lighting_display(self, previous_stage, **kwargs):
    previous_stage.displayColorTexture.load()
    previous_stage.displaySecondaryColorTexture.load()
    previous_stage.displayAuxColorTexture.load()
    self.lighting_rectangle.display()
