from BeautifulSoup import BeautifulStoneSoup, Tag
from copy import copy
from markdown import markdown

replacements = [ 
    ('\xe2\x80\x9c','"'),
    ('\xe2\x80\xa6','"'),
    ('\xe2\x80\x99','\''),
    ('\xe2\x80\x9d','...'),
    ('\xe2\x80\x93','-'),
    ('\xc2\xa3','&pound;'),
    ('\xe2\x80\x98','\''),
    ('\xc3\xaf','&iuml;'),
    ('\xc3\xaa','&egrave;'),
    ('\xc3\xa9','&eacute;'),
    ('\xc2\xa0','&nbsp;'),
]

def charReplacements(contents):
    for replacement in replacements:
        try:
            contents = contents.replace(replacement[0],replacement[1])
        except:
            contents = contents.replace(replacement[0].decode('utf8'),replacement[1])
            
    return contents

def replaceImg(post):
    if not hasattr('post.a', 'img'):
        return None
    img = post.a.img
    if img is not None:
        src = img.get('src')
        img.parent.replaceWith('')
        return src
    else:
        return None

def replaceTag(target, targettag,tag=None):
    try:
        if len(targettag) >1:
            elems = target.findAll(targettag[0],targettag[1])
        else:
            elems = target.findAll(targettag[0])
        for element in elems:
            soup = BeautifulStoneSoup()
            contents = element.renderContents()
            contents = charReplacements(contents)
            if tag is None:
                element.replaceWith(contents)
            elif tag is 'newline':
                element.replaceWith('\n%s'%contents)
            else:
                t = Tag(soup, tag)
                t.insert(0,contents)
                element.replaceWith( t )
    except:
        print target
    return


def getComments(id):
    html = BeautifulStoneSoup(open('comments/%s.html'%id).read())
    comments = []
    if html.find('dd') is not None:
        for d in html.findAll('dd'):
            try:
                name = d.previousSibling.previousSibling.span.a.renderContents()
            except:
                if d.previousSibling.previousSibling.span:
                    name = d.previousSibling.previousSibling.span.renderContents()
                else:
                    name = ''
            replaceTag(d,('br',),tag='newline')
            dateHtml = d.find('p',{'class':'comment-timestamp'})
            date = dateHtml.renderContents()
            dateHtml.extract()
            lastDiv = d.find('div',{'class':'r'})
            lastDiv.extract()
            contents = d.renderContents()

            contents = charReplacements(contents)
            comments.append( {'date':date,'body':contents.replace('\'','\\\'').replace('"','\\"'),'name':name} )          
        return comments
    else:
        return None

def parsePost(post):
    img = replaceImg(post)
    id = post.previous.previous.previous.previous.previous.previous.previous.previous.previous.previous.get('name')
    commentUrl =  post.findNextSibling('div',{'class':'post-footer-line post-footer-line-1'}).find('a',{'class':'comment-link'}).get('href')
    replaceTag(post,('span',{'style':'font-style: italic;'}),tag='em')
    replaceTag(post,('span',{'style':'font-weight: bold;'}),tag='strong')
    replaceTag(post,('span',{'style':'font-size:85%;'}))
    replaceTag(post,('span',{'class':'blsp-spelling-error'}))
    replaceTag(post,('span',{'class':'blsp-spelling-corrected'}))
    replaceTag(post,('br',),tag='newline')
    date = post.findNextSibling('div',{'class':'post-footer-line post-footer-line-1'}).find('abbr').get('title')
    text = charReplacements(''.join([str(c) for c in post.contents]).replace('</ul><ul>','').replace('<em></em>',''))
    comments = getComments(id)    
    return {'date':date,'text':text,'img':img,'comments':comments,'id':id}
    

def getAllData():

    html = open('allposts.html').read()
    
    soup = BeautifulStoneSoup(html,convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    posts = soup.findAll('div',{ "class" : "post-body entry-content" })
                
    
    data = []
    for post in posts:
        d = parsePost(post)
        text = d['text'].replace('\'','\\\'').replace('\n','\\n')
        d['title'] = text[:50]
        d['body'] = text
        d['shortdescription'] = text[:150]
        d['sidebar'] = ''
        #print 'httrack --get "https://www.blogger.com/comment.g?blogID=4047028985894596901&postID=%s&isPopup=true" -V "mv \$0  %s.html"'%(d['id'],d['id'])
        data.append(d)

    PYTHONPATH="PYTHONPATH=.:../share/eggs/poop-0.9.2-py2.5.egg:../share/eggs/purepg-0.6.7-py2.4.egg:../share:../share/eggs/formal-0.15.4-py2.5.egg:../share/eggs/crux-0.3.2-py2.4.egg"
    import commands
    from datetime import datetime
    for d in data:
        dataTemplate="from dateutil.parser import *\nimport formal\nattrs={'title':{'en':'%(title)s'},'date':parse('%(date)s'), 'shortdescription':{'en':'%(shortdescription)s'},'body':{'en':formal.types.RichText('markdown','%(body)s')},'sidebar':{'en':'%(sidebar)s'}}"%(d)
        print dataTemplate
        f = open('buildAttrs.py','w')
        f.write(dataTemplate)
        f.close()

        command = "%s python createitem.py -u timparkin -d timparkin -t basiccms.blogentry.BlogEntry --execfile=buildAttrs.py name='%s' author='Tim Parkin'"%(PYTHONPATH,d['id'])
        print command
        import sys; sys.exit()
        out = commands.getstatusoutput(command)
        #id = out[1].split('id=')[1]
        #import sys
        #sys.exit()
        #id = 999
        if d['comments'] is not None:
            for comment in d['comments']:
                comment['id'] = id
                args = 'relatesTo=%(id)s authorName="%(name)s" authorEmail=None comment="%(body)s"'%comment
                dataTemplate = "from dateutil.parser import *\nattrs = {'approved':True,'posted': parse('%s')}"%comment['date']
                f = open('buildAttrs.py','w')
                f.write(dataTemplate)
                f.close()
                command = "%s python createitem.py -u timparkin -d timparkin -t comments.model.Comment --execfile=buildAttrs.py %s"%(PYTHONPATH,args)
                print command
                #import sys
                #sys.exit()
                out = commands.getstatusoutput(command)
        

    
    
    
    
        
    #f = file('data.dumps','w')
    #import pickle
    #f.write( pickle.dumps(data) )
    #f.close()
    
    
        
    
if __name__ == '__main__':
    getAllData()
