import feedparser
import re


def getwordcounts(url):
    d = feedparser.parse(url)
    wc = {}
    for e in d.entries:

        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description

        words = getwords(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1

    return d.feed.title, wc


def getwords(html):
    txt = re.compile(r'<[^>]+>').sub('', html)
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    return(word.lower() for word in words if word != '')


def generatefeedvector():
    apcount = {}
    wordcounts = {}
    feedlist = []

    with open('..//data//feedlist.txt', 'r') as feedlist_txt:
        for feedurl in feedlist_txt:
            feedlist.append(feedurl)
            try:
                title, wc = getwordcounts(feedurl)
                wordcounts[title] = wc
                for word, count in wc.items():
                    apcount.setdefault(word, 0)
                    if count >= 1:
                        apcount[word] += 1

            except:
                print(feedurl + ': no good')

    wordlist = []
    for w, bc in apcount.items():
        frac = float(bc) / len(feedlist)
        if frac > 0.1 and frac < 0.5:
            wordlist.append(w)
        else:
            print('booting ' + w + ' ' + str(frac))

    with open('..//data//blogdata.txt', 'w') as out:
        out.write('Blog')
        for word in wordlist:
            out.write('\t%s' % word)
        out.write('\n')
        for blog, wc in wordcounts.items():
            #blog = blog.encode('ascii', 'ignore')
            if isinstance(blog, str):
                out.write(blog)
            else:
                print(blog, blog.__class__)
            for word in wordlist:
                if word in wc:
                    out.write('\t%d' % wc[word])
                else:
                    out.write('\t0')

            out.write('\n')


if __name__ == "__main__":
    generatefeedvector()
