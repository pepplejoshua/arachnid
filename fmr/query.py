""" Query for Filenames """

class Query:
    """A class for holding user query combination used to scope searches for files.
    """
    def __init__(self, keyword, searchType):
        """Initialization function.

        Args:
            keyword (str): String term for matching file name
            searchType (str): String representation of selected search type \
                used for selecting matching type (startswith, endswith, contains)
        """
        self.keyword = keyword
        self.searchType = searchType