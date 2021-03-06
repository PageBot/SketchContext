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

#from pagebot.document import Document
#from pagebot.elements import *
from pagebot.constants import FILETYPE_SKETCH, A4
from pagebot.contexts.basecontext.basecontext import BaseContext
from pagebot.contexts.basecontext.babelstring import BabelString
from pagebot.constants import *
from pagebot.toolbox.color import color
from pagebot.toolbox.units import pt, units, upt

from pagebotsketch.sketchbuilder import SketchBuilder
from pysketch.sketchclasses import *

class SketchContext(BaseContext):

    W, H = A4 # Default size of a document, as SketchApp has infinite canvas.

    #DOCUMENT_CLASS = Document

    def __init__(self, path=None):
        """Constructor of Sketch context.

        >>> import pysketch
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> from pagebot.document import Document
        >>> path = path2Dir(pysketch.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(path) # Context now interacts with the file.
        >>> # Create a PageBot Document instance, reading the Sketch file data as source.
        >>> doc = Document()
        >>> context.readDocument(doc)
        >>> page = doc[1]
        >>> page
        <Page #1 default (576pt, 783pt) E(7)>

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

        >>> import pysketch
        >>> context = SketchContext() # Context now interacts with the default Resource file.
        >>> context.b.api.filePath.split('/')[-1]
        'Template.sketch'
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(pysketch.__file__) + '/Resources/TemplateSquare.sketch'
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
        return color(0.5)

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
                    x=frame.x, y=y, w=frame.w, h=frame.h, fill=fillColor)

            elif isinstance(layer, SketchOval):
                fillColor = self._extractFill(sketchLayer) # Sketch color is defined in parent
                newOval(name=layer.name, parent=e, sId=layer.do_objectID,
                    x=frame.x, y=y, w=frame.w, h=frame.h, fill=fillColor)

            elif isinstance(layer, SketchText):
                fillColor = self._extractFill(sketchLayer) # Sketch color is defined in parent
                newTextBox(self.asBabelString(layer.attributedString), name=layer.name, parent=e,
                    sId=layer.do_objectID, x=frame.x, y=y, w=frame.w, h=frame.h, textFill=fillColor)

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
        instance doc with them, interpreting SketchPages as chapters and Sketch
        Artboards as PageBot pages.

        >>> import pysketch
        >>> from pagebot.document import Document
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> from pagebot.document import Document
        >>> path = path2Dir(pysketch.__file__) + '/Resources/TemplateText.sketch'
        >>> context = SketchContext(path=path) # Context now interacts with the default file.
        >>> # Create a PageBot Document instance, reading the current Sketch file data as source.
        >>> doc = Document(name='TestReadDocument')
        >>> context.readDocument(doc)
        >>> page = doc[1]
        >>> e = page.elements[0]
        >>> e
        <Text $Type & sty...$ x=137pt y=134pt w=518pt h=100pt>
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
        >>> import pysketch
        >>> from pysketch.sketchappcompare import sketchCompare
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> readPath = path2Dir(pysketch.__file__) + '/Resources/TemplateSquare.sketch'
        >>> context = SketchContext(readPath) # Context now interacts with the reader file.
        >>> exportDir = path2Dir(pysketch.__file__) + '/_export/'
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

    def asBabelString(self, sas):
        """Convert the SketchAttributedString skText into a generic BabelString.

        * https://developer.apple.com/documentation/foundation/nsattributedstring
        * https://developer.apple.com/documentation/coretext/ctframesetter-2eg

        >>> import pysketch
        >>> from pysketch.sketchapi import SketchApi
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(pysketch.__file__) + '/Resources/TemplateText.sketch'
        >>> context = SketchContext(path)
        >>> skTextBox = context.b.artboards[0].layers[0] # Find the Sketch text box
        >>> sas = skTextBox.attributedString # SketchText inside the box
        >>> sas
        <SketchAttributedString>
        >>> len(sas.attributes)
        3
        >>> bs = context.asBabelString(sas) # Convert to generic BabelString
        >>> len(bs.runs) # We originally had 3 typographic parameter runs
        3
        >>> bs # Represented by joining text strings of all runs
        $Type & sty...$
        >>> bs.runs[0].s, bs.runs[0].style['font'], bs.runs[0].style['fontSize']
        ('Type ', 'Proforma-Book', 90pt)
        >>> bs.runs[1].s, bs.runs[1].style['font'], bs.runs[1].style['fontSize']
        ('&', 'Proforma-Book', 200pt)
        >>> sas2 = context.fromBabelString(bs) # New conversion
        >>> sas == sas2 # Bi-directional conversion works
        True
        >>> # Now change the BabelString
        >>> bs.runs[0].style['font'] = 'Verdana-Bold'
        >>> bs.runs[1].style['font'] = 'Verdana-Italic'
        >>> bs.runs[1].style['textFill'] = color(1, 0, 0)
        >>> bs.runs[2].style['textFill'] = color(1, 0, 0.5)
        >>> bs.runs[2].s = ' changed' # Change text of the run
        >>> sas2 = context.fromBabelString(bs) # New conversion
        >>> skTextBox.attributedString = sas2
        >>> context.save('_export/TemplateTextChanged.sketch') # Save as other document
        >>> bs2 = context.asBabelString(sas2) # Convert back to pbs
        >>> bs == bs2 # This should be identical, after bi-directional conversion.
        True
        """
        assert isinstance(sas, SketchAttributedString), "%s.asBabelString: @sas has class %s" % (
            self.__class__.__name__, sas.__class__.__name__)
        ALIGNMENTS = {0: LEFT, 1: RIGHT, 2: CENTER, None: JUSTIFIED}
        bsResult = None
        for attrs in sas.attributes:
            fd = attrs.attributes.MSAttributedStringFontAttribute.attributes
            cc = attrs.attributes.MSAttributedStringColorAttribute
            textFill = color(r=cc.red, g=cc.green, b=cc.blue, a=cc.alpha)
            verticalAlignment = attrs.attributes.textStyleVerticalAlignmentKey
            tracking = attrs.attributes.kerning # Wrong Sketch name for tracking
            paragraphStyle = attrs.attributes.paragraphStyle

            style = dict(font=fd.name, fontSize=pt(fd.size), textFill=textFill,
                tracking=tracking, xAlign=ALIGNMENTS.get(paragraphStyle.alignment, JUSTIFIED))
            #print('===', style)
            s = sas.string[attrs.location:attrs.location+attrs.length]
            bs = BabelString(s, style=style)
            if bsResult is None:
                bsResult = bs
            else:
                bsResult += bs
        return bsResult

    def fromBabelString(self, bs):
        """

        >>> bs = BabelString('abcd', style=dict(font='Roboto-Regular', fontSize=pt(18)))
        >>> context = SketchContext()
        >>> sas1 = context.fromBabelString(bs)
        >>> sas1
        <SketchAttributedString>
        >>> sas2 = context.fromBabelString(bs)
        >>> sas1 == sas2
        True
        """
        assert isinstance(bs, BabelString)
        ALIGNMENTS = {LEFT: 0, RIGHT: 1, CENTER: 2, JUSTIFIED: None}
        cIndex = 0
        sas = SketchAttributedString()
        sas.string = ''
        style = None
        attrs = sas.attributes
        for run in bs.runs:
            if style is None or run.style is not None:
                style = run.style
            ssa = SketchStringAttribute()
            ssa.location = cIndex
            ssa.length = len(run.s)
            sas.string += run.s
            cIndex += ssa.length

            ssa.attributes = SketchAttributes()
            ssa.attributes.kerning = style.get('tracking', 0)
            ssa.attributes.textStyleVerticalAlignmentKey = 0 # ???
            ssa.attributes.paragraphStyle = SketchParagraphStyle()
            ssa.attributes.paragraphStyle.alignment = ALIGNMENTS.get(style.get('xAlign', JUSTIFIED))

            ssa.attributes.MSAttributedStringFontAttribute = SketchFontDescriptor()
            fd = ssa.attributes.MSAttributedStringFontAttribute.attributes
            fd.name = run.style.get('font', 'Verdana')
            fd.size = upt(run.style.get('fontSize', 12))
            tc = run.style.get('textFill', color(0))

            ssa.attributes.MSAttributedStringColorAttribute = SketchColor(red=tc.r, green=tc.g, blue=tc.b, alpha=tc.a)
            attrs.append(ssa)
        return sas


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
