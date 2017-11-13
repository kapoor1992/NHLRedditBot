from urllib.request import urlopen
import traceback

from .res.keywords import resolve_team_name

def get_identifiers(lines):
    identifiers = []

    for line in lines:
        if "carousel__item--" in str(line):
            identifier = ''
            for char in str(line):
                if char.isdigit():
                    identifier += char
                elif identifier != '':
                    break
            identifiers.append(identifier)

    return identifiers

def get_names(lines):
    names = []

    for line in lines:
        if "video-preview__blurb" in str(line):
            copy = False
            name = ''
            for char in str(line):
                if char == '>':
                    copy = True
                elif (copy) & (char == '<'):
                    break
                elif (copy) and char != "\\":
                    name += char
            names.append(name)

    return names

def get_pages(identifiers, team):
    pages = []
    
    for identifier in identifiers:
        prefix = 'https://www.nhl.com/' + team + '/video/c-'
        pages.append(prefix + identifier)

    return pages

def get_links(pages):
    links = []
    
    for page in pages:
        data = urlopen(page)
        lines = data.readlines()
        for line in lines:
            if '"contentURL" content="' in str(line):
                link = ''
                for char in str(line):
                    if char == 'h':
                        link += char
                    elif (link != '') & (char == '"'):
                        links.append(link)
                        break
                    elif link != '':
                        link += char
                break

    return links

def get_videos(lines, team):
    identifiers = get_identifiers(lines)
    pages = get_pages(identifiers, team)
    videos = get_links(pages)

    return videos

def get_response(team):

    # make sure we resolve the team name appropriately if it is a single name team
    team = resolve_team_name(team)

    try:
        lines = urlopen("https://www.nhl.com/" + team + "/video/").readlines()

        videos = get_videos(lines, team)
        names = get_names(lines)
        return create_response(names, videos)
    except Exception as e:
        print ("exception occured in videos.get_response:")
        print (str(e))
        print (traceback.print_exc())
        return None

def create_response(names, videos):
    response = ""

    for name, video in zip(names, videos):
        response += '[' + name + ']' + '(' + video + ')\n\n'

    return response
