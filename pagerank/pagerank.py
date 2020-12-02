import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # if page has no outgoing links
    transition_dict = dict()
    if len(corpus[page]) == 0:
        for key in corpus:
            transition_dict[key] = 1/len(corpus)
        return transition_dict
    else:
        # probability to choose a page randomly
        rand_prob = (1 - damping_factor)/len(corpus)

        # probability to choose itself
        for key in corpus:
            transition_dict[key] = rand_prob

        # probability to choose a link page
        links = corpus[page]
        divisor = len(links) if len(links) > 1 else 1
        link_prob = (damping_factor / divisor)
        for pages in links:
            transition_dict[pages] += link_prob

        for key in corpus:
            transition_dict[key] = round(transition_dict[key], 4)
        return transition_dict





def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pagerank = dict()
    pages = list(corpus.keys())

    for i in range(1, n + 1):
        if i == 1:
            # random sample
            page = random.choice(pages)
            pagerank[page] = 1
        else:
            # sample based on transition model
            if len(corpus[page]) != 0:
                page_links = list(corpus[page])
                page = random.choice(page_links)
            transition = transition_model(corpus, page, damping_factor)
            population = list()
            weight = list()
            for key in transition:
                population.append(key)
                weight.append(transition[key])
            choice = random.choices(population, weight, k=1)
            escolha = choice[0]
            if escolha in pagerank:
                pagerank[escolha] += 1
            else:
                pagerank[escolha] = 1
    for key in pagerank:
        pagerank[key] = pagerank[key] / n
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    d = damping_factor
    error = 0.001
    PR_i = dict()
    NumLinks = dict()
    links = dict()
    n = len(corpus)

    for key in corpus:
        links[key] = set()
        if len(corpus[key]) == 0:
            corpus[key] = set(corpus.keys())
    for key in corpus:
        for link in corpus[key]:
            links[link].add(key)
        NumLinks[key] = len(corpus[key])

    # all pages starts with the same PR
    for key in corpus:
        PR_i[key] = 1 / n

    while True:
        PR_p = dict()
        for key in corpus:
            PR_p[key] = (1 - d) / n
            for link in links[key]:
                PR_p[key] += d * PR_i[link] / NumLinks[link]

        repeat = 0
        for key in corpus:
            if abs(PR_p[key] - PR_i[key]) > error:
                repeat += 1
            PR_i = PR_p

        if repeat == 0:
            break
    return PR_i


if __name__ == "__main__":
    main()
