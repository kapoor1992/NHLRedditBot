import urllib2

def getIdentifiers(lines):
    identifiers = []

    for line in lines:
        if "carousel__item--" in line:
            identifier = ''
            for char in line:
                if char.isdigit():
                    identifier += char
                elif identifier != '':
                    break
            identifiers.append(identifier)

    return identifiers

def getNames(lines):
    names = []

    for line in lines:
        if "video-preview__blurb" in line:
            copy = False
            name = ''
            for char in line:
                if char == '>':
                    copy = True
                elif (copy) & (char == '<'):
                    break
                elif (copy):
                    name += char
            names.append(name)

    return names

def getPages(identifiers, team):
    pages = []
    
    for identifier in identifiers:
        prefix = 'https://www.nhl.com/' + team + '/video/c-'
        pages.append(prefix + identifier)

    return pages

def getLinks(pages):
    links = []
    
    for page in pages:
        data = urllib2.urlopen(page)
        lines = data.readlines()
        for line in lines:
            if '"contentURL" content="' in line:
                link = ''
                for char in line:
                    if char == 'h':
                        link += char
                    elif (link != '') & (char == '"'):
                        links.append(link)
                        break
                    elif link != '':
                        link += char
                break

    return links

def getVideos(lines, team):
    identifiers = getIdentifiers(lines)
    pages = getPages(identifiers, team)
    videos = getLinks(pages)

    return videos

def get_response(team):

    try:
        data = urllib2.urlopen("https://www.nhl.com/" + team + "/video/")
        lines = data.readlines()

        videos = getVideos(lines, team)
        names = getNames(lines)
        return create_response(names, videos)
    except Exception, e:
        print ""
        print "exception occured in videos.get_response:"
        print str(e)
        return None

def create_response(names, videos):
    response = ""

    for name, video in zip(names, videos):
        response += '[' + name + ']' + '(' + video + ')\n\n'

    return response
