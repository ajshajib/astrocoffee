# -*- coding: utf-8 -*-
"""
Paper object to store the associated information from a submitted url or an
arXiv ID. This module defines the following classes:

- `Paper`, schema for the associated information of a paper
- `SubmittedPaper`, extends `Paper` to process a submitted url.

"""

import requests
import datetime


class Paper(object):
    """
    Define the schema for the associated information of a paper.
    """

    def __init__(self):
        """
        Declare the variables to store the associated information.
        """
        self.url = ''
        self.author = ''
        self.author_number = 0
        self.title = ''
        self.date_submitted = ''
        self.date_extended = ''
        self.abstract = ''
        self.subject = ''
        self.sources = ''
        self.volunteer = ''
        self.discussed = ''
        self.errors = '0'


class SubmittedPaper(Paper):
    """
    Process submitted url and store the associated information.

    Extend `Paper`.
    """

    def __init__(self, url):
        """
        Extend `Paper.__init()__`. Keep the submitted unprocessed url in
        `self._raw_url` and the arXiv url prefix in `self._arxiv_prefix`.
        Declare `self.html` to contain the html from the url.

        :param url: Raw submitted url or arXiv id.
        :type url: str
        """
        Paper.__init__(self)

        self._raw_url = url
        self._arxiv_prefix = 'http://arxiv.org/abs/'
        self.html = ''

        self._set_dates()
        self._process_url(url)

    def _set_dates(self):
        """
        Set current date in `self.date_submitted` and `self.date_extended`.

        :return: None.
        :rtype: None
        """
        now = datetime.datetime.now()
        self.date_submitted = now.strftime('%Y-%m-%d %H:%M:%S')
        self.date_extended = now.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _clean_arxiv_id(id):
        """
        Extract arXiv id from a url to arXiv pdf.

        :param id: String containing arXiv ID.
        :type id: str
        :return: Extracted arXiv ID.
        :rtype: str
        """
        pdf_index = id.find('pdf/')
        id = id.rstrip('.pdf')
        id = id[pdf_index + 4:]  # Extract arXiv id from remaining text
        return id

    def _clean_url(self, url):
        """
        Clean up various paper urls.

        :param url: Url or arXiv id.
        :type url: str
        :return: Cleaned up url or arXiv id.
        :rtype: str
        """
        url = str(url).strip()

        # Check if arXiv ID is a pdf
        if 'pdf' in url and 'arxiv.org' in url:
            url = self._clean_arxiv_id(url)

        # Check if Science ID is not link to full article
        if 'science.sciencemag.org' in url and '.full' not in url:
            url = url + '.full'

        # Check if PRL submission is a pdf
        if '/pdf/' in url and 'journals.aps.org/prl' in url:
            url = url.replace('/pdf/', '/abstract/')

        return url

    def _get_arxiv_url(self, url):
        """
        Process an arXiv id or url to point to the abstract page.

        If `id` is not an arXiv url, return as it is.

        :param id: arXiv id or url.
        :type id: str
        :return: Url to arXiv abstract if an arXiv id/url, else the input url.
        :rtype: str
        """
        # Check for the various types of arXiv identifiers
        if '.' in url and url.replace('.', '', 1).isdigit():
            # It's just a number so put the arXiv url prefix in front of it
            self.is_arxiv = len(url) >= 9
            url = self._arxiv_prefix + url
        else:
            # It's not just numbers. Look for arxiv:###... style, but not
            # valid arxiv.org addresses that were submitted
            arxiv_words = ['arxiv', 'arXiv']
            if any(x in url for x in arxiv_words) and \
                    '.org' not in url and '.gov' not in url:
                self.is_arxiv = True
                url = self._arxiv_prefix + url
            else:
                self.is_arxiv = False

        return url

    def _is_webpage(self, url):
        """
        Check if a webpage exists.

        :param url: Url of the webpage.
        :type url: str
        :return: Url of the webpage if it exists, or `None`.
        :rtype: str
        """
        try:
            request = requests.get(url)
            if request.status_code == 200:
                self.html = request.text
                return url
            else:
                if not url.startswith('http://'):
                    request = requests.get('http://' + url)
                    if request.status_code == 200:
                        self.html = request.text
                        return 'http://' + url
                    else:
                        if not url.startswith('http://www.'):
                            request = requests.get('http://www.' + url)
                            if request.status_code == 200:
                                self.html = request.text
                                return 'http://www.' + url
        except:
            self.errors = 'invalid url'

        return None

    def _process_url(self, url):
        """
        Store the associated information from a paper url.

        :param url: Url pointing to the paper.
        :type url: str
        :return: None.
        :rtype: None
        """

        url = self._clean_url(url)
        url = self._get_arxiv_url(url)
        url = self._is_webpage(url)

        if url is not None:
            self.url = url
        else:
            self.errors = 'Error reading ' + self._raw_url
            self.url = ''

    def retrieve_html(self):
        """
        Get the html of the page at `self.url`.

        :return: None
        :rtype: None
        """
        if self.url != '':
            request = requests.get(self.url)
            if request.status_code == 200:
                self.html = request.text
            else:
                self.errors = 'Error reading' + self.url