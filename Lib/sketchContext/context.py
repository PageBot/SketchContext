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
#  Eqivalent classes on PageBot <--> SketchApp2Py
#  Publication       SketchApi/Sketch file
#  Document          SketchPage
#  Document.pages    SketchArtBoard[]
#  Page.elements     SketchArtBoard.layers
#
#  The SketchContext is, together with the 
from pagebot.document import Document
from pagebot.constants import FILETYPE_SKETCH, A4
from pagebot.contexts.basecontext.basecontext import BaseContext
from pagebot.toolbox.units import units

from sketchcontext.builder import SketchBuilder
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
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(path) # Context now interacts with the file.
        
        >>> # Create a PageBot Document instance, reading the Sketch file data as source.
        >>> doc = context.getDocument()
        >>> page = doc[1]
        >>> page
        <Page #1 default (300pt, 400pt)>

        """
        super().__init__()
        self.name = self.__class__.__name__
        # Keep open connector to the file data. If path is None, a default resource
        # files is opened.
        self.b = SketchBuilder(path) 
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

    def read(self, path):
        """
        >>> import sketchapp2py
        >>> context = SketchContext() # Context now interacts with the default Resource file.
        >>> context.b.sketchApi.filePath.split('/')[-1]
        'Template.sketch'
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context.read(path)
        >>> context.b.sketchApi.filePath.split('/')[-1] # Listening to another file now.
        'TemplateSquare.sketch'
        """
        self.b = SketchBuilder(path)

    def _createElements(self, sketchLayer, e):
        """Copy the attributes of the sketchLayer into the element where
        necessary.

        """
        pass
        '''
        if isinstance(sketchLayer, (SketchArtboard, SketchPage)):
            e.w = artboard.width
            e.h = artboard.height
        elif isinstance(sketchLayer, SketchFramed):
            e.x = artboard.x
            e.y = artboard.y
            e.w = artboard.width
            e.h = artboard.height

        if isinstance(sketchLayer, SketchLayer): # There are child layers
            for layer in sketchLayer.layers:
                if isinstance(SketchShapeGroup):
                    self._createElements(layer, newGroup(parent=e))
        '''

    def getDocument(self):
        """Create a new tree of Document/Page/Element instances, interpreting
        Sketch Artboards as pages.

        >>>
        """
        doc = Document(w=300, h=400, context=self)
        self.b
        """
        sketchPages = self.b.getArtBoards()
        doc = None
        page = None
        for artboard in self.b.getArtBoards():
            if page is None:
                doc = Document(w=artboard.width, h=artboard.height)
                page = doc[1]
            else:
                page = page.next
            # Create the element, and copy data from the artboard layers where necessary.
            self._createElements(page, artboard)
        """
        return doc

    def save(self, path=None):
        """Save the current builder data into Sketch file, indicated by path. 
        >>> import sketchapp2py
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(path) # Context now interacts with the file.

        """
        if path is None:
            path = self.b.sketchApi.filePath
        self.b.sketchApi.save(path)
        pass

    def newDocument(self, w, h):
        pass

    def newDrawing(self):
        pass

    def newPage(self, w, h):
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
