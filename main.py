# -*- coding: utf-8 -*-
# Module: default
# Author: cache-sk
# Created on: 19.9.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import sys
#import topserialy
import xbmcgui, xbmcaddon, xbmcplugin

_url = sys.argv[0]
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()

if __name__ == '__main__':
    #topserialy.router(sys.argv[2][1:])
    disc = """
Sluzby verystream, oload, streamango a rapidvideo ukoncili svoju prevadzku, vzhladom na fakt, ze vsetky odkazy na videa boli
z tychto zdrojov sme sa rozhodli ukoncit prevadzku aj my.

Farewell, RIP.


Doplnok si tym padom mozte odstranit, uz nikdy nebude fungovat.
    """
    xbmcgui.Dialog().textviewer(_addon.getAddonInfo('name'), disc)
    xbmcplugin.endOfDirectory(_handle)
