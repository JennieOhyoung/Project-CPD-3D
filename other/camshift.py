#!/usr/bin/env python

import cv
import numpy as np

def is_rect_nonzero(r):
    (_,_,w,h) = r
    return (w > 0) and (h > 0)

class CamShiftDemo:

    def __init__(self):
        self.capture = cv.CaptureFromCAM(0)
        cv.NamedWindow( "CamShiftDemo", cv.CV_WINDOW_NORMAL)
        cv.NamedWindow( "Histogram", 1 )
        cv.SetMouseCallback( "CamShiftDemo", self.on_mouse)

        # find middle of screen 
        frame = cv.QueryFrame(self.capture)
        self.midScreenX = (frame.width/2)
        self.midScreenY = (frame.height/2)
        self.midScreen = (self.midScreenX, self.midScreenY)
        print "This is the center of the screen: " + str(self.midScreen)

        self.drag_start = None      # Set to (x,y) when mouse starts drag
        self.track_window = None    # Set to rect when the mouse drag finishes

# print instructions in terminal 

        # print( "Keys:\n"
        #     "    ESC - quit the program\n"
        #     "    b - switch to/from backprojection view\n"
        #     "To initialize tracking, drag across the object with the mouse\n" )

    def hue_histogram_as_image(self, hist):
        """ Returns a nice representation of a hue histogram """
        histimg_hsv = cv.CreateImage( (320,200), 8, 3)
        mybins = cv.CloneMatND(hist.bins)
        cv.Log(mybins, mybins)
        
        (_, hi, _, _) = cv.MinMaxLoc(mybins)
        cv.ConvertScale(mybins, mybins, 255. / hi)

        w,h = cv.GetSize(histimg_hsv)
        hdims = cv.GetDims(mybins)[0]
        for x in range(w):
            xh = (180 * x) / (w - 1)  # hue sweeps from 0-180 across the image
            val = int(mybins[int(hdims * x / w)] * h / 255)
            cv.Rectangle( histimg_hsv, (x, 0), (x, h-val), (xh,255,64), -1)
            cv.Rectangle( histimg_hsv, (x, h-val), (x, h), (xh,255,255), -1)

        histimg = cv.CreateImage( (320,200), 8, 3)
        cv.CvtColor(histimg_hsv, histimg, cv.CV_HSV2BGR)
        return histimg

    def on_mouse(self, event, x, y, flags, param):
        if event == cv.CV_EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        if event == cv.CV_EVENT_LBUTTONUP:
            self.drag_start = None
            self.track_window = self.selection
        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax - xmin, ymax - ymin)
            print "selection is" + str(self.selection)

    def run(self):
        hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )
        backproject_mode = False
        while True:
            frame = cv.QueryFrame(self.capture)

            # Convert to HSV and keep the hue
            hsv = cv.CreateImage(cv.GetSize(frame), 8, 3)
            cv.CvtColor(frame, hsv, cv.CV_BGR2HSV)
            self.hue = cv.CreateImage(cv.GetSize(frame), 8, 1)
            cv.Split(hsv, self.hue, None, None, None)

            # Compute back projection
            backproject = cv.CreateImage(cv.GetSize(frame), 8, 1)

            # Run the cam-shift
            cv.CalcArrBackProject( [self.hue], backproject, hist )

            if self.track_window and is_rect_nonzero(self.track_window):
                crit = ( cv.CV_TERMCRIT_EPS | cv.CV_TERMCRIT_ITER, 10, 1)
                (iters, (area, value, rect), track_box) = cv.CamShift(backproject, self.track_window, crit)
                self.track_window = rect

            # If mouse is pressed, highlight the current selected rectangle
            # and recompute the histogram

            if self.drag_start and is_rect_nonzero(self.selection):
                sub = cv.GetSubRect(frame, self.selection)
                save = cv.CloneMat(sub)
                cv.ConvertScale(frame, frame, 0.5)
                cv.Copy(save, sub)
                x,y,w,h = self.selection
                cv.Rectangle(frame, (x,y), (x+w,y+h), (0,0,255))

                # print self.hue
                sel = cv.GetSubRect(self.hue, self.selection )
                cv.CalcArrHist( [sel], hist, 0)
                (_, max_val, _, _) = cv.GetMinMaxHistValue( hist)
                if max_val != 0:
                    cv.ConvertScale(hist.bins, hist.bins, 255. / max_val)
            elif self.track_window and is_rect_nonzero(self.track_window):
                cv.EllipseBox(frame, track_box, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )

# find centroid coordinate (x,y) and area (z)
                selection_centroid = track_box[0]
                global xposition
                xposition = selection_centroid[0]
                yposition = selection_centroid[1]
                width_height = track_box[1]


# writes output of coordinates to seed file if needed
                # with open('seed.txt', 'a') as f:
                #     value = (xposition, yposition)
                #     s = str(value) + '\n'
                #     f.write(s)
                #     # f.write('end_of_session')
                # f.close()

# print outs
                print "x: " + str(xposition)
                print "y: " + str(yposition)
                selection_area = width_height[0]*width_height[1]
                # print "The width is: " + str(width_height[0]) + " The height is: " + str(width_height[1])
                # print "centroid is: " + str(selection_centroid)
                # return "centroid is: " + str(selection_centroid)
                print "area is: " + str(selection_area)
                # return "area is: " + str(selection_area)

            if not backproject_mode:
                cv.ShowImage( "CamShiftDemo", frame )
            else:
                cv.ShowImage( "CamShiftDemo", backproject)
            cv.ShowImage( "Histogram", self.hue_histogram_as_image(hist))

            c = cv.WaitKey(10)
            if c == 27: # escape key
                break
            elif c == ord("b"): # show backproject mode with "b" key
                backproject_mode = not backproject_mode


if __name__=="__main__":
    demo = CamShiftDemo()
    demo.run()





