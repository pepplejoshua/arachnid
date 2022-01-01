from termcolor import cprint
from colorama import init
init()

def coprint(obj, colr='grey', bckgrnd='on_grey', attrb=[]):
    """This function acts a custom interface to the termcolor.cprint()
    function.

    Args:
        strng (str): String to be color printed
        colr (str, optional): This is the main text color used for the print. Use termcolor color strings.\
            Defaults to 'grey'.
        bckgrnd (str, optional): This is the main text color used for the print. Use termcolor color strings.\
            Defaults to 'on_grey'.
        attrb (list, optional): This is the list of attributes to be applied to be text. e.g: `"bold"`. Defaults to [].
    """
    cprint(obj, colr, bckgrnd, attrs=attrb)