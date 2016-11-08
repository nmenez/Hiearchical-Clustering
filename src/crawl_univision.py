import searchengine


# website = {'http://es.wikipedia.org/wiki/Wikipedia:Portada'}
website={'http://www.univision.com/'}


crawler = searchengine.crawler('searchindex5.db')
crawler.createindextables()
crawler.crawl(website)


