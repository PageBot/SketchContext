#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#  P A G E B O T
#
#  Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens
#  www.pagebot.io
#  Licensed under MIT conditions
#
#  Supporting DrawBot, www.drawbot.com
#  Supporting Flat, xxyxyz.org/flat
#  Supporting Sketch, https://github.com/Zahlii/python_sketch_api
# -----------------------------------------------------------------------------
#
#  sketchcontext.py
#
#  Inspace sketch file:
#  https://xaviervia.github.io/sketch2json/
#
#  https://gist.github.com/xaviervia/edbea95d321feacaf0b5d8acd40614b2
#  This description is not complete.
#  Additions made where found in the Reading specification of this context.
#
#  Equivalent classes on PageBot <--> SketchApp2Py
#  Publication       SketchApi/Sketch file
#  Document          SketchPage
#  Document.pages    SketchArtBoard[]
#  Page.elements     SketchArtBoard.layers
#
#  The SketchContext is, together with the HDMLContext, capable of reading and
#  writing data into the designated file format.
#
import os
from random import random

from pagebot.document import Document
from pagebot.constants import FILETYPE_SKETCH, A4
from pagebot.contexts.basecontext.basecontext import BaseContext
from pagebot.toolbox.units import units
from pagebot.toolbox.color import color

from sketchcontext.builder import SketchBuilder
from sketchcontext.sketchstring import SketchString
#from pagebot.toolbox.color import color
#from pagebot.toolbox.units import asNumber, pt
#from pagebot.toolbox.transformer import path2Dir, path2Extension
from pagebot.elements import *
from sketchapp2py.sketchapi import *

class SketchContext(BaseContext):

    W, H = A4 # Default size of a document, as SketchApp has infinite canvas.

    DOCUMENT_CLASS = Document

    def __init__(self, path=None):
        """Constructor of Sketch context.

        >>> import sketchapp2py
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> from pagebot.document import Document
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(path) # Context now interacts with the file.
        >>> # Create a PageBot Document instance, reading the Sketch file data as source.
        >>> doc = Document()
        >>> context.readDocument(doc)
        >>> page = doc[1]
        >>> page
        <Page #1 default (576pt, 783pt) E(6)>

        """
        super().__init__()
        self.name = self.__class__.__name__
        # Keep open connector to the file data. If path is None, a default resource
        # file is opened.
        self.setPath(path) # Sets self.b to SketchBuilder(path)
        self.fileType = FILETYPE_SKETCH
        self.shape = None # Current open shape
        self.w = self.h = None # Optional default context size, overwriting the Sketch document.

    def setSize(self, w=None, h=None):
        """Optional default document size. If not None, overwriting the size of the 
        open Sketch document.

        >>> context = SketchContext()
        >>> context.w is None and context.h is None
        True
        >>> context.setSize(w=300)
        >>> context.w
        300pt
        """
        self.w = units(w)
        self.h = units(h)

    def setPath(self, path):
        """Set the self.b builder to SketchBuilder(parth), answering self.b.api.

        >>> import sketchapp2py
        >>> context = SketchContext() # Context now interacts with the default Resource file.
        >>> context.b.api.filePath.split('/')[-1]
        'Template.sketch'
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> api = context.setPath(path)
        >>> api.filePath.split('/')[-1] # Listening to another file now.
        'TemplateSquare.sketch'
        """
        self.b = SketchBuilder(path)
        return self.b.api

    def getNameTree(self, layer, t=None, tab=0):
        if t is None:
            t = ''
        t += '%s%s\n' % (tab*'\t', layer)
        if hasattr(layer, 'layers'):
            for child in layer.layers:
                self.getNameTree(child, t, tab+1)
        return t

    def _extractFill(self, layer):
        if hasattr(layer, 'style') and hasattr(layer.style, 'fills') and layer.style.fills:
            sketchColor = layer.style.fills[0].color
            return color(r=sketchColor.red, g=sketchColor.green, b=sketchColor.blue)
        return color(1, 0, 0)

    def _createElements(self, sketchLayer, e):
        """Copy the attributes of the sketchLayer into the element where
        necessary.

        """
        for layer in sketchLayer.layers:
            frame = layer.frame
            y = e.h - frame.h - frame.y # Flip the y-axis
            if isinstance(layer, (SketchGroup, SketchShapeGroup)):
                fillColor = self._extractFill(layer)
                child = newGroup(name=layer.name, parent=e, sId=layer.do_objectID,
                    x=frame.x, y=y, w=frame.w, h=frame.h)
                self._createElements(layer, child)
            
            elif isinstance(layer, SketchRectangle):
                fillColor = self._extractFill(sketchLayer) # Sketch color is defined in parent
                newRect(name=layer.name, parent=e, sId=layer.do_objectID, 
                    x=frame.x, y=y, w=frame.w, h=frame.h, 
                    fill=fillColor)
            
            elif isinstance(layer, SketchOval):
                fillColor = self._extractFill(sketchLayer) # Sketch color is defined in parent
                newOval(name=layer.name, parent=e, sId=layer.do_objectID, 
                    x=frame.x, y=y, w=frame.w, h=frame.h, 
                    fill=fillColor)
            
            elif isinstance(layer, SketchText):
                fillColor = self._extractFill(sketchLayer) # Sketch color is defined in parent
                newTextBox(SketchString(layer.attributedString), name=layer.name, parent=e, 
                    sId=layer.do_objectID, x=frame.x, y=y, w=frame.w, h=frame.h, 
                    textFill=fillColor)

            elif isinstance(layer, SketchBitmap):
                # All internal Sketch file images are converted to .png
                # SketchApp2Py converts the internal names with long id's to their object
                # names and copies them into a parallel folder, indicated by self.b.api.sketchFile
                path = self.b.api.sketchFile.imagesPath + layer.name + '.png' 
                frame = layer.frame
                newImage(path=path, name=layer.name, parent=e, sId=layer.do_objectID,
                    x=frame.x, y=y, w=frame.w, h=frame.h)
            
            elif isinstance(layer, SketchSymbolInstance):
                # For now only show the Symbol name.
                frame = layer.frame
                newTextBox('[%s]' % layer.name, name=layer.name, parent=e, 
                    sId=layer.do_objectID, fill=0.9, textFill=0, font='Verdana', fontSize=12,
                    x=frame.x, y=y, w=frame.w, h=frame.h)

            else:
                print('Unsupported layer type', layer)

    def readDocument(self, doc):
        """Read Page/Element instances from the SketchApi and fill the Document
        instance doc with them, interpreting SketchPages as chapters and 
        Sketch Artboards as PageBot pages.

        >>> import sketchapp2py
        >>> from pagebot.document import Document
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> from pagebot.document import Document
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(path=path) # Context now interacts with the default file.
        >>> # Create a PageBot Document instance, reading the current Sketch file data as source.
        >>> doc = Document(name='TestReadDocument')
        >>> context.readDocument(doc) 
        """
        sketchPages = self.b.pages # Collect the list of SketchPage instance 
        doc.w, doc.h = self.b.size
        #assert doc.originTop # For now, make sure the origin of the document is set on top.
        
        page = doc[1]
        for pIndex, sketchPage in enumerate(sketchPages): 
            artboards = sketchPage.layers
            for artboard in artboards:
                page.w = artboard.frame.w
                page.h = artboard.frame.h
                self._createElements(artboard, page)
                if pIndex < len(artboards)-1:
                    page = page.next
            if pIndex < len(sketchPages)-1:
                page = page.next

    def save(self, path=None):
        """Save the current builder data into Sketch file, indicated by path. 
        >>> import sketchapp2py
        >>> from sketchapp2py.sketchappcompare import sketchCompare
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> readPath = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(readPath) # Context now interacts with the reader file.
        >>> exportDir = path2Dir(sketchapp2py.__file__) + '/_export/'
        >>> if not os.path.exists(exportDir):
        ...     os.path.mkdir(exportDir)
        >>> savePath = exportDir + 'TemplateSquare.sketch'        
        >>> context.save(savePath)
        >>> sketchCompare(readPath, savePath)
        []

        TODO: Read/Save should go through the creation and build of Document instance.
        """
        if path is None:
            path = self.b.sketchApi.filePath
        self.b.api.save(path)

    def newDocument(self, w, h):
        pass

    def newDrawing(self, w=None, h=None):
        pass

    def newPage(self, w, h):
        pass

    def saveDrawing(self, path, multiPage=True):
        pass

    def stroke(self, c, strokeWidth=None):
        pass

    def line(self, p1, p2):
        pass

    def getFlattenedPath(self, path=None):
        pass

    def getFlattenedContours(self, path=None):
        pass

    def getGlyphPath(self, glyph, p=None, path=None):
        pass


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
