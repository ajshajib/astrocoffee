# -*- coding: utf-8 -*-
"""
Process the submitted url or arXiv ID and collect the associated information
in a SubmittedPaper object. This module exports the following function:

`get_paper`: returns a SubmittedPaper from a url/arXiv ID.

Example:
.. code-block::

    url = 'https://arxiv.org/abs/1604.03939'
    submitted_paper = get_paper(url)

To-do:
- complete the other functions to handle non-arXiv urls.

"""

from bs4 import BeautifulSoup as bs
import re

from .paper import SubmittedPaper


def get_paper(url):
    """
    Get the paper information from `url` and store it in `paper`.

    :param url: Url of the paper.
    :type url: str
    :return: SubmittedPaper object containing associated information.
    :rtype: SubmittedPaper
    """
    paper = SubmittedPaper(url)

    if paper.html == '':
        paper.retrieve_html()

    if paper.errors == '0':
        if 'nature.com' in paper.url:
            if 'nature.com/news/' in paper.url:
                paper = _set_web_info(paper)
            else:
                paper = _set_nature_info(paper)
        elif 'adsabs.harvard.edu' in paper.url:
            paper = _set_ads_info(paper)
        elif 'arxiv.org' in paper.url or 'xxx.lanl.gov' in paper.url or \
                (hasattr(paper, 'is_arxiv') and getattr(paper, 'is_arxiv')):
            paper = _set_arxiv_info(paper)
        elif 'aanda.org' in paper.url:
            paper = _set_aanda_info(paper)
        elif 'mnras.oxfordjournals.org' in paper.url:
            paper = _set_mnras_info(paper)
        elif 'science.sciencemag.org' in paper.url:
            paper = _set_science_info(paper)
        elif 'physicstoday.scitation.org' in paper.url:
            paper = _set_physicstoday_info(paper)
        elif 'journals.aps.org/prl/' in paper.url:
            paper = _set_prl_info(paper)
        elif 'voxcharta.org' in paper.url:
            paper = _set_voxcharta_info(paper)
        elif 'vixra.org' in paper.url:
            paper = _set_vixra_info(paper)
        else:
            paper = _set_web_info(paper)

        return paper
    else:
        return None


def _set_arxiv_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    # Remove all the muck that screws up the BeautifulSoup parser
    # Will fail on PDF submission, so take care of that exception first
    try:
        fixed_html =re.sub(re.compile("<!--.*?-->", re.DOTALL), "", paper.html)
        soup = bs(fixed_html, 'lxml')
        paper.errors = '0'
    except:
        return None

    # Grab the Title, Date, and Authors, and all the other stuff
    try:
        paper.title = soup.find('h1',
                                {'class': 'title mathjax'}).contents[1].string
    except:
        paper.errors = '1'
        paper.title = 'Error Grabbing Title'

    #print paper.title + "\n"

    try:
        authors = soup.find('div', {'class': 'authors'})
        authors = authors.findAll('a')
        paper.author_number = len(authors)
        # Convert the authors to strings only and replace the relative links
        author_list = []
        for i in authors:
            author_list.append(str(i).replace('/find/',
                                              'http://arxiv.org/find/'))
        paper.author = ', '.join(author_list[0:4])
        # Kill all affiliation marks since some have them and some don't; done
        # in two steps to take care of nested parens
        paper.author = re.sub(r'\([^()]*\)', '', paper.author)
        paper.author = re.sub(r'\([^()]*\)', '', paper.author)
    except:
        paper.errors = '1'
        paper.author = 'Error Grabbing Authors'

    #   print paper.errors + paper.author + "\n"

    try:
        date = soup.find('div', {'class':'submission-history'})
        date = date.findAll(text=True) # Remove HTML tags
        date = list(dict.fromkeys(date)) # ignoring multiple \n's
        date = date[-1].split() # Most recent revision date will be the last
        paper.date = date[1] + ' ' + date[2] + ' ' + date[3]
    except:
        paper.errors = '1'
        paper.date = 'Error Grabbing Date'

    #   print paper.errors + paper.date + "\n"

    try:
        paper.abstract = soup.find('blockquote',
                                   {'class': 'abstract mathjax'}).contents[2]
    except:
        paper.errors = '1'
        paper.abstract = 'Error Grabbing Abstract'

    #   print paper.errors + paper.abstract + "\n"

    try:
        sources = soup.find('div', {'class': 'full-text'})
        sources  = sources.findAll('a')
        source_list=[]
        for source in sources:
            source = str(source)
            source = source.replace('/ps','http://arxiv.org/ps')
            source = source.replace('/pdf','http://arxiv.org/pdf')
            source = source.replace('/format','http://arxiv.org/format')
            source = source.replace('PostScript','PS')
            source = source.replace('Other formats','Other')
            if 'license' in source:
                continue
            source_list.append(source)
        paper.sources = ' '.join(source_list)
    except:
        paper.errors = '1'
        paper.sources = ''

    #   print paper.errors + paper.sources + "\n"

    try:
        paper.subject = soup.find('span', {'class': 'primary-subject'}).string
    except:
        paper.errors = '1'
        paper.subject = 'Error Grabbing Subject'

    #   print paper.errors + paper.subject + "\n"

    #try:
    #paper.comments = soup.find('td', {'class':'tablecell comments'}).string
    #except:
        #paper.errors = "1"
        #paper.comments = "Error Grabbing Comments"

    return paper


def _set_web_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_nature_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_ads_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_aanda_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_mnras_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_science_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_physicstoday_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_prl_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_voxcharta_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass


def _set_vixra_info(paper):
    """
    Retrieve paper information from the html.

    :param paper: SubmittedPaper object to scrape html information.
    :type paper: SubmittedPaper
    :return: SubmittedPaper object with html information retrieved.
    :rtype: SubmittedPaper
    """
    pass
