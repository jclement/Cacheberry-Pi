import math

def angleDifference(angle1, angle2):
  """
  Find the difference between two angles specified in degrees.
  
  solution from here:
   http://actionsnippet.com/?p=1451
  """
  return abs((angle1+180 -angle2) % 360 - 180)

def distanceFromPath(angleOfPath, angleToPoint, distanceToPoint):
  """
  Find the closest distance from a point to the path of travel.
  """
  theta = math.radians(angleDifference(angleOfPath, angleToPoint))
  if theta > math.pi/2:
    return None
  distanceToIntersection = distanceToPoint * math.sin(theta)
  return distanceToIntersection 

if __name__=='__main__':
  for params, output in [
    ((45, 30, 100), 25.882),
    ((30, 45, 100), 25.882),
    ((350, 5, 100), 25.882),
    ((5, 350, 100), 25.882),
    ]:
    print (params,"should be", output)
    if output == None:
      assert distanceFromPath(*params) == None
    else:
      assert round(distanceFromPath(*params),3) == round(output,3)
  
  

