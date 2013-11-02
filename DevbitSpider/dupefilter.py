from scrapy.dupefilter import RFPDupeFilter
from scrapy.utils.request import request_fingerprint
from scrapy import log
import os

class CustomDupeFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    def __init__(self, path=None):
        self.urls_seen = set()
        RFPDupeFilter.__init__(self, path)

    def request_seen(self, request):
        level = self.determine_level(request)
        if level == 5:
            fp = request_fingerprint(request)
            if fp in self.fingerprints:
                return True
            self.fingerprints.add(fp)
            if self.file:
                self.file.write(fp + os.linesep)

    def log(self, request, spider):
        if self.logdupes:
            fmt = "Filtered duplicate request: %(request)s"
            log.msg(format=fmt, request=request, level=log.DEBUG, spider=spider)
            #self.logdupes = False

    def determine_level(self, request):
        """
        determine the index level of current response, so we can decide wether to continue crawl or not.
        level 1: people/[a-z].html
        level 2: people/[A-Z][\d+].html
        level 3: people/[a-zA-Z0-9-]+.html
        level 4: search page, pub/dir/.+
        level 5: profile page
        """
        import re
        url = request.url
        if re.match(".+-[a-z]$", url):
            return 1
        elif re.match(".+-[a-z]-\d+$", url):
            return 2
        elif re.match(".+-[a-z]-\d+-\d+$", url):
            return 3
        elif re.match(".+/pub/dir/.+", url):
            return 4
        elif re.match(".+/vsearch/.+", url):
            return 4
        elif re.match(".+/pub/.+", url):
            return 5
        elif re.match(".+/in/.+", url):
            return 5
        return None