class PhonStateNT:
    def __init__(self, options={}):
        self.position = 0
        self.rootconsonant = None
        self.vowel = None
        self.final = None
        self.end = None
        self.tone = None
        self.phon = ''
        self.options = options
        self.hightonechar = 'hightonechar' in options and options['hightonechar'] or '\u02CA'
        self.lowtonechar = 'lowtonechar' in options and options['lowtonechar'] or '\u02CA'
        self.eatR = 'eatR' in options and options['eatR'] or False
        self.eatL = 'eatL' in options and options['eatL'] or False
        self.eatP = 'eatP' in options and options['eatP'] or False
        self.aspirateLowTones = 'aspirateLowTones' in options and options['aspirateLowTones'] or False
  
    def getFinal(endstr):
        """ returns the final consonant or '' """
        if not endstr:
            return ''
        simplesuffixes = "mpn'krl"
        lastchar = endstr[-1]
        if lastchar == 'g':
            return 'ng'
        elif lastchar in simplesuffixes:
            return lastchar
        return ''

    #TODO: remove aspiration on low tones
    simpleRootMapping = {
        'sh': 'ɕ', #p. 440
        'rh': 'ʂ', #p. 440
        's': 's', #p. 440
        'r': 'r', #p. 441
        'l': 'l', #p. 441
        'lh': 'l̥ʰ', #p. 441
        'h': 'h', #p. 441
        'm': 'm', #p. 441
        'n': 'n', #p. 442
        'ny': 'ɲ', #p. 442
        'ng': 'ŋ', #p. 442
        'w': 'w', #p. 443
        'y': 'j' #p. 443
    }

    simpleVowMapping = {
        'ä': 'ɛ', #p. 443
        'ö': 'ø', #p. 444
        'u': 'u', #p. 444
        'ü': 'y', #p. 444
        'i': 'i' #p. 444
    }

    simpleFinalMapping = {
        "'": 'ʔ', #p. 435
        ":": 'ː', #p. 435
        'm': 'm', #p. 444
        'ng': 'ŋ' #p. 442
    }

    def getNextRootCommonPattern(position, tone, lastcondition, phon1, phon2, phon3):
        """ this corresponds to the most common pattern for roots: phon1 at the beginning
            of high-toned words, phon2 at the beginning of low-tones words, phon1 after
            some consonnants (if lastcondition is met), and phon3 otherwise"""
        if position == 1:
            return tone == '+' and phon1 or phon2
        return lastcondition and phon1 or phon3

    def getNextRootPhon(self, nrc): # nrc: nextrootconsonant
        # self.tone is the first tone (can be associated with current syllable)
        # self.position is the position of the syllable we're adding
        # self.final is the previous final consonnant (if any)
        if nrc.startswith('~'):
            # TODO: Do some magic here?
            nrc = nrc[1:]
        possibleAspirate = True
        if self.tone == '-' and not self.aspirateLowTones:
            possibleAspirate = False
        if nrc in PhonStateNT.simpleRootMapping:
            return PhonStateNT.simpleRootMapping[nrc]
        if nrc == '':
            return ''
        if nrc == 'kh':
            return possibleAspirate and 'kʰ' or 'k' #p. 435
        if nrc == 'khy':
            return possibleAspirate and 'cʰ' or 'c' #p. 436
        if nrc == 'thr':
            return possibleAspirate and 'ʈʰ' or 'ʈ' #p. 436
        if nrc == 'th':
            return possibleAspirate and 'tʰ' or 't' #p. 437
        if nrc == 'ph':
            return possibleAspirate and 'pʰ' or 'p' #p. 438
        if nrc == 'ch':
            return possibleAspirate and 'tɕʰ' or 'tɕ' #p. 439
        if nrc == 'tsh':
            return possibleAspirate and 'tsʰ' or 'ts' #p. 439
        if nrc == 'k':
            lastcond = (self.final == 'p')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 'k', 'g', 'g̥')
        if nrc == 'ky':
            lastcond = (self.final == 'p')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 'c', 'ɟ', 'ɟ̥')
        if nrc == 'tr':
            lastcond = (self.final == 'p' or self.final == 'k')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 'ʈ', 'ɖ', 'ɖ̥')
        if nrc == 't':
            lastcond = (self.final == 'p' or self.final == 'k')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 't', 'd', 'd̥')
        if nrc == 'p':
            lastcond = (self.final == 'k')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 'p', 'b', 'b̥')
        if nrc == 'c':
            lastcond = (self.final == 'p' or self.final == 'k')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 'tɕ', 'dʑ', 'ɖ̥ʑ')
        if nrc == 'ts':
            lastcond = (self.final == 'p' or self.final == 'k')
            return PhonStateNT.getNextRootCommonPattern(self.position, self.tone, lastcond, 'ts', 'dz', 'dz̥')
        print("unknown root consonant: "+nrc)
        return nrc

    def doCombineCurEnd(self, endofword, nrc='', nextvowel=''): # nrc = next root consonant
        """ combined the self.end into the self.phon """
        if not self.end:
            return
        slashi = self.end.find('/')
        if slashi != -1:
            self.end = self.end[:slashi]
        self.vowel = self.end[:1]
        # do something about final ~ ?
        if self.end.endswith('~'):
            self.end = self.end[:-1]
        self.final = PhonStateNT.getFinal(self.end)
        ## vowels:
        vowelPhon = ''
        if self.vowel in PhonStateNT.simpleVowMapping:
            vowelPhon = PhonStateNT.simpleVowMapping[self.vowel]
        elif self.vowel == 'a':
            if self.position == 1 and self.final != 'p':
                vowelPhon = 'a'
            else:
                vowelPhon = 'ə'
        elif self.vowel == 'e':
            if self.final != '':
                vowelPhon = 'ɛ'
            else:
                vowelPhon = 'e'
        elif self.vowel == 'o':
            if self.final != '':
                vowelPhon = 'ɔ'
            else:
                vowelPhon = 'o'
        else:
            print("unknown vowel: "+self.vowel)
        # add w at beginning of low tone words:
        if self.position == 1 and self.vowel in "öou" and self.phon == '':
            self.phon += 'w'
        self.phon += vowelPhon
        if self.position == 1:
            self.phon += self.tone == '+' and self.hightonechar or self.lowtonechar
        # TODO: option for r and l, replace : with ː
        finalPhon = ''
        if self.final in PhonStateNT.simpleFinalMapping:
            vowelPhon = PhonStateNT.simpleFinalMapping[self.final]
        elif self.final == 'k':
            if not endofword: # p. 433
                if nrc in ['p', 't', 'tr', 'ts', 'c', 's']:
                    finalPhon = 'k'
                elif self.vowel in ['i', 'e'] and nrc in ['l', 'sh']:
                    finalPhon = 'k'
                elif nrc in ['r', 'l']:
                    finalPhon = 'g̥'
                elif self.vowel not in ['e', 'i'] and nrc in ['l', 'sh', 'm', 'ny', 'n', 'ng']:
                    finalPhon = 'ɣ'
                elif nrc in ['k', 'ky', 'w', 'y']:
                    finalPhon = ''
                elif self.vowel in ['e', 'i'] and nrc in ['m', 'ny', 'n', 'ng']:
                    finalPhon = 'ŋ'
                else:
                    print("unhandled case, this shouldn't happen")
            else:
                finalPhon = 'ʔ'
        elif self.final == 'p':
            if not endofword:
                if nrc in ['p', 't', 'tr', 'ts', 'c', 's', 'sh']:
                    finalPhon = 'p'
                else:
                    finalPhon = self.eatP and '' or 'b̥'
            else:
                finalPhon = self.eatP and 'ʔ' or 'b̥' # TODO: check
        elif self.final == 'n':
            if not endofword:
                if nrc in ['t', 'tr']:
                    finalPhon = 'n'
                elif nrc == 'p':
                    finalPhon = 'm'
                elif nrc == 'k':
                    finalPhon = 'ŋ'
                elif nrc == 'ky':
                    finalPhon = 'ɲ'
                else:
                    finalPhon = '' # TODO: or 'n'?
            else:
                finalPhon = '' # TODO: or '~'?
        elif self.final == 'r':
            finalPhon = self.eatR and 'ː' or 'r'
        elif self.final == 'l':
            finalPhon = self.eatL and 'ː' or 'l'
        elif self.final == '':
            finalPhon = ''
        else:
            print("unrecognized final: "+self.final)
        self.phon += finalPhon

    def combineWithException(self, exception):
        syllables = exception.split('|')
        for syl in syllables:
            indexplusminus = syl.find('+')
            if indexplusminus == -1:
                indexplusminus = syl.find('-')
            if indexplusminus == -1:
                print("invalid exception syllable: "+syl)
                continue
            self.combineWith(syl[:indexplusminus+1], syl[indexplusminus+1:])

    def combineWith(self, nextroot, nextend):
        self.position += 1
        slashi = nextroot.find('/')
        if slashi != -1:
            if self.position > 1:
                nextroot = nextroot[slashi+1:]
            else:
                nextroot = nextroot[:slashi]
        if self.position == 1:
            self.tone = nextroot[-1]
        nextrootconsonant = nextroot[:-1]
        nextvowel = ''
        self.doCombineCurEnd(False, nextrootconsonant, nextvowel)
        nextrootphon = self.getNextRootPhon(nextrootconsonant)
        self.phon += nextrootphon
        self.end = nextend
    
    def finish(self):
        self.doCombineCurEnd(True)

if __name__ == '__main__':
    """ Example use """
    s = PhonStateNT()
    s.combineWith("k+", "ak")
    s.finish()
    print(s.phon)
