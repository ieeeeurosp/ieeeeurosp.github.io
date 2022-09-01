###
### process.py -> posters.py
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
POSTERS_CSV = "/Users/dave/Dropbox/eurosp22posters-finals/eurosp22posters-data.csv"
## PAPERS_CSV = "/Users/dave/Dropbox/EuroSP/conference/test.csv"
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

def lookup_paper(papers, id):
    for paper in papers:
        if paper["ID"] == id:
            return paper

    return None

def read_posters(fname):
    posters = []
    tauthors = {}
    institutions = {}
    topics = {}

    with open(fname, encoding='utf-8') as csvfile: # ) 
        sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(sreader)
        for row in sreader:
           posters.append({key: value for key, value in zip(headers, row)})

    # cleanup
    for paper in posters:
        if not paper["Title"]:
            print("No title: " + str(paper))
            posters.remove(paper)
            continue
        # print ("Paper: " + paper["Title"])
        paper['topics'] = set()
        authors = paper["Authors"]
        # remove affiliations
        nauthors = []
        fauthors = []
        if '),' in authors:
            print ("Problem: " + authors)
        for author in authors.split('; '):
            # print("Authors: " + author)
            anames = author.strip()
            affiliation = anames.find('(')
            if affiliation > 5:
                affend = anames.find(')', affiliation)
                iname = anames[(affiliation + 1):affend]
                if iname[0] == '[': # handle multiple affiliations
                    # print ("maffiliations: " + iname)
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
                paper = lookup_paper(posters, id)
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
                        trec = {'posters': []}
                        topics[topicname] = trec

                    trec['posters'].append(paper)
            else:
                 print ("No paper!")
                 
    return posters, lauthors, tinstitutions, topics

def generate_papertitle(paper, artifactURL=False, inSession=False, openURL=False): # True):
    num = paper["ID"]
    title = paper["Title"]
    res = '<A href="//2022/posters/eurosp22posters-final' + str(num) + '.pdf"><em>' + title + '</em></a>'

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
    res = fauthors + '. ' + generate_papertitle(paper, inSession=inSession) 
    return res

def generate_paper(paper, inSession=False):
    authors = paper["Authors"]
    res = authors + '. ' + generate_papertitle(paper, inSession=inSession) 
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
    posters, authors, institutions, abstract = read_posters(POSTERS_CSV)
    posters.sort(key = lambda p: p["Title"].upper())
    
    print("Number of posters: " + str(len(posters)))
    print("Number of authors: " + str(len(authors)))
    print("Number of institutions: " + str(len(institutions)))

    # sessions = read_sessions("sessions.csv")
    # writeSessions(posters, authors, institutions, sessions)
    print("Writing posters.html...")
    with open("posters.html", "w") as f:
      f.write("""
+++
title = "IEEE EuroS&P 2022 - Posters"
+++
<p>
The following posters were accepted to the """ + CONFERENCE_FULL + """ and presented at the conference held June 6-10, 2022 in Genoa, Italy.
</p>

</p>
""")
   #   &middot; <a href="https://ieeeeurosp.github.io/2022/openposters"><b>Available Posters</b></a> &middot; <a href="https://ieeeeurosp.github.io/2022/artifacts"><b>Artifacts</b></a></p>
      f.write("""   <table class="posters"> """)
      shading = False
      count = 0
      for p in posters:
          print ("Poster: " + p["Title"] + " / Authors: " + p["Authors"])
          assert len(p["Authors"]) > 5
          row = '<td width="55%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + generate_papertitle(p) + '</td><td width="45%" style="padding: 10px; border-bottom: 1px solid #ddd;">' + p["Authors"] + "</td>"
          f.write(("<tr>" if shading else "<tr bgcolor=\"E6E6FA\">") + row + "</tr>")
          count += 1
          shading = not shading
      f.write("""   </table>""") 

