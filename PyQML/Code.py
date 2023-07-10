import inspect, re, dill, os, sys

def privateAttrDeclar(code, toAdd, pos="before init"):
    """Add a string to declar a privat class attribute (between class and init declaration)
    
    Arguments:
        code {str} -- Code where the other code should be added
        toAdd {str} -- Input code to add
    
    Keyword Arguments:
        pos {str} -- Insert position "befor init" or "after class" (default: {"before init"})
    
    Returns:
        [str] -- Code changed
    """
    if pos == "before init":
        return re.sub(r"(.*\s+)(.+)(def\s+__init__\s*\()", r"\1\2"+toAdd+r"\n\2\3", code, count=1)
    elif pos == "after class":
        return re.sub(r"(class\s+\w+\(.*\):\s*[\n]{1})([ ]+)(\S+)", r"\1\2"+toAdd+r"\n\2\3", code, count=1)

def funcLineDeclar(codeLines, toAdd, funcName="__init__"):
    """Add a string to declar a public class attribute from the init declaration
    
    Arguments:
        codeLines {str} -- Code where the other code should be added
        toAdd {str} -- Input code to add
    
    Returns:
        [str] -- Code changed
    """
    return re.sub(r"(def\s+"+funcName+r"\s*\(.*\):\s*[\n]{1})([ ]+)(\S+)", r"\1\2"+toAdd+r"\n\2\3", codeLines, count=1)# add to init

def addInheritageDeclar(codeLines, toAdd):
    """Add a string which is a class inheritage type name
    
    Arguments:
        codeLines {str} -- Code where the other code should be added
        toAdd {str} -- Input code to add
    
    Returns:
        [str] -- Code changed
    """
    return re.sub(r"(class\s+\w+\()(.*\):)", r"\1"+toAdd+r",\2", codeLines, count=1)



## search a pattern and return all match obj
def searchAll(pattern, _str, count=-1, subPattern=None):
    """ Compile the pattern and use search method across the given str to return a list of re match object(s)
    
    Arguments:
        _str {str} -- Input string
    
    Keyword Arguments:
        count {int} -- Stop the matching when the nb of matched objs up to count value (default: {-1} until the _str end)
        subPattern {str} -- Replace from re match span by it
    
    Returns:
        [list] -- Match objects list
    """
    pos = []
    # simulate the match object end() method for the first itteration
    class match():
        def end(self):
            return 0
    match = match()
    # compile re pattern
    cp = re.compile(pattern)
    while match!=None and (count==-1 or count>=0):
        # set the last match end index at the start of the next maching
        match = cp.search(_str, match.end())
        if match:
            pos.append(match)
            if not count<0:
                count-=1
    return pos
