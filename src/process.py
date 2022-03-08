###
### process.py
###
### Kludgey code for generating a conference papers website
### David Evans (evans@virginia.edu
###
### This is adapted from the version I wrote for ACM CCS 2017:
###    https://github.com/acmccs/acmccs.github.io/blob/master/src/process.py
###


from collections import namedtuple
import time
import re
import csv

# This is a hard-coded pathname (output by hotcrp).
# This file should not be included in repo due to confidentiality risks.
PAPERS_CSV = "/Users/dave/Dropbox/EuroSP/conference/eurosp2022-data.csv"
TOPICS_CSV = "/Users/dave/Dropbox/EuroSP/conference/eurosp2022-topics.csv"
CONFERENCE = "IEEE EuroS&P 2022"
CONFERENCE_FULL = '<a href="https://www.ieee-security.org/TC/EuroSP2022/">7<sup>th</sup> IEEE European Symposium on Security and Privacy</a>'

### Need to update when we have these for Euro S&P

# SESSION_TIMES = {
#     1: 'Tuesday, 10:45am-noon',
#     2: 'Tuesday, 1:45-3:15pm',
#     3: 'Tuesday, 3:45-5:15pm',
#     4: 'Wednesday, 9:00-10:30am',
#     5: 'Wednesday, 11:00am-12:30pm',
#     6: 'Wednesday, 2:00-3:30pm',
#     7: 'Wednesday, 4:00-5:00pm',
#     8: 'Thursday, 9:00-10:30am',
#     9: 'Thursday, 11:00am-12:30pm',
#     10: 'Thursday, 2:00-3:30pm',
#     11: 'Thursday, 4:00-5:30pm' }

# def session_time(s): # yuck, this is just hardcoded
#     val = int(s)
#     assert val in SESSION_TIMES
#     return SESSION_TIMES[val]

def strip_the(name):
    name = name.replace("&eacute;", "e")
    if name.startswith("the "):
        return name[4:]
    else:
        return name

def sort_name(fullname):
    fullname = fullname.replace('&nbsp;', ' ')
    endname = fullname.find('<')
    fname = fullname[:endname]
    fname = fname.strip()
    # print("last name: " + fname)
    lastspace = fname.rfind(' ')
    if lastspace == -1:
        return fname
    assert lastspace > 1
    if fname.rfind(' van der ') > 0:
        lastspace = fname.rfind(' van der ');
    lastname = fname[lastspace:]
    sortname = lastname + ' ' + fullname
    # print("sortname: " + sortname)
    return sortname

def read_sessions(fname):
    sessions = []

    with open(fname, encoding='ISO-8859-1') as csvfile:
        sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(sreader)
        for row in sreader:
            session = {key: value for key, value in zip(headers, row)}
            if "SessionID" in session: 
                sessions.append(session)
            else:
                print("Invalid session: " + str(row))

    return sessions

def lookup_paper(papers, id):
    for paper in papers:
        if paper["ID"] == id:
            return paper

    return None

def read_papers(fname):
    papers = []
    tauthors = {}
    institutions = {}
    topics = {}

    with open(fname) as csvfile: # , encoding='ISO-8859-1') 
        sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(sreader)
        for row in sreader:
           papers.append({key: value for key, value in zip(headers, row)})

    # cleanup
    for paper in papers:
        if not paper["Title"]:
            print("No title: " + str(paper))
            papers.remove(paper)
            continue
        # print ("Paper: " + paper["Title"])
        paper['topics'] = set()
        authors = paper["Authors"]
        # remove affiliations
        nauthors = []
        fauthors = []
        for author in authors.split('; '):
            # print("Authors: " + author)
            anames = author.strip()
            affiliation = anames.find('(')
            if affiliation > 5:
                affend = anames.find(')', affiliation)
                iname = anames[(affiliation + 1):affend]
                if iname[0] == '[': # handle multiple affiliations
                    print ("maffiliations: " + iname)
                    assert iname[-1] == ']'
                    maffiliations = iname[1:-1]
                    affs = []
                    for aff in maffiliations.split('/'):
                        aff = aff.replace('$', ',')
                        affs.append(aff) 
                    print ("maffiliations: " + str(affs))
                else: # print ("Institution: " + iname)
                    assert ('(' not in iname)
                    iname = iname.replace('[', '(').replace(']',')').replace('$', ',')
                    affs = [iname]
                anames = anames[:affiliation].strip()
                assert (')' not in anames)

            anames = anames.replace(', and ', ',')
            anames = anames.replace(' and ', ',')
            for aname in anames.split(','):
                aname = aname.strip()
                if (len(aname) < 30):
                    aname = aname.replace(' ', '&nbsp;')
                # replace [ in name with (, ]->) JV
                # print("Author name: " + aname)
                aname = aname.replace('[', '(').replace(']',')')
                nauthors.append(aname)
                instnames = ' / '.join(affs)
                faname = '<span class="author">' + aname + '</span> <span class="institution">(' + instnames + ')</span>'
                fauthors.append(faname)
                frname = aname + ' </span><span class="institution">(' + instnames + ')</span>'                

                for iname in affs:
                    if iname in institutions:
                        if not paper in institutions[iname]:
                            institutions[iname].append(paper)
                    else:
                        institutions[iname] = [paper]

                if frname in tauthors:
                    tauthors[frname].append(paper)
                else:
                    tauthors[frname] = [paper]
        paper["Authors"] = ', '.join(nauthors)
        paper["FullAuthors"] = ', '.join(fauthors)

    lauthors = list(tauthors.items())
    lauthors.sort(key = lambda a: sort_name(a[0]).lower()) # abhi rule

    tinstitutions = list(institutions.items())
    tinstitutions.sort(key = lambda a: strip_the(a[0].lower()))

    print ("Reading topics...")
    with open(TOPICS_CSV) as csvfile:
        sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(sreader)
        for row in sreader:
            rowinfo = {key: value for key, value in zip(headers, row)}
            if "paper" in rowinfo:
                id = rowinfo["paper"]
                paper = lookup_paper(papers, id)
                if not paper:
                    pass # print("No submission for paper: " + str(id))
                else:
                    # print("Found paper: " + paper["Title"])
                    topicname = rowinfo["topic"]
                    assert len(topicname) > 2

                    paper['topics'].add(topicname)
                    # print ("Adding to " + topicname)
                    if topicname in topics:
                        trec = topics[topicname]
                    else:
                        trec = {'papers': []}
                        topics[topicname] = trec

                    trec['papers'].append(paper)
            else:
                 print ("No paper!")
                 
    return papers, lauthors, tinstitutions, topics

def paper_finalist(paper):
    if "BestPaperFinalist" in paper:
        bpf = paper["BestPaperFinalist"].strip()
        if len(bpf) > 0:
            assert (bpf == "1")
            return True

    return False

def paper_available(paper):
    if "PaperURL" in paper:
        paperurl = paper["PaperURL"].strip()
        if len(paperurl) > 0:
            assert (paperurl.startswith("http://") or paperurl.startswith("https://"))
            return paperurl

    return None

def artifact_available(paper):
    if "ArtifactURL" in paper:
        artifacturl = paper["ArtifactURL"].strip()
        if len(artifacturl) > 2:
            assert (artifacturl.startswith("http://") or artifacturl.startswith("https://"))
            return artifacturl

    return None

def generate_papertitle(paper, inSession=False): # True):
    title = paper["Title"]
    res = '<em>' + title + '</em>'

    url = None # acm_paper(paper)
    if url:
        res += ' <a href="' + url + '">[PDF]</a>'

    url = paper_available(paper)
    if url:
        res += ' <a href="' + url + '">[Paper]</a>'

    if artifact_available(paper):
        res += ' <a href="' + paper["ArtifactURL"] + '">[Artifact]</a>'

    # if inSession:
    #    session = paper["SessionID"]
    #    assert len(session) == 2
    #    res += ' <a href="/session-' + session + '"><font color="#777">(' + session + ')</font></a>'


    if paper_finalist(paper):
        res += ' <a href="/finalists"><font color="#FFD700">&#9733;</font></a>'

    return res

def generate_fulls_paper(paper, inSession=True):
    res = '<span class="ptitle">' + paper["Title"] + '</span></br>'
    res += '<div class="pblock">'
    res += paper["FullAuthors"] + '<br>'
    res += '<div class="pextra">'

    if paper_finalist(paper):
        res += '<a href="/finalists"><font color="#FFD700">&#9733;</font></a> (Award Finalist)<br>'

    url = None # acm_paper(paper)
    if url:
        res += ' <a href="' + url + '">[PDF]</a><br>'

    if paper_available(paper):
        res += '<a href="' + paper_available(paper) + '">[Paper]</a><br>'

    if artifact_available(paper):
        res += '<a href="' + paper["ArtifactURL"] + '">[Artifact]</a><br>'

    res += '</div>'
    res += '</div>'
    return res

def generate_fullt_paper(paper, inSession=True):
    res = '<span class="ptitle">' + paper["Title"] + '</span></br>'
    res += '<div class="pblock">'
    res += paper["FullAuthors"] + '<br>'
    res += '<div class="pextra">'

    if paper_finalist(paper):
        res += '<a href="/finalists"><font color="#FFD700">&#9733;</font></a> (Award Finalist)<br>'

    if False: # acm_paper(paper):
        res += '<a href="' + acm_paper(paper) + '">[PDF]</a><br>'

    if paper_available(paper):
        res += '<a href="' + paper_available(paper) + '">[Paper]</a><br>'

    if artifact_available(paper):
        res += '<a href="' + paper["ArtifactURL"] + '">[Artifact]</a><br>'

    ## session = paper["SessionID"]
    ## assert len(session) == 2
    ## res += 'Session: <a href="/session-' + session + '"><font color="#777">' + session[::-1] + '</font></a>'

    res += '</div>'
    res += '</div>'
    return res

def generate_full_paper(paper, inSession=True):
    fauthors = paper["FullAuthors"]
    res = fauthors + '. ' + generate_papertitle(paper, inSession) 
    return res

def generate_paper(paper, inSession=True):
    authors = paper["Authors"]
    res = authors + '. ' + generate_papertitle(paper, inSession) 
    return res

def generate_short_paper(paper):
    authors = paper["Authors"]

    res = paper["Title"] + ' (' + authors + ') '
    if paper_finalist(paper):
        res += '<a href="/finalists"><font color="#FFD700">&#9733;</font></a> '

    if False: # acm_paper(paper):
        res += '<a href="' + acm_paper(paper) + '">[PDF]</a> '

    if paper_available(paper):
        res += '<a href="' + paper_available(paper) + '">[Paper]</a> '

    if artifact_available(paper):
        res += '<a href="' + paper["ArtifactURL"] + '">[Artifact]</a>'

    return res

def generate_shortt_paper(paper):
    authors = paper["Authors"]

    res = paper["Title"] + ' (' + authors + ') '
    if paper_finalist(paper):
        res += '<a href="/finalists"><font color="#FFD700">&#9733;</font></a> '

    if False: # acm_paper(paper):
        res += '<a href="' + acm_paper(paper) + '">[PDF]</a> '

    if paper_available(paper):
        res += '<a href="' + paper_available(paper) + '">[Paper]</a> '

    if artifact_available(paper):
        res += '<a href="' + paper["ArtifactURL"] + '">[Artifact]</a>'

    ##session = paper["SessionID"]
    ## assert len(session) == 2
    ## res += ' <a href="/session-' + session + '"><font color="#777">(' + session + ')</font></a>'

    return res

def generate_short(title, authors):
    return (authors + '. <em>' + title + '</em>')
    
if __name__=="__main__":
    papers, authors, institutions, topics = read_papers(PAPERS_CSV)
    # papers.sort(key = lambda p: p["SessionID"] + p["SessionOrder"])
    papers.sort(key = lambda p: p["Title"].upper())
    
    print("Number of papers: " + str(len(papers)))
    print("Number of authors: " + str(len(authors)))
    print("Number of institutions: " + str(len(institutions)))

    # sessions = read_sessions("sessions.csv")
    # writeSessions(papers, authors, institutions, sessions)
    print("Writing papers.html...")
    with open("papers.html", "w") as f:
      f.write("""
+++
title = "IEEE EuroS&P 2022 - Accepted Papers"
+++
<p>
The following papers have been accepted to the """ + CONFERENCE_FULL + """ to be held June 6-10, 2022 in Genoa, Italy.
</p>

</p>
<p align=center>
<a href="../authors"><b>List By Authors</b></a> &middot; <a href="../institutions"><b>Institutions</b></a> &middot; <a href="../fulltopics"><b>Papers by Topic</b></a>  </p>
""")
   #   &middot; <a href="../openpapers"><b>Available Papers</b></a> &middot; <a href="../artifacts"><b>Artifacts</b></a></p>
      f.write("""   <table class="papers"> """)
      shading = False
      count = 0
      for p in papers:
          # print ("Paper: " + p["Title"] + " / Authors: " + p["Authors"])
          assert len(p["Authors"]) > 5
          row = '<td width="55%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + generate_papertitle(p) + '</td><td width="45%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + p["Authors"] + "</td>"
          f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + row + "</tr>")
          count += 1
          shading = not shading
      f.write("""   </table>""") 

    print("Writing openpapers.html...")
    count = 0
    with open("openpapers.html", "w") as f:
      f.write("""
+++
title = "IEEE Euro S&P 2022 - Available Papers"
+++
<p>
The following papers that have been accepted to appear in the <a href="https://www.ieee-security.org/TC/EuroSP2022/">7<sup>th</sup> IEEE European Symposium on Security and Privacy</a> are now openly available.
</p>
<p align=center>
<a href="/papers"><b>All Papers</b></a> &middot; <a href="/authors"><b>List By Authors</b></a> &middot; <a href="/institutions"><b>Institutions</b></a></p>
""")
      f.write("""   <table class="papers"> """)
      shading = False
      for p in papers:
          assert len(p["Authors"]) > 5
          if paper_available(p):
              row = '<td width="55%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + generate_papertitle(p) + '</td><td width="45%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + p["Authors"] + "</td>"
              f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + row + "</tr>")
              count += 1
              shading = not shading
      f.write("""   </table>""") 
      f.write("<p><center>" + str(count) + " open papers</center></p>")

    print("Writing artifacts.html...")
    with open("artifacts.html", "w") as f:
      f.write("""
+++
title = "IEEE Euro S&P 2022 - Available Artifacts"
+++
<p>
The following papers have artifacts available (in accordance with our Open Science expectations). 
</p>

<p align=center>
<a href="/papers"><b>All Papers</b></a> &middot; <a href="/authors"><b>List By Authors</b></a> &middot; <a href="/institutions"><b>Institutions</b></a></p>
""")
      f.write("""   <table class="papers"> """)
      shading = False
      for p in papers:
          assert len(p["Authors"]) > 5
          if artifact_available(p):
              row = '<td width="55%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + generate_papertitle(p) + '</td><td width="45%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + p["Authors"] + "</td>"
              f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + row + "</tr>")
              shading = not shading
      f.write("""   </table>""") 



#       # papers.sort(key = lambda p: p["ID"])
#     print("Writing finalists.html...")
#     count = 0
#     with open("finalists.html", "w") as f:
#       f.write("""
# +++
# title = "CCS 2017 - Award Finalists"
# author = "CCS PC Chairs"
# +++
# <p>
# The following 24<sup>th</sup> ACM Conference on Computer and Communications Security papers have been selected as finalists for paper awards. The awards will be announced at the CCS Banquet, 1 November 2017.
# </p>
# <p align=center>
# <a href="/papers"><b>All Papers</b></a> &middot; <a href="/authors"><b>List By Authors</b></a> &middot; <a href="/institutions"><b>Institutions</b></a></p>
# <p align=center>(Ordered by Conference Session)</p>
# """)
#       f.write("""   <table class="papers"> """)
#       shading = False
#       for p in papers:
#           assert len(p["Authors"]) > 5
#           if paper_finalist(p):
#               row = '<td width="55%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + generate_papertitle(p) + '</td><td width="45%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + p["Authors"] + "</td>"
#               f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + row + "</tr>")
#               count += 1
#               shading = not shading
#       f.write("""   </table>""") 
#       f.write("<p><center>" + str(count) + " award finalists</center></p>")

    print("Writing authors.html...")
    with open("authors.html", "w") as f:
      f.write("""
+++
title = \"""" + CONFERENCE + """ - Authors\"
+++

<p align=center>
<a href="../papers"><b>Papers</b></a> &middot; <a href="../institutions"><b>Institutions</b></a> &middot; <a href="../fulltopics"><b>Papers by Topic</b></a> 
</p>

""")

      #  &middot; <a href="../openpapers"><b>Available Papers</b></a> &middot; <a href="../artifacts"><b>Artifacts</b></a></p>
      f.write("""   <table class="papers"> """)
      shading = False
      for author in authors:
          # print("Author: " + author[0])
          f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + '<td width="38%"><span class="author">' + author[0] + "</span></td><td>")
          papers = author[1]
          papers.sort(key = lambda p: p["Title"])
          for paper in papers:
              # print("Paper: " + str(list(paper.items())))
              f.write('<div class="hanging">' + generate_paper(paper) + "</div>")
          f.write("</td></tr>")
          shading = not shading
      f.write(""" </table>""")

      
    print("Writing institutions.html...")
    with open("institutions.html", "w") as f:
      f.write("""
+++
title = \"""" + CONFERENCE + """ - Institutions\"
+++
<p align=center><a href="../papers"><b>List of Accepted Papers</b></a> &middot; <a href="../authors"><b>Authors</b></a></p>
<p>
Insitutions affiliated with authors of papers in the """ + CONFERENCE_FULL + """.


<p align=center>
<a href="../papers"><b>Papers</b></a> &middot; <a href="../institutions"><b>Institutions</b></a> &middot; <a href="../fulltopics"><b>Papers by Topic</b></a></p>

<p>


</p>

""")
#  &middot; <a href="../openpapers"><b>Available Papers</b></a> &middot; <a href="../artifacts"><b>Artifacts</b></a></p>
      f.write("""   <table class="papers"> """)
      shading = False
      for institution in institutions:
          # print("Institution: " + str(institution))
          f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + '<td width="35%"><span class="author">' + str(institution[0]) + "</span></td><td>")
          papers = institution[1]
          papers.sort(key = lambda p: p["Authors"])
          for paper in papers:
              # print("Paper: " + str(list(paper.items())))
              # f.write('<p class="hanging">' + generate_short(paper["Title"], paper["Authors"]) + "</p>")
              assert len(paper["Authors"]) > 5
              # f.write('<div class="hanging">' + paper["Authors"] + ". " + "<em>" + paper["Title"] + "</em>.</div>")
              f.write('<div class="hanging">' + generate_paper(paper) + "</div>")
          f.write("</td></tr>")
          shading = not shading
      f.write(""" </table>""")

    print("Writing topics.html...")
    with open("topics.html", "w") as f:
      f.write("""
+++
title = \"""" + CONFERENCE + """ - Topics\"
+++

<p align=center>
<a href="../fulltopics"><b>Complete List of Papers by Topic</b></a> &middot; <a href="../authors"><b>List By Authors</b></a> &middot; <a href="../institutions"><b>Institutions</b></a></p>

""")
      #  &middot;  <a href="../openpapers"><b>Available Papers</b></a> &middot; <a href="../artifacts"><b>Artifacts</b></a></p>
      topiclist = list(topics.keys())
      topiclist.sort()
      with open("fulltopics.html", "w") as ff:
          ff.write("""
+++
title = \"""" + CONFERENCE + """ - Topics"
+++
<p>
<p align="center">
Topics are based on selections by the authors. The same paper may be listed under multiple topics.
</p>

""")

          for topici in range(len(topiclist)):
              topic = topiclist[topici]
              print("Topic: " + topic)
              fshead = "<a href=\"../topic-" + str(topici) + "\"><b>" + topic + "</b></a>" 
              f.write(fshead + '<br>')
              ff.write("<p>" + fshead + ' ')
              ff.write('<br>')
              with open("topic-" + str(topici) + ".md", "w") as fs:
                  fs.write("""+++
title = \"""" + CONFERENCE + """ - Papers on """ + topic + """\"
+++
<center><a href="../topics"><b>Topics</b></a> &middot; <a href="../papers"><b>Papers</b></a></center>
<p>
<h2>""" + topic + "</h2>")
                  spapers = topics[topic]['papers']
                  ## spapers.sort(key = lambda p: p["SessionOrder"])
                  spapers.sort(key = lambda p: p["Title"].upper())
                  for paper in spapers:
                      fs.write("<div class=\"bpaper\">");
                      fs.write(generate_fullt_paper(paper, inSession=False))
                      fs.write("</div>");

                      ff.write("<div class=\"hanging\">")
                      ff.write(generate_shortt_paper(paper))
                      ff.write("</div>\n")
              ff.write("</p>")
