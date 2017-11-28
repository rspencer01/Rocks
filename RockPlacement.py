import dent.Shaders as Shaders
import logging
import OpenGL.GL as gl
import numpy as np

transform_shader = Shaders.TransformFeedbackShader('rock_placement_feedback')
transform_shader.addProgram(gl.GL_VERTEX_SHADER, Shaders.ShaderFile('shaders/rock_placement/vertex.shd', gl.GL_VERTEX_SHADER))
Shaders.shaders['rock_placement_feedback'] = transform_shader
transform_shader.addProgram(gl.GL_GEOMETRY_SHADER, Shaders.ShaderFile('shaders/rock_placement/geometry.shd',gl.GL_GEOMETRY_SHADER))
transform_shader.addOutput('outValue')

transform_shader.build()
transform_shader.load()

input_sizes = []
render_ids = []
output_buffers = []

def initialise(buffer_sizes):
  for max_N in buffer_sizes:
    ids = np.zeros(max_N, dtype=[('id',np.int32,1)])
    ids['id'] = np.arange(max_N)

    render_id = transform_shader.setData(ids)
    output_buffer = transform_shader.getOutputBufferObject(render_id, max_N*16*4)

    input_sizes.append(max_N)
    render_ids.append(render_id)
    output_buffers.append(output_buffer)

def update(centre):
  counts = []
  for i in xrange(len(render_ids)):
    transform_shader['scan'] = int(input_sizes[i]**0.5)
    transform_shader['lodlevel'] = i
    transform_shader['centre'] = np.array([centre[0],centre[2]])
    counts.append(transform_shader.draw(gl.GL_POINTS, render_ids[i],output_buffers[i], input_sizes[i]))
  return counts
