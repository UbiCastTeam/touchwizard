#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Page(object):
    """
    Abstract class to subclass to describe different properties of a touchwizard page.

    Attributes :

      - provides (tuple of str)
          List of session keys the page defines.

      - requires (tuple of str)
          List of depending session keys (the page cannot be displayed as long
          as all elements of this list are not set in session). Instead of
          displaying the page, the first page providing a missing element will
          be displayed.

      - my_icon (Icon)
          The icon of the page itself. Used when an icon which goes to the page
          is needed in the icon bar.

      - title (str):
          The human-readable title of the page.

      - name (str):
          The name of the page. Should be unique.

      - icons (list of Icon):
          The icons to load in the icon bar when the page is displayed.
    """

    provides = tuple()
    requires = tuple()
    need_session = False
    need_loading = False
    reuse = False
    my_icon = None
    title = None
    name = None
    panel = None
    previous = None
    next = None
    icons = ()

    def __init__(self, session):
        if self.need_session:
            self.panel = self.__class__.panel(session=session)
        else:
            self.panel = self.__class__.panel()
