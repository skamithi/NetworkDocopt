
from ipaddr import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from re import match as re_match, search as re_search
from sys import argv

debug = False

class Token():

    def __init__(self, text, required):
        self.text = text
        self.words = text.split('|')
        self.required = required
        self.key_text = text
        self.value = False

    def __str__(self):
        return self.text

    def matches(self, argv_text):

        if not argv_text:
            return False

        for word in self.words:

            # Variable input <ip>, <number>, etc
            if word.startswith('<'):

                if word == '<ip>' or word == '<source-ip>':
                    if re_match('\d+\.\d+\.\d+\.\d+', argv_text):
                        self.key_text = word
                        self.value = argv_text
                        return True

                elif word == '<ip/mask>':
                    if re_match('\d+\.\d+\.\d+\.\d+\/\d+', argv_text):
                        self.key_text = word
                        self.value = argv_text
                        return True

                elif word == '<interface>':

                    if re_match('\w+\d+', argv_text):
                        self.key_text = word
                        self.value = argv_text
                        return True

                    if argv_text == 'lo':
                        self.key_text = word
                        self.value = argv_text
                        return True

                elif word == '<name>' or word == '<cleartext>':
                    self.key_text = word
                    self.value = argv_text
                    return True

                elif word == '<major>' or word == '<minor>' or word == '<number>':
                    if argv_text.isdigit():
                        self.key_text = word
                        self.value = int(argv_text)
                        return True

            # Keyword
            else:
                if argv_text == word:
                    self.key_text = word
                    self.value = True
                    return True

                elif word.startswith(argv_text):
                    self.key_text = word
                    self.value = True
                    return True

        return False

class CommandSequence():
    def __init__(self, string):

        self.option = None
        self.score = 0

        # Remove leading and trailing whitespaces
        self.text = string.strip()

        # Compress duplicate spaces into single space
        self.text = ' '.join(self.text.split())
        tmp_tokens = self.text.split(' ')[1:]
        self.text = ' '.join(tmp_tokens)

        # Now that we know each word is separated by a single whitespace split
        # on whitespace. Ignore the first token which is the program name.
        self.tokens = []
        for x in tmp_tokens:

            if x.startswith('('):

                # Remove the leading and trailing ()s
                x = x[1:-1]
                token = Token(x, True)

            elif x.startswith('['):

                # Remove the leading and trailing []s
                x = x[1:-1]
                token = Token(x, False)

            elif x.startswith('--'):
                token = Token(x, False)

            else:
                token = Token(x, True)

            self.tokens.append(token)

    def argv_matches_tokens(self, argv):
        len_argv = len(argv)

        if len_argv > len(self.tokens):
            if debug:
                print "%-70s: %d argv words but we only have %d tokens" % (self.text, len_argv, len(self.tokens))
            return False

        argv_index = 0
        for token in self.tokens:
            if argv_index < len_argv:
                text_argv = argv[argv_index]
            else:
                text_argv = None

            if token.required:

                if not token.matches(text_argv):
                    if not argv_index:
                        self.score -= 1

                    self.option = token.text.split('|')
                    if debug:
                        print "%-70s: Required token '%s' failed to match vs. argv[%d] '%s'" % (self.text, token.text, argv_index, text_argv)
                    return False

                argv_index += 1
                self.score += 1
            else:
                if token.matches(text_argv):
                    argv_index += 1
                    self.score += 1

        if self.score != len_argv:
            if debug:
                print "%-70s: %d/%d argv words matches" % (self.text, self.score, len_argv)
            return False

        if debug:
            print "%-70s: MATCH" % (self.text)
        return True

"""
Heavily influenced by docopt but designed to be a little more like
a Networking CLI with partial word acceptance, IPv4 sanity checking, etc
"""
class NetworkDocopt():
    def __init__(self, docstring):
        self.args    = {}
        self.match   = False
        self.options = []
        self.program = None
        self.closest_matches = []

        # Parse the 'Usage' section of the doc string.  Create a
        # CommandSequence object for every line in Usage, store those
        # objects on the self.commands list.
        state = None
        self.commands = []
        for line in docstring.split('\n'):
            if line.startswith('Usage'):
                state = 'Usage'
                continue
            elif line.startswith('Help'):
                break
            elif line.startswith('Options'):
                break
            elif line == '':
                continue

            if state == 'Usage':
                self.commands.append(CommandSequence(line))

                if self.program is None:
                    result = re_search('^\s+(\S+)', line)
                    if result:
                        self.program = result.group(1)

        # Now loop over all of the CommandSequence objects and build a list
        # of every kind of token in the doc string
        self.all_tokens = []
        for cmd in self.commands:
            for token in cmd.tokens:
                self.all_tokens += token.words
        self.all_tokens = set(self.all_tokens)

        # The 1st item in argv is prcli...ignore it
        self.argv = argv[1:]

        # Init all tokens in args to False
        for x in self.all_tokens:
            self.args[x] = False

        candidates = []
        for cmd in self.commands:
            if cmd.argv_matches_tokens(self.argv):
                candidates.append(cmd)

        # This is a bad thing
        if not candidates:

            high_score = -1
            scores = {}
            options_by_score = {}

            for cmd in self.commands:
                score = cmd.score

                if score > high_score:
                    high_score = score

                if score not in scores:
                    scores[score] = []

                if score not in options_by_score:
                    options_by_score[score] = []

                if cmd.option:
                    options_by_score[score] += cmd.option
                scores[score].append(cmd)

            if high_score in scores and scores[high_score]:
                self.closest_matches.append('')
                self.closest_matches.append('Closest Matches:')

                for cmd in scores[high_score]:
                    self.closest_matches.append('    %s %s' % (self.program, cmd.text))
                self.closest_matches.append('')

            if high_score in options_by_score and options_by_score[high_score]:
                self.options = sorted(set(options_by_score[high_score]))

        # This is a good thing
        elif len(candidates) == 1:
            cmd = candidates[0]

            for token in cmd.tokens:
                self.args[token.key_text] = token.value
                if debug:
                    print "args key: %s, value: %s" % (token.key_text, token.value)

            self.match = True

            if cmd.option:
                self.options = cmd.option

        else:
            print "\nERROR: ambiguous parse chain\n"

    def print_options(self):
        if self.options:
            print '\n'.join(self.options)
            with open("/var/log/dwalton.log", "a") as myfile:
                myfile.write(' '.join(self.argv))
                myfile.write('\n')
                myfile.write('\n'.join(self.options))
                myfile.write('\n')
                myfile.write('\n')
