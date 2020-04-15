    # -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#     S K E T C H  C O N T E X T
#
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens
#     www.pagebot.io
#     Licensed under MIT conditions
#
#     Supporting DrawBot, www.drawbot.com
#     Supporting Flat, xxyxyz.org/flat
# -----------------------------------------------------------------------------
#
#     sketchbuilder.py
#
from pagebot.contexts.basecontext.basebuilder import BaseBuilder
from pagebot.toolbox.units import upt
from sketchapp2py.sketchapi import SketchApi

class SketchBuilder(BaseBuilder):
    PB_ID = 'Sketch'

    def __init__(self, path=None, **kwargs):
    	"""
        >>> import sketchapp2py
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
		>>> b = SketchBuilder(path)
        >>> b
        <SketchBuilder path=TemplateSquare.sketch>
		>>> b.api
		<SketchApi path=TemplateSquare.sketch>
		>>> sketchPage = b.api.selectPage(0)
		>>> sketchPage, sketchPage.frame
		(<SketchPage name=Page 1>, <SketchRect x=0 y=0 w=0 h=0>)
    	"""
    	super().__init__(**kwargs)
    	self.api = SketchApi(path)

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.api.sketchFile.path.split('/')[-1])

    def frameDuration(self, frameDuration):
        pass

    def save(self):
        pass

    def fill(self, e, g, b, alpha=None):
        pass

    def _get_pages(self):
        """Answer the list of all SketchPage instances.

        >>> import sketchapp2py
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> b = SketchBuilder(path)
        >>> b.pages
        [<SketchPage name=Page 1>]
        """
        return self.api.getPages()
    pages = property(_get_pages)

    def _get_artboards(self):
        """Answer a list with all artboards on the current selected page.

        >>> import sketchapp2py
        >>> from pagebot.toolbox.transformer import path2Dir
        >>> path = path2Dir(sketchapp2py.__file__) + '/Resources/TemplateSquare.sketch'
        >>> b = SketchBuilder(path)
        >>> b.artboards
        [<SketchArtboard name=Artboard 1 w=576 h=783>]
        """
        return self.api.getArtboards()
    artboards = property(_get_artboards)

    def _get_idLayers(self):
        """Answer the dictionary with {layer.do_objectID: layer, ...}

        """
        return self.api.getIdLayers()
    idLayers = property(_get_idLayers)

    def _get_size(self):
        return upt(self.api.getSize())
    size = property(_get_size)

    def restore(self):
        pass


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])


