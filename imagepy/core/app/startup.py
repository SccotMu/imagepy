import wx, sys
from .source import *
from sciapp import Source
from imagepy.core.app import loader

def extend_plgs(plg):
    if isinstance(plg, tuple):
        return (plg[0].title, extend_plgs(plg[1]))
    elif isinstance(plg, list):
        return [extend_plgs(i) for i in plg]
    elif isinstance(plg, str): return plg
    else: return (plg.title, plg)

def extend_tols(tol):
    if isinstance(tol, tuple) and isinstance(tol[1], list):
        return (tol[0].title, extend_tols(tol[1]))
    elif isinstance(tol, tuple) and isinstance(tol[1], str):
        return (tol[1], tol[0])
    elif isinstance(tol, list): return [extend_tols(i) for i in tol]

def extend_wgts(wgt):
    if isinstance(wgt, tuple) and isinstance(wgt[1], list):
        return (wgt[0].title, extend_wgts(wgt[1]))
    elif isinstance(wgt, list): return [extend_wgts(i) for i in wgt]
    else: return (wgt.title, wgt)

def load_plugins():
    data = loader.build_plugins('menus')
    extends = glob('plugins/*/menus')
    keydata = {}
    for i in data[1]:
        if isinstance(i, tuple): keydata[i[0].title] = i[1]
    for i in extends:
        plgs = loader.build_plugins(i)
        for j in plgs[1]:
            if not isinstance(j, tuple): continue
            name = j[0].title
            if name in keydata: keydata[name].extend(j[1])
            else: data[1].append(j)
    return extend_plgs(data)

def load_tools():
    data = loader.build_tools('tools')
    extends = glob('plugins/*/tools')
    default = 'Transform'
    for i in extends:
        tols = loader.build_tools(i)
        if len(tols)!=0: data[1].extend(tols[1])
    return extend_tols(data)

def load_widgets():
    data = loader.build_widgets('widgets')
    extends = glob('plugins/*/widgets')
    for i in extends:
        tols = loader.build_widgets(i)
        if len(tols)!=0: data[1].extend(tols[1])
    return extend_wgts(data)

def start():
    from imagepy.core.app import ImagePy, ImageJ
    #from skimage.data import camera, astronaut
    import wx.lib.agw.advancedsplash as AS

    app = wx.App(False)
    bitmap = wx.Bitmap('data/logolong.png', wx.BITMAP_TYPE_PNG)
    shadow = wx.Colour(255,255,255)

    asp = AS.AdvancedSplash(None, bitmap=bitmap, timeout=1000,
        agwStyle=AS.AS_TIMEOUT |
        AS.AS_CENTER_ON_PARENT |
        AS.AS_SHADOW_BITMAP,
        shadowcolour=shadow)
    asp.Update()

    uistyle = Source.manager('config').get('uistyle') or 'imagepy'
    frame = ImageJ(None) if uistyle == 'imagej' else ImagePy(None)
    #frame.show_img([camera()], 'camera')
    #frame.show_img([astronaut()], 'astronaut')
    frame.Show()
    app.MainLoop()