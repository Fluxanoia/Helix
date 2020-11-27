
def updateBounds(l, u, new):
    if l is None or new < l: l = new
    if u is None or new > u: u = new
    return l, u
