try:
    import ipaddress
except ImportError:
    import ipaddr as ipaddress
from re import match as re_match, search as re_search
from os import listdir
import sys
import logging

""" change to logging.DEBUG when running debugs"""
logging.basicConfig(level=logging.WARN)

class Token():

    def __init__(self, text, required):
        self.text = text
        self.words = text.split('|')
        self.required = required
        self.key_text = None
        self.value = False
        self.exact_match = False

    def __str__(self):
        return "REQUIRED: %s, KEY_TEXT: %s, VALUE: %s, WORDS: %s" % (self.required, self.key_text, self.value, self.words)

    def options(self):
        results = []

        for word in self.words:
            if word.startswith('<'):

                if word == '<interface>':
                    results.extend([x for x in listdir('/sys/class/net/') if x != 'bonding_masters'])
                else:
                    results.append(word)

            # Keyword
            else:
                results.append(word)

        return results

    def matches(self, argv_text, all_tokens):

        if not argv_text:
            return False

        for word in self.words:

            # Variable input <ip>, <number>, etc
            if word.startswith('<'):

                if word == '<ip>' or word == '<source-ip>':
                    try:
                        ipv4_or_ipv6 = ipaddress.IPAddress(argv_text)
                        self.key_text = word
                        self.value = argv_text
                        self.exact_match = True
                        return True
                    except:
                        pass

                elif word == '<ip/mask>':
                    try:
                        ipv4_or_ipv6 = ipaddress.IPNetwork(argv_text)
                        self.key_text = word
                        self.value = argv_text
                        self.exact_match = True
                        return True
                    except:
                        pass

                elif word == '<interface>':

                    if argv_text in listdir('/sys/class/net/'):
                        self.key_text = word
                        self.value = argv_text
                        self.exact_match = True
                        return True

                elif word == '<major>' or word == '<minor>' or word == '<number>':
                    if argv_text.isdigit():
                        self.key_text = word
                        self.value = int(argv_text)
                        self.exact_match = True
                        return True

                # For all other <foo> inputs, only do basic sanity checking
                else:
                    conflicts_with_keyword = False

                    for x in all_tokens:
                        if x.startswith(argv_text):
                            conflicts_with_keyword = True
                            break

                    if not conflicts_with_keyword:
                        self.key_text = word
                        self.value = argv_text
                        self.exact_match = True
                        return True

            # Keyword
            else:
                if argv_text == word:
                    self.key_text = word
                    self.value = True
                    self.exact_match = True
                    return True

                elif argv_text != '-' and argv_text != '--' and word.startswith(argv_text):
                    self.key_text = word
                    self.value = True
                    return True

        return False


class CommandSequence():

    def __init__(self, string):

        self.option = []
        self.score = 0

        # Remove leading and trailing whitespaces
        self.text = string.strip()

        # Compress duplicate spaces into single space
        self.text = ' '.join(self.text.split())
        tmp_tokens = self.text.split(' ')[1:]
        self.text = ' '.join(tmp_tokens)

        self.text = self.text.replace(' |', '|')
        self.text = self.text.replace('| ', '|')
        self.text = self.text.replace(' ]', ']')
        self.text = self.text.replace('[ ', '[')

        assert self.text.count('[') == self.text.count(']'), 'You have mis-matched []s in:\n  %s\n' % self.text
        assert self.text.count('(') == self.text.count(')'), 'You have mis-matched ()s in:\n  %s\n' % self.text

        # Now that we know each word is separated by a single whitespace split
        # on whitespace. Ignore the first token which is the program name.
        self.tokens = []
        for x in self.text.split(' '):

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

    def __str__(self):
        text = []
        index = 0

        for token in self.tokens:
            text.append('%d: %s' % (index, token))
            index += 1
        return self.text + '\n' +  '\n'.join(text)

    def argv_matches_tokens(self, argv):
        len_argv = len(argv)

        if len_argv > len(self.tokens):
            logging.debug("%-70s: %d argv words but we only have %d tokens. SCORE: 0" % (
                self.text, len_argv, len(self.tokens)))
            return False

        self.last_matching_token = None
        argv_index = 0

        for token in self.tokens:
            if argv_index < len_argv:
                text_argv = argv[argv_index]
            else:
                text_argv = None

            if token.required:

                if token.matches(text_argv, self.all_tokens):
                    argv_index += 1
                    self.score += 1
                    self.option = []
                    self.last_matching_token = token

                else:
                    if not argv_index:
                        self.score -= 1

                    self.option.extend(token.options())
                    logging.debug("%-70s: Required token '%s' failed to match vs. argv[%d] '%s'. SCORE: %d" % \
                            (self.text, token.text, argv_index, text_argv,
                                self.score))
                    return False

            else:
                if token.matches(text_argv, self.all_tokens):
                    argv_index += 1
                    self.score += 1
                    self.option = []
                    self.last_matching_token = token
                else:
                    self.option.extend(token.options())

        if self.score != len_argv:
            logging.debug(
                    "%-70s: %d/%d argv words matches. SCORE: %d" % (self.text,
                        self.score, len_argv, self.score))
            return False

        logging.debug("%-70s: MATCH" % (self.text))
        return True


class NetworkDocopt():
    """
    Heavily influenced by docopt but designed to be a little more like
    a Networking CLI with partial word acceptance, IPv4 sanity checking, etc
    """

    def __init__(self, docstring):
        self.args    = {}
        self.match   = False
        self.options = []
        self.program = None
        self.closest_matches = []
        self.docstring = docstring

        # Parse the 'Usage' section of the doc string.  Create a
        # CommandSequence object for every line in Usage, store those
        # objects on the self.commands list.
        state = None
        self.commands = []
        found_help_option = False

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
                if '--help' in line:
                    found_help_option = True
                self.commands.append(CommandSequence(line))

                if self.program is None:
                    result = re_search('^\s+(\S+)', line)
                    if result:
                        self.program = result.group(1)

        # Automagically add a (-h|--help) option
        if not found_help_option:
            line = '%s (-h|--help)' % self.program
            self.commands.append(CommandSequence(line))

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            for cmd in self.commands:
                logging.debug('CMD TEXT: %s' % cmd.text)
                logging.debug('CMD TOKENS')
                logging.debug(cmd)
                logging.debug('')

        # Now loop over all of the CommandSequence objects and build a list
        # of every kind of token in the doc string
        all_tokens = []
        for cmd in self.commands:
            for token in cmd.tokens:
                all_tokens += token.words
        all_tokens = set(all_tokens)

        for cmd in self.commands:
            cmd.all_tokens = all_tokens

        # The 1st item in argv is the program name...ignore it
        self.argv = sys.argv[1:]

        # Init all tokens in args to None
        for x in all_tokens:
            self.args[x] = None

        candidates = []
        for cmd in self.commands:
            if cmd.argv_matches_tokens(self.argv):
                candidates.append(cmd)

        # This is a bad thing
        if not candidates:

            logging.debug("There are no candidates")

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

                # Set the option choices to return for bash-completion
                if cmd.option:

                    # If the user entered the exact keyword then we should return the
                    # options following that keyword.
                    if not cmd.last_matching_token or cmd.last_matching_token.exact_match:
                        options_by_score[score] += cmd.option

                    # If they only entered part of the keyword ('sh' for 'show' for example)
                    # then we should return 'show' so bash can tab complete it.
                    else:
                        if cmd.last_matching_token.key_text:
                            options_by_score[score].append(cmd.last_matching_token.key_text)

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

            logging.debug("There is one candidate:\n%s"  % cmd)

            for token in cmd.tokens:

                # The key_text is only set if the token matched
                if token.key_text:
                    self.args[token.key_text] = token.value
                    logging.debug("args key: %s, value: %s" % (token.key_text,
                        token.value))

            self.match = True

            if cmd.option:
                self.options = cmd.option

            # If the user entered -h or --help print the docstring and exit
            if len(cmd.tokens) == 1:
                token = cmd.tokens[0]
                if token.key_text == '-h' or token.key_text == '--help':
                    print(self.docstring)
                    exit(0)

        else:
            print("\nERROR: ambiguous parse chain...matches:")

            for cmd in candidates:
                print("%s\n" % cmd)

    def get(self, keyword):
        return self.args.get(keyword)

    def print_options(self):
        if self.options:
            print('\n'.join(self.options))
