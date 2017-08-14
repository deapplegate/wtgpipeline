def use_comp(x,y,c):
    if x-c < y-c:
        return 1    
    elif x-c == y-c:
        return 0
    else:
        return -1
