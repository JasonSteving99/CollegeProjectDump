# Description: This program solves a heavily extended version of the 
#   match.py program assigned in 499 for 3/9/16. Not only does it 
#   determine if the given pattern can be found in a string, but it will
#   report the starting and ending indices of the actual string matched
#   which can easily be used to grab the actual substring itself.
#
#   The biggest extension and by far the most important, though, is the
#   idea of "compiling" the pattern to return a DFA for to match that
#   pattern. This concept is entirely an attempt at creating a tool that
#   emulates Python's built-in regular expression class (i.e. re.compile(...))
#   The massive benefit of doing this is that if you want to use this
#   expression to find matches in more than one string it is far more 
#   efficient to build up the DFA before checking for any matches, as you
#   avoid having to make multiple passes through the many conditions 
#   necessary to parse the various expressions making up the pattern. From
#   my tests I'd guess that this probably shaves a quarter to half the runtime
#   once you start passing larger numbers of strings as arguments (or much 
#   longer patterns) by simply not having to go through all of the 
#   conditions repeatedly.
#
# Usage: python match-extended.py [pattern] [string] [string] [string] ... etc
###########################################################################
import sys


def compile_pattern(pattern):
    if pattern[0] == '^':
        DFA = build_DFA(pattern[1:])
    else:
        DFA = build_DFA('.*' + pattern)
    return DFA  #DFA = Deterministic Finite State Automaton


'''This function builds up and returns a single composed function (essentially 
   daisy chained) which will take any string and return a boolean stating 
   whether the given pattern can be found within.'''


def build_DFA(pattern, i=0):
    if i == len(pattern):  #somehow got to the end of the pattern. success
        return accept_node()  #there will be no next pattern to match
    elif i + 1 < len(pattern) and pattern[i + 1] == '*':
        return match_star_node(pattern[i], build_DFA(pattern, i + 2))
    #dollar has special meaning at end of pattern
    elif i == len(pattern) - 1 and pattern[i] == '$':
        return match_dollar_node(build_DFA(pattern, i + 1))
    else:  #match a character literal or dot
        return match_char_node(pattern[i], build_DFA(pattern, i + 1))


'''The following functions are all defined to implement the concept of a
   "Partial Application" to build a list of functions that can be initialized
   with partial state, a.k.a. at the very least what function will be called
   next, so that once we find out the rest of the state, a.k.a. the particular
   string and the index in that string to try to find a match in, we can move
   ahead and perform the checks necessary to match the pattern specified. 

   NOTE: Another way I thought of that I could've done this would be with 
   lambdas up in build_DFA and just making regular functions that take all 
   the parameters they need for example:   
	def match_dot(next_node, s, i):
		....
	
	return lambda (s, i) : match_dot(build_DFA(pattern, i+1), s, i)

   It's worth noting that all of this is literally done JUST TO AVOID THE
   TRIVIAL OO SOLUTION to this idea of partial applications.'''


def match_dollar_node(next_node):
    def match_dollar(s, i=0):
        if i == len(s):
            res, _, end = next_node(s, i + 1)
            if res == True:
                return True, i, end
        return False, i, i

    return match_dollar


#given a char, match it as many times as possible
def match_star_node(c, next_node):
    def match_star(s, i=0):
        j = i  #determine the farthest point to use for what the star consumes
        while j < len(s) and s[j] == c:
            j += 1
        last = len(s) if c == '.' else j  #dot star could always go to end
        #try successive continuing points after consuming star pattern
        for k in xrange(i, last + 1, 1):
            res, _, end = next_node(s, k)  #matched 0 or more and move on
            if res == True:
                return True, i, end
        return False, i, i  #exhausted all continuing points, match never found

    return match_star


def match_char_node(c, next_node):
    def match_char(s, i=0):
        match_dot = c == '.'
        if i < len(s) and (match_dot or c == s[i]):
            res, _, end = next_node(s, i + 1)
            return res, i, end
        else:
            return False, i, i

    return match_char


def accept_node():
    def accept(s, i=0):
        return True, i - 1, i - 1

    return accept


if __name__ == '__main__':
    pattern = sys.argv[1]
    match = compile_pattern(pattern)

    for s in sys.argv[2:]:
        print "Check {0}".format(s)
        matched, start, end = match(s)
        print matched
        if matched:
        	print s[start : end + 1]
        print
