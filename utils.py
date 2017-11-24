import numpy as np

def make_normals(data, indices):
  for i in xrange(len(indices)/3):
    p1 = data['position'][indices[i*3  ]]
    p2 = data['position'][indices[i*3+1]]
    p3 = data['position'][indices[i*3+2]]
    n = np.cross(p3-p2,p1-p2)
    n/=np.linalg.norm(n)
    data['normal'][indices[i*3  ]] = n
    data['normal'][indices[i*3+1]] = n
    data['normal'][indices[i*3+2]] = n

def remove_duplicates(data, indices):
  order = range(len(data))
  order.sort(lambda x,y: 1 if data[x][0]>
                              data[y][0] else -1)
  for i in xrange(len(order)-1):
    k = i
    while abs(data[order[i]][0] - data[order[k]][0] ) < 0.1:
      if np.linalg.norm(data[order[i]] - data[order[k]]) < 0.01:
        for j in xrange(len(indices)):
          if indices[j] == order[k]:
            indices[j] = order[i]
      k+=1
      if k == len(order): break
  return data, indices
