import urllib.request
import urllib.parse
from html.parser import HTMLParser

class DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_a = False
        self.curr_href = ''
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, val in attrs:
                if name == 'href' and 'ad_domain' not in val:
                    self.in_a = True
                    self.curr_href = val
    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_a = False
    def handle_data(self, data):
        if self.in_a and self.curr_href.startswith('//duckduckgo.com/l/?uddg='):
            actual = urllib.parse.unquote(self.curr_href.split('uddg=')[1].split('&')[0])
            self.links.append((actual, data))

def search(query):
    req = urllib.request.Request(
        f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        p = DDGParser()
        p.feed(html)
        print(f"--- Results for: {query} ---")
        for l, d in p.links[:3]:
            print(f"{l}\n  {d.strip()}")
    except Exception as e:
        print(f"Error for {query}: {e}")

search("site:csn.se study grant and student loan english")
search("site:migrationsverket.se moving to sweden english")
search("site:migrationsverket.se apply for a work permit english")
search("site:skatteverket.se personal identity number english")
search("site:skatteverket.se declaring taxes english")
