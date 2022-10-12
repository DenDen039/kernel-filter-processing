import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import messagebox

import filters

import os

from PIL import  ImageTk,Image
import cv2 as cv

from collections import deque
from scipy.special import comb
import numpy as np


FILTERS_DIR = "./filters/"
FILTERS_LIST_NAME = "filters"

def bernstein_poly(i, n, t):
    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i


def bezierr_curve(points, nTimes=1000):
    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])
    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return xvals, yvals

class App:
    def __init__(self, root):
        

        if not os.path.exists(FILTERS_DIR):
            os.makedirs(FILTERS_DIR)
        
        #setting title
        root.title("Image filters")
        #setting window size
        width=798
        height=325
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        

        self.history_stack = deque()

        ImportImageButton=tk.Button(root)
        ImportImageButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ImportImageButton["font"] = ft
        ImportImageButton["fg"] = "#000000"
        ImportImageButton["justify"] = "center"
        ImportImageButton["text"] = "Import"
        ImportImageButton.place(x=110,y=280,width=70,height=25)
        ImportImageButton["command"] = self.ImportImageButton_command

        self.ImportImageLabel=tk.Label(root)
        self.ImportImageLabel["justify"] = "center"
        self.ImportImageLabel.place(x=10,y=10,width=265,height=265)

        self.ResultImageLabel=tk.Label(root)
        self.ResultImageLabel["justify"] = "center"
        self.ResultImageLabel.place(x=290,y=10,width=265,height=265)

        self.current_filter = tk.StringVar(root)
        self.filter_list = filters.GetFilterList()
        self.current_filter.set(self.filter_list[0])

        self.FiltersList=tk.OptionMenu(root, self.current_filter, *self.filter_list)
        self.FiltersList["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.FiltersList["font"] = ft
        self.FiltersList["fg"] = "#333333"
        self.FiltersList["justify"] = "center"
        self.FiltersList.place(x=670,y=30,width=95,height=30)

        ProcessButton=tk.Button(root)
        ProcessButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ProcessButton["font"] = ft
        ProcessButton["fg"] = "#000000"
        ProcessButton["justify"] = "center"
        ProcessButton["text"] = "Process"
        ProcessButton.place(x=680,y=70,width=71,height=30)
        ProcessButton["command"] = self.ProcessButton_command

        LoadFilterButton=tk.Button(root)
        LoadFilterButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        LoadFilterButton["font"] = ft
        LoadFilterButton["fg"] = "#000000"
        LoadFilterButton["justify"] = "center"
        LoadFilterButton["text"] = "Load filter"
        LoadFilterButton.place(x=680,y=110,width=73,height=30)
        LoadFilterButton["command"] = self.LoadFilterButton_command

        SaveImageButton=tk.Button(root)
        SaveImageButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        SaveImageButton["font"] = ft
        SaveImageButton["fg"] = "#000000"
        SaveImageButton["justify"] = "center"
        SaveImageButton["text"] = "Save"
        SaveImageButton.place(x=380,y=280,width=70,height=25)
        SaveImageButton["command"] = self.SaveImageButton_command

        BezierCurveButton=tk.Button(root)
        BezierCurveButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        BezierCurveButton["font"] = ft
        BezierCurveButton["fg"] = "#000000"
        BezierCurveButton["justify"] = "center"
        BezierCurveButton["text"] = "Bezier Curve"
        BezierCurveButton.place(x=680,y=150,width=74,height=30)
        BezierCurveButton["command"] = self.BezierCurveButton_command

        ApplyCurveButton=tk.Button(root)
        ApplyCurveButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        ApplyCurveButton["font"] = ft
        ApplyCurveButton["fg"] = "#000000"
        ApplyCurveButton["justify"] = "center"
        ApplyCurveButton["text"] = "Apply Curve"
        ApplyCurveButton.place(x=680,y=190,width=72,height=30)
        ApplyCurveButton["command"] = self.ApplyCurveButton_command

        MedianFilterButton=tk.Button(root)
        MedianFilterButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        MedianFilterButton["font"] = ft
        MedianFilterButton["fg"] = "#000000"
        MedianFilterButton["justify"] = "center"
        MedianFilterButton["text"] = "Median Filter"
        MedianFilterButton.place(x=680,y=230,width=72,height=30)
        MedianFilterButton["command"] = self.MedianFilterButton_command

        root.bind('<Control-z>', self.undo) 
        self.result_img = None
        self.root = root
        self.bezier_window_state = False
        self.bezier_dots = []
        self.saved_dots = []

    def undo(self,event):
        if len(self.history_stack) == 0:
            return
        
        self.result_img = self.history_stack.pop()
        self.UpdateResultImage()

    def searchForFilePath(self):
        currdir = os.getcwd()

        file = filedialog.askopenfile(
            parent=self.root, mode='r',  initialdir=currdir, title='Please select an image')
        if file == None:
            return "",""
        filepath = os.path.abspath(file.name)

        return filepath,os.path.split(str(filepath))[1]

    def ImportImageButton_command(self):
        path,file_name = self.searchForFilePath()

        try:
            img = cv.imread(path)
            cv.cvtColor(img,cv.COLOR_BGR2RGB)
        except:
            messagebox.showerror(title="Invalid image",
                                message="Cannot load file as an image")
            return 
        
        self.import_img = img
        self.result_img = self.import_img

        photo = ImageTk.PhotoImage(Image.fromarray(cv.cvtColor(cv.resize(self.import_img, dsize=(265, 265), interpolation=cv.INTER_CUBIC), cv.COLOR_BGR2RGB)))

        self.ImportImageLabel.configure(image=photo)
        self.ImportImageLabel.image = photo
        
    def UpdateResultImage(self):
        photo = ImageTk.PhotoImage(Image.fromarray(cv.cvtColor(cv.resize(self.result_img, dsize=(265, 265), interpolation=cv.INTER_CUBIC), cv.COLOR_BGR2RGB)))
        self.ResultImageLabel.configure(image=photo)
        self.ResultImageLabel.image = photo

    def ApplyCorrection(self):
        if self.bezier_window_state or self.saved_dots == []:
            return

        try:
            self.result_img[0,0,0]
        except:
            return

        x,y = bezierr_curve(self.saved_dots,256)

        normlized_x = np.floor((255*(x - np.min(x))/np.ptp(x)))
        normlized_y = np.floor((255*(y - np.min(y))/np.ptp(y)))
        weights = {}

        for i in range(len(normlized_x)):
            weights[255-i] = np.uint8(255-normlized_y[i])
        
        mp = np.arange(0, 256)
        mp[list(weights.keys())] = list(weights.values())
        self.result_img = mp[self.result_img.astype(int)].astype(np.uint8)

        self.history_stack.append(self.result_img)

        self.UpdateResultImage()
        
    def UpdateOptionMenu(self):
        menu = self.FiltersList["menu"]
        menu.delete(0, "end")

        for string in self.filter_list:
            menu.add_command(label=string, 
                             command=lambda value=string: self.current_filter.set(value))

    def ProcessButton_command(self):
        try:
            self.history_stack.append(self.result_img)
            
            self.result_img = filters.ApplyFilter(self.result_img,self.current_filter.get())

            self.UpdateResultImage()
        except:
            messagebox.showerror(title="Invalid image",
                                message="Image not loaded")
            return

    def onBezierWindowClose(self):
        self.bezier_window.destroy()
        self.bezier_window_state = False
        self.bezier_dots = []
        self.saved_dots = []
    
    def BuildBezier(self):
        points = [[0,400]]
        for i in self.bezier_dots:
            coord = self.bezier_canvas.coords(i)
            points.append(coord)
        points.append([400,0])
        
        x,y = bezierr_curve(points,255)

        self.saved_dots=points

        self.bezier_canvas.delete("line")
        for i in range(len(x)-1):
            self.bezier_canvas.create_line(x[i],y[i],x[i+1],y[i+1],fill='white',tags='line')

    def DeleteDot(self,event):
        canvas_item_id = event.widget.find_withtag('current')[0]

        if canvas_item_id in self.bezier_dots: 
            self.bezier_dots.remove(canvas_item_id)

        self.bezier_canvas.delete("current")

        self.BuildBezier()

    def CreateDot(self,event):
        x1, y1 = (event.x - 5), (event.y - 5)
        x2, y2 = (event.x + 5), (event.y + 5)

        self.bezier_dots.append(self.bezier_canvas.create_oval(x1, y1, x2, y2, fill="#ffffff"))

        self.bezier_canvas.tag_bind(self.bezier_dots[-1],"<Button-3>",self.DeleteDot)
        self.bezier_canvas.tag_bind(self.bezier_dots[-1],"<B1-Motion>", self.RelocateDot)

        self.bezier_tags+=1

        self.BuildBezier()

    def RelocateDot(self, event):
        if event.x < 0 or event.x > 400 or event.y < 0 or event.y > 400:
            return
        canvas_item_id = event.widget.find_withtag('current')[0]
        self.bezier_canvas.moveto(canvas_item_id, event.x-5, event.y-5) 

        self.BuildBezier()
    def SaveDots(self):
        self.bezier_window.destroy()
        self.bezier_dots = []
        self.bezier_window_state = False
    
    def openBezierWindow(self):

        self.bezier_window = tk.Toplevel(self.root)

        self.bezier_window.title("Bezier Curve")
        self.bezier_window.geometry("400x500")
        
        self.bezier_tags = 0
        self.bezier_dots = []

        OKButton=tk.Button(self.bezier_window)
        OKButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        OKButton["font"] = ft
        OKButton["fg"] = "#000000"
        OKButton["justify"] = "center"
        OKButton["text"] = "Ok"
        OKButton.place(x=100,y=450,width=74,height=30)
        OKButton["command"] = self.SaveDots

        CancelButton=tk.Button(self.bezier_window)
        CancelButton["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        CancelButton["font"] = ft
        CancelButton["fg"] = "#000000"
        CancelButton["justify"] = "center"
        CancelButton["text"] = "Cancel"
        CancelButton.place(x=300-74,y=450,width=74,height=30)
        CancelButton["command"] = self.onBezierWindowClose

        self.bezier_canvas = tk.Canvas(self.bezier_window,width=400,height=400)
        self.bezier_canvas.configure(bg='black')
        self.bezier_canvas.pack()
        
        self.BuildBezier()
        
        self.bezier_window.protocol("WM_DELETE_WINDOW", self.onBezierWindowClose)
        self.bezier_window.bind('<Double-Button-1>',self.CreateDot)

    def LoadFilterButton_command(self):
        path,file_name = self.searchForFilePath()

        try:
            kernel,post_processing = filters.AddFilter(path)
        except:
            messagebox.showerror(title="Invalid filter",
                                message="Cannot load load new filter")
            return

        try:
            f_name = filters.CreateFilter(kernel,file_name.split(".")[0],post_processing)
            self.filter_list.append(f_name)
            self.UpdateOptionMenu()
        except:
            messagebox.showerror(title="Invalid filter",
                                message="Cannot load load new filter")
            return
        

    def SaveImageButton_command(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".jpg", initialfile="Untiled.jpg")
        if not filename:
            return  
        Image.fromarray(cv.cvtColor(self.result_img, cv.COLOR_BGR2RGB)).save(filename)

    def MedianFilterButton_command(self):
        try:
            self.result_img[0,0,0]
        except:
            return

        self.result_img = cv.medianBlur(self.result_img,5)

        self.UpdateResultImage()

    def BezierCurveButton_command(self):
        if not self.bezier_window_state:
            self.bezier_window_state=True
            self.openBezierWindow()
            
    def ApplyCurveButton_command(self):
        self.ApplyCorrection()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()