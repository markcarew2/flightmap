
def calc_zoom(radius):
    zooms = [27.5*(2**num) for num in range(0,10)]
    for zoom in zooms:
        if radius > 12000:
            return 0
        
        elif radius<zoom+(zoom/4):
            return 11-zooms.index(zoom)
        else:
            pass