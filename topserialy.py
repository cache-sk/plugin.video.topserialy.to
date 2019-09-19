# -*- coding: utf-8 -*-
# Module: default
# Author: cache-sk
# Created on: 19.9.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import resolveurl
import requests
from bs4 import BeautifulSoup
import base64

_url = sys.argv[0]
_handle = int(sys.argv[1])

_addon = xbmcaddon.Addon()
_session = requests.Session()
_profile = xbmc.translatePath( _addon.getAddonInfo('profile')).decode('utf-8')

BASE = 'https://www.topserialy.to'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 'Referer': BASE}
RECAP = 'https://www.topserialy.to/recap-check-very.php?'
PRVDRSBASE = {'streamango':'https://streamango.com/embed/'}


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs, 'utf-8'))

def prefix_url(url):
    if url.startswith('/'):
        return url
    return '/' + url

def root():
    xbmcplugin.setPluginCategory(_handle, _addon.getLocalizedString(30000))

    xbmcplugin.addDirectoryItem(_handle, get_url(action='new'), xbmcgui.ListItem(label=_addon.getLocalizedString(30001)), True)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='full'), xbmcgui.ListItem(label=_addon.getLocalizedString(30002)), True)

    xbmcplugin.endOfDirectory(_handle)

def new(page = None):
    xbmcplugin.setPluginCategory(_handle, _addon.getLocalizedString(30001))
    url = BASE + '/ajax_vypis.php' + ('?page=' + page if page is not None else '')
    data_raw = _session.get(url, headers=HEADERS)
    html = BeautifulSoup('<html><body>' + data_raw.text + '</body></html>', 'html.parser')
    items = html.find_all('a',{'class':'prechod'},True)
    for item in items:
        iurl = item['href']
        img = item.select('img')[0]
        title = img['alt']
        img = img['src']
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'title': title})
        list_item.setArt({'thumb': img})
        link = get_url(action='play', url=iurl)
        is_folder = False
        list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)
    xbmcplugin.addDirectoryItem(_handle, get_url(action='new',page=str(int(page)+1) if page is not None else '2'), xbmcgui.ListItem(label=_addon.getLocalizedString(30003)), True)
    xbmcplugin.endOfDirectory(_handle, updateListing=page is not None)

def full():
    xbmcplugin.setPluginCategory(_handle, _addon.getLocalizedString(30002))
    url = BASE + '/serialy'
    data_raw = _session.get(url, headers=HEADERS)
    html = BeautifulSoup(data_raw.text, 'html.parser')
    items = html.find_all('a',{'class':'single-result'},True)
    for item in items:
        iurl = item['href']
        title = item['data-name'] + ' / ' + item['data-altname']
        csfd = 0
        try:
            csfd = int(item['data-csfd']) / 100
        except:
            pass
        img = item.find_all('img',{},True)[0]['data-original']
        genres = [li.string for li in item.find_all('li',{},True)]
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'title': title, 'genre':genres, 'rating':csfd})
        list_item.setArt({'thumb': BASE + img})
        link = get_url(action='detail', url=iurl)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)

def detail(url):
    url = BASE + url
    data_raw = _session.get(url, headers=HEADERS)
    html = BeautifulSoup(data_raw.text, 'html.parser')
    text = html.find_all('div',{'class':'serial-text'},True)[0]
    title = text.select('h2')[0].string + ' / ' + text.select('h3')[0].string
    plot = text.select('p')[0].string
    xbmcplugin.setPluginCategory(_handle, title)
    img = html.find_all('div',{'class':'simg'}, True)[0].select('img')[0]['src']
    
    items = html.find_all('div',{'class':'accordion'}, True)
    for item in items:
        title = item.select('h3')[0]
        iurl = title.select('p')[0]['data']
        title = title.string
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'title': title, 'plot':plot})
        list_item.setArt({'thumb': BASE + img})
        link = get_url(action='episodes', url=iurl)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)

def episodes(url):
    xbmcplugin.setPluginCategory(_handle, _addon.getLocalizedString(30004))
    url = BASE + url
    data_raw = _session.get(url, headers=HEADERS)
    html = BeautifulSoup('<html><body>' + data_raw.text + '</body></html>', 'html.parser')
    items = html.find_all('a',{},True)
    for item in items:
        iurl = item['href']
        title = item.find_all('span',{'class':'epname'})[0].string
        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo('video', {'title': title})
        link = get_url(action='play', url=iurl)
        is_folder = False
        list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, link, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)

def play(url):
    headers = HEADERS.copy()
    data_raw = _session.get(BASE + url, headers=headers)

    html = BeautifulSoup(data_raw.text, 'html.parser')

    videoxz = html.find_all('div', {'class' : 'videoxz'}, True)[0]
    newtabs = videoxz.find_all('div', {'class':'newtabs'}, True)[0]
    ul = newtabs.find_all('ul',{},True)[0]
    lis = ul.find_all('li',{},True)

    providers = []

    for li in lis:
        #provider
        provider = li['class']
        if len(provider) == 1:
            provider = provider[0]
        else:
            for p in provider:
                if p != 'active':
                    provider = p
                    break

        #source
        source = li.find_all('a',{},True)[0]
        id = source['href'][1:]
        div = html.find_all('div',{'id':id},True)[0]
        iframe = div.find_all('iframe',{},True)[0]
        src = base64.b64decode(iframe['data-src'])

        #lang
        lang = li.find_all('span', {}, True)[0].string

        providers.append({'provider':provider, 'lang':lang, 'source': src})

    dialog = xbmcgui.Dialog()
    opts = [provider['provider'] + ' ' + provider['lang'] for provider in providers]
    index = dialog.select(_addon.getLocalizedString(30005), opts)
    
    if index != -1:
        provider = providers[index]
    else:
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return

    headers.update({'Referer': BASE + url})
    response = _session.get(provider['source'], headers=headers, allow_redirects=False)

    path = ''
    subtitles = []

    if response.status_code > 300 and response.status_code < 400:
        real = response.headers['Location']
        real = real.split('?')
        path = real[0]
        if len(real) > 1:
            params = dict(parse_qsl(real[1]))
            if 'c1_file' in params:
                subtitles.append(params['c1_file'])
    elif response.status_code == 200 and provider['provider'] in PRVDRSBASE:
        #captcha reroute? :)
        url2 = RECAP + provider['source'].split('?')[1]
        response2 = _session.get(url2, headers=headers, allow_redirects=False)
        if response2.status_code > 300 and response2.status_code < 400:
            real = response2.headers['Location']
            real = real.split('?')
            code = real[0].split('/')
            path = PRVDRSBASE[provider['provider']] + code[len(code)-2]
            if len(real) > 1:
                params = dict(parse_qsl(real[1]))
                if 'c1_file' in params:
                    subtitles.append(params['c1_file'])

    try:
        resolved_url = resolveurl.resolve(path)
        listitem = xbmcgui.ListItem(path=resolved_url)
        if subtitles:
            listitem.setSubtitles(subtitles)
        xbmcplugin.setResolvedUrl(_handle, True, listitem)
    except Exception as e:
        xbmcgui.Dialog().ok(_addon.getLocalizedString(30000), _addon.getLocalizedString(30006))



def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params and 'action' in params:
        if params['action'] == 'new':
            if 'page' in params:
                new(params['page'])
            else:
                new()
        elif params['action'] == 'full':
            full()
        elif params['action'] == 'detail':
            detail(prefix_url(params['url']))
        elif params['action'] == 'episodes':
            episodes(prefix_url(params['url']))
        elif params['action'] == 'play':
            play(prefix_url(params['url']))
        else:
            root()
    else:
        root()
