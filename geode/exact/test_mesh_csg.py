#!/usr/bin/env python

from __future__ import division,print_function
from geode import *
from geode.geometry.platonic import *

def test_simple_triangulate():
  for n in 0,1,2,3,4,5,10,50:
    for k in xrange(10):
      simple_triangulate_test(n+1000*k,n,n+1,n,n)

def test_csg():
  random.seed(17)

  # Enable to do really expensive things
  expensive = 0
  sphere,_ = sphere_mesh(2)

  # Perform a bunch of tetrahedron CSG
  tet,X0 = tetrahedron_mesh()
  X0 *= tet.volume(X0)**(-1/3)
  I0 = mesh_signature(tet,X0)
  ico,_ = icosahedron_mesh()
  for i in xrange(100):
    random.seed(i)
    X1 = random.randn(4,3)
    X1 *= abs(tet.volume(X1))**(-1/3)
    X2 = random.randn(4,3)
    X2 *= abs(tet.volume(X2))**(-1/3)
    X3 = random.randn(ico.nodes(),3)
    I1 = mesh_signature(tet,X1)
    I2 = mesh_signature(tet,X2)
    I3 = mesh_signature(ico,X3)
    cases = [('2-tet',I0+I1,((tet,X0),(tet,X1))),
             ('3-tet',I0+I1+I2,((tet,X0),(tet,X1),(tet,X2))),
             ('ico',I3,((ico,X3),))]
    if i < 10:
      cases.append(('bad-ico',2*I3,((ico,X3),(ico,X3))))
    if expensive:
      Xs = random.randn(sphere.nodes(),3)
      cases.append(('sphere',mesh_signature(sphere,Xs),((sphere,Xs),)))
    Is = {}
    for name,Iin,meshes in cases:
      print(name)
      if 1:
        m,Z = split_soups(meshes,depth=None)
        assert allclose(Iin,mesh_signature(m,Z))
      if 1:
        m,Z = soup_union(*meshes)
        Is[name] = mesh_signature(m,Z)
        assert not len(m.nonmanifold_nodes(0))
        if 'bad-' in name:
          assert allclose(Is[name],Is[name[4:]])
  print('Success!')

def test_depth_weight():
  tet,X0 = tetrahedron_mesh()
  X0 *= tet.volume(X0)**(-1/3)
  itet,_ = tetrahedron_mesh()
  itet.elements = map(lambda x: (x[1], x[0], x[2]), itet.elements)

  for n in [2, 3, 4]:
    # make a merged mesh of n copies of X0 and one copy with depth n.
    input_meshes = [(tet,X0),]*n + [(itet,X0),]
    meshes,Xs = merge_meshes(input_meshes)
    weight = [1]*n*len(tet.elements) + [n]*len(tet.elements)
    result,Xr = split_soup_with_weight(meshes,Xs,weight,0)

    # the resulting mesh must have volume 0
    assert abs(result.volume(Xr)) < 1e-8

    # make a merged mesh of n copies of X0 and one copy with depth -n-1
    weight = [1]*n*len(tet.elements) + [n-1]*len(tet.elements)
    result,Xr = split_soup_with_weight(meshes,Xs,weight,0)

    # the resulting mesh must have volume 1
    assert abs(result.volume(Xr)-1) < 1e-8

if __name__=='__main__':
  test_simple_triangulate()
  test_csg()
  test_depth_weight()
