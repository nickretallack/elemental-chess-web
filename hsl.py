from __future__ import division
import math

def HSL_2_RGB(H,S,L):
  if (S == 0 ):                       # HSL values = [0-1]
    R = L * 255                       # RGB results = [0-255]
    G = L * 255
    B = L * 255
  else:
    if ( L < 0.5 ):
      var_2 = L * ( 1 + S )
    else:
      var_2 = ( L + S ) - ( S * L )
    var_1 = 2 * L - var_2
    R = rounded(255 * Hue_2_RGB( var_1, var_2, H + ( 1 / 3 ) ))
    G = rounded(255 * Hue_2_RGB( var_1, var_2, H ))
    B = rounded(255 * Hue_2_RGB( var_1, var_2, H - ( 1 / 3 ) ))
  return (R,G,B)  

def Hue_2_RGB( v1, v2, vH ):             # Hue_2_RGB
  if ( vH < 0 ):
    vH += 1
  if ( vH > 1 ):
    vH -= 1
  if ( ( 6 * vH ) < 1 ):
    return ( v1 + ( v2 - v1 ) * 6 * vH )
  if ( ( 2 * vH ) < 1 ):
    return v2 
  if ( ( 3 * vH ) < 2 ):
    return ( v1 + ( v2 - v1 ) * ( ( 2 / 3 ) - vH ) * 6 )
  return v1 
  
  
def hsl_rgb(hue, saturation, lightness):
  if lightness < 0.5:
    temp2 = lightness * (1 + saturation);
  else:
    temp2 = lightness + saturation - lightness*saturation;

  temp1 = 2 * lightness - temp2;

  colors = {
    "red": (hue + 4/3) % 1,
    "green": (hue + 3/3) % 1,
    "blue": (hue + 2/3) % 1
  }

  result = {}
  for (color,coloriness) in colors.iteritems():
    if coloriness * 6 < 1:
      result[color] = temp1 + (temp2 - temp1) * 6 * coloriness;
    elif coloriness * 2 < 1:
      result[color] = temp2;
    elif coloriness * 3 < 2:
      result[color] = temp1 + (temp2 - temp1) * 6 * (2/3 - coloriness);
    else:
      result[color] = temp1;
  return result
  
  
  
def rounded(float):
  return int(math.floor(float+0.5))
  
if __name__ == "__main__":
  print HSL_2_RGB(0,1,.5)