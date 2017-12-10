# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 03:32:05 2016
@author: yxl
"""
import wx
import threading

from ... import IPy
from ...ui.panelconfig import ParaDialog
from ..manager import TextLogManager, TaskManager

class Simple:
    title = 'SimpleFilter'
    note = []
    para = None
    'all, 8-bit, 16-bit, rgb, float, req_roi, stack, stack2d, stack3d'
    view = None
    prgs = (None, 1)
    modal = True

    def __init__(self, ips=None):
        print('simple start')
        self.ips = IPy.get_ips() if ips==None else ips
        self.dialog = None
    
    def progress(self, i, n):
        self.prgs = (i, n)

    def load(self, ips):return True
        
    def preview(self, ips, para):pass

    def show(self):
        if self.view==None:return wx.ID_OK
        self.dialog = ParaDialog(IPy.get_window(), self.title)
        self.dialog.init_view(self.view, self.para, 'preview' in self.note, modal=self.modal)
        self.dialog.set_handle(lambda x:self.preview(self.ips, self.para))
        if self.modal: return self.dialog.ShowModal()
        self.dialog.on_ok = lambda : self.ok(self.ips)
        self.dialog.on_cancel = lambda : self.cancel(self.ips)
        self.dialog.Show()
    
    def run(self, ips, imgs, para = None):pass
        
    def cancel(self, ips):pass

    def ok(self, ips, para=None, callafter=None):
        if para == None: para = self.para
        threading.Thread(target = self.runasyn, 
                    args = (ips, ips.imgs, para, callafter)).start()
        win = TextLogManager.get('Recorder')
        if win!=None: win.append('{}>{}'.format(self.title, para))

    def runasyn(self,  ips, imgs, para = None, callback = None):
        TaskManager.add(self)
        self.run(ips, imgs, para)
        ips.update = 'pix'
        TaskManager.remove(self)
        if callback!=None:callback()

    def check(self, ips):
        note = self.note
        if ips == None:
            IPy.alert('no image opened!')
            return False
        if 'req_roi' in note and ips.roi == None:
            IPy.alert('no Roi found!')
            return False
        if not 'all' in note:
            if ips.get_imgtype()=='rgb' and not 'rgb' in note:
                IPy.alert('do not surport rgb image')
                return False
            elif ips.get_imgtype()=='8-bit' and not '8-bit' in note:
                IPy.alert('do not surport 8-bit image')
                return False
            elif ips.get_imgtype()=='16-bit' and not '16-bit' in note:
                IPy.alert('do not surport 16-bit uint image')
                return False
            elif ips.get_imgtype()=='32-int' and not 'int' in note:
                IPy.alert('do not surport 32-bit int uint image')
                return False
            elif 'float' in ips.get_imgtype() and not 'float' in note:
                IPy.alert('do not surport float image')
                return False
        if sum([i in note for i in ('stack','stack2d','stack3d')])>0:
            if ips.get_nslices()==1:
                IPy.alert('stack required!')
                return False
            elif 'stack2d' in note and ips.is3d:
                IPy.alert('stack2d required!')
                return False
            elif 'stack3d' in note and not ips.is3d:
                IPy.alert('stack3d required!')
                return False
            
        return True
        
    def start(self, para=None, callback=None):
        #print self.title, para
        if not self.check(self.ips):return
        if not self.load(self.ips):return
        if para!=None or self.view==None:
            self.ok(self.ips, para, callback)
        elif self.modal:
            if self.show() == wx.ID_OK:
                self.ok(self.ips, para, callback)
            else:self.cancel(ips)
            self.dialog.Destroy()
        else: self.show()

            