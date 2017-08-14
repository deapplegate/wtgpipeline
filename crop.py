import Image
import sys
from glob import glob

for pattern, name in [['BPZODDS_new','odds'],['chiratio','chi'],['ACSratio','shearrat']]:
    gs = glob('*' + pattern + '*png')                                           
    
    print gs
    x1 = 0 
    y1 = 0 
    x2 = 1000 
    y2 =  772 
    
    mosaic = Image.new('RGB',[3*(x2-x1),3*(y2-y1)],(255,255,255))
    
    x = 0
    y = 0
    
    for f in gs:
        box = [x,y,x+(x2-x1),y+(y2-y1)]
        print f, x, box
        im = Image.open(f)
        print im.size
       # width,int(height*(float(a[1])/a[0])))
        #p= im.crop([0,0,x2,y2])#.resize((x2-x1,y2-y1))
    
        p= im.resize((x2,y2))
        mosaic.paste(p,box) 
        x += (x2 - x1)
        if x > 2*(x2-x1):
            x = 0
            y += (y2-y1)
        if y > 2*(y2-y1): break
        
    import os
    os.system('rm ' + name + '.pdf')
    mosaic.save(name + '.pdf','PDF')
