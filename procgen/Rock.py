import numpy as np
import noise
import utils
import dent.assets

def make_tesselated_triangle(p1,p2,p3,offset=0, N=50):
  ans = []
  indices = []
  for i in xrange(N+1):
    for j in xrange(N+1-i):
      xi = float(i)/N
      xj = float(j)/N
      xk = 1-xi-xj
      ans.append(xi*p1+xj*p2+xk*p3)
  c = offset
  for i in xrange(N+1):
    for j in xrange(N-i):
      indices+=[c+1,c,c+1+(N-i)]
      if j>0:
        indices+=[c,c+(N-i),c+1+(N-i)]
      c+=1
    c+=1
  return ans, indices

def make_tetrahedron(N=50):
  corners = map(np.array,[
      (1, 0, -2**(-.5)),
      (-1, 0, -2**(-.5)),
      (0, 1, 2**(-.5)),
      (0, -1, 2**(-.5))])
  verts , I = make_tesselated_triangle(corners[1],corners[2],corners[0],0,N)
  v, i = make_tesselated_triangle(corners[1],corners[3],corners[2],len(verts),N)
  verts += v
  I += i
  v, i = make_tesselated_triangle(corners[3],corners[0],corners[2],len(verts),N)
  verts += v
  I += i
  v, i = make_tesselated_triangle(corners[0],corners[3],corners[1],len(verts),N)
  verts += v
  I += i
  return utils.remove_duplicates(verts,I)

def slice_off(vertices):
  d = np.random.rand(3)*2-.5
  while np.linalg.norm(d)>1:
    d = np.random.rand(3)*2-.5
  d /= np.linalg.norm(d)
  r = np.random.rand(1)*0.3+0.6
  for i in xrange(len(vertices)):
    if d.dot(vertices[i]) > r:
      vertices[i] -= d * d.dot(vertices[i])
      vertices[i] += d*r

def disturb(vertices, amount=0.1, scale=1):
  for i in xrange(len(vertices)):
    l = np.linalg.norm(vertices[i])
    vertices[i] /= l
    l+=noise.snoise3(*vertices[i]*scale)*amount
    vertices[i] *= l

def crackle(vertices, amount=0.1,scale=1):
  for i in xrange(len(vertices)):
    l = np.linalg.norm(vertices[i])
    vertices[i] /= l
    l+= np.arctan(noise.snoise3(
      vertices[i][0]*scale/10,
      vertices[i][1]*scale,
      vertices[i][2]*scale/10,
      )*100)*amount
    vertices[i] *= l

def smooth(vertices, indices):
  for i in xrange(len(indices)/3):
    m = (vertices[indices[i*3  ]]+\
        vertices[indices[i*3+1]]+\
        vertices[indices[i*3+2]])/3
    vertices[indices[i*3  ]] = vertices[indices[i*3  ]]*.9+m*.1
    vertices[indices[i*3+1]] = vertices[indices[i*3+1]]*.9+m*.1
    vertices[indices[i*3+2]] = vertices[indices[i*3+2]]*.9+m*.1

def get_rock_mesh(seed=None):
  np.random.seed(seed)
  verts, I = dent.assets.getAsset('tetrahedron', make_tetrahedron, (10,), True)

  data = np.zeros(len(verts), dtype=[("position", np.float32, 3),
                                     ("normal", np.float32, 3)])
  data['position'] = verts

  for i in xrange(len(data)):
    data['position'][i] /= np.linalg.norm(data['position'][i])

  disturb(data['position'],0.1)
  for i in xrange(len(data)):
    data['position'][i][0] *= 1.2
    data['position'][i][2] *= 1.5
  for i in xrange(5):
    slice_off(data['position'])
  smooth(data['position'],I)
  crackle(data['position'],0.01,2)
  disturb(data['position'],0.02,4)

  utils.make_normals(data, I)
  return data, np.array(I, dtype=np.int32)
