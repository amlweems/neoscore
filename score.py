import random
import urllib2
import re

def submit(user, score, gameID):
    sHash, sSK, rand = fetchData(gameID)
    s = ScoreSubmission(gameID, sHash, sSK, user)
    url = s.ch(score)
    print url

def fetchData(gameID):
    url = "http://neopets.com/games/play_flash.phtml?va=&game_id={0}&nc_referer=&age=1&sp=2&questionSet=&r={1}"
    url = url.format(gameID, random.randint(0,9999999))
    u = urllib2.urlopen(url)
    data = u.read()
    sh = re.findall("&sh=([^&]+)",data)
    sk = re.findall("&sk=([^&]+)",data)
    return sh[0],sk[0]

class ScoreSubmission:

    def __init__(self, _gameID, _sHash, _sSK, _user):
        self.gameID = _gameID
        self.sHash = _sHash
        self.sSK = _sSK
        self.username = _user
        self.framerate = 24
        self.challenge = 0
        self.multiple = 0
        self.dailychallenge = 0

    def ch(self, _score):
        _gameID = self.gameID * 300
        _gameTime = random.randint(1000, 9000) * 10
        _url = "http://www.neopets.com/high_scores/process_flash_score.phtml"
        _url += "?cn={0}&gd={1}&r={2}".format(_gameID, _gameTime, random.random())
        _crypt = Crypto()
        _crypt.initBin(self.sHash, self.sSK)
        _urlForHashing = "ssnhsh={0}&ssnky={1}&gmd={2}&scr={3}&frmrt={4}&chllng={5}&gmdrtn={6}"
        _urlForHashing = _urlForHashing.format(self.sHash, self.sSK, self.gameID, _score, self.framerate, self.challenge, _gameTime)
        _urlHash = _crypt.escapeURL(_urlForHashing)
        _url += "&gmd_g={0}&mltpl_g={1}&gmdt_g={2}&sh_g={3}&sk_g={4}&usrnm_g={5}&dc_g={6}"
        _url = _url.format(self.gameID, self.multiple, _urlHash, self.sHash, self.sSK, self.username, self.dailychallenge)
        return _url

class Crypto:

    def __init__(self):
        self.vigenereCipher = ['*KS5fJ(+,=FO$V^elCjpLbE_@Q;~-9G}8ziBUg1c)mHkyPWd0AxnX72IMqY4owN?v!t.6uD{sh%a&TR:Zr3',
                               'N;zqeE2Ps70lV8jD-!5ZgxB6Kfv@Wc=y)XdQbLM*CIwko?t&Rr.%_TJFO^i4{UAn+a~1,ShGH$}3(u9:pYm',
                               '2IMHqbD=GX+i&5*Q4oVy.JYs;pT:f)uxL{gkU9vCnmcr7BZ@FWNd_}wK,3ShAeEOzaP!%6l80j-R(~?1t^$',
                               'ma63v+Qh9qJ5dS*fgt0RuH$sGw);W_z4l-bIVBoN~PE{(Fx&y@:8%pnTk2Ze}!Y17cCKrUijO=^AM?,.XDL',
                               'CwB%_Pi@,?(1mkgx7nqa*cpUDjs2;GlLZKe^z+4=Itdv}XH6bNSVr0Q5WM$:ho{FOfJYu)ETR~y938!.-A&',
                               'wg0a%ZPSJ;U_$e1-mvp:qcxRln~KTXE4(?usOH@k={jW*5YBo3N26CQt&97IGbD.AfzMydr^,VhL)Fi+8!}',
                               '%jOuNck,em(QVzH-nDr8!bG?ofhKYd}As25BR$J&wTp~iF0U*9^;Lv+.PW:_IlXg{Za)q@CE6S=t4137Mxy',
                               '5grI;v:Z0@Jnfo.?l{~zHS$d%pYqF2)&Ue7s!(jT}Lu*1MQ+A,V8CymDP^9a_wxhiGWKRXcOtE46Bk=bN3-',
                               'E!H@.wLp;XNWaOY(~z=6_B^P}ju0$J{3Gg8yk,&nAoVTI5c+UMDdx)SQ:2*CRe4tK1r%?s7hb9fZqi-lmFv',
                               'Dg+qPTL,?-GH;{jK8Vi)~x%o6af2:^uCIBJNwscAUZ(YkreM@9vER1nX$zb_yOmQ3&4lWFdS50!=h*p.7t}',
                               '.eHl6:mkpx=QKV+~UM3C)ZoEYi&5F}^;I_1LRnAgJ?0h8q{D9,$WPzjO%fBXu(cv!aG7wdb@yt42S-rNT*s',
                               '9{n%A&*3aELb,cqRBwZS1pUJ(~ojzIH$T.d=084K_YDg^it:Nu!sxmQhr-CWl6}+OkMfy;VG72e?5v)P@XF',
                               '(+{}am~80qkyIfv^!jY2.XC?pK@3r_hD:dJHFouW%N7Gi6Q;V),91EtPbnwRLez*UO-Mg=SlAxZs5B4T$&c',
                               'CFH@KIY_0M%sW5JxnSTye!tPhb-Zw;}*&:~D^kV{lv.X3$umaAp6UR+fiOQc2q=(dL9?8B74EG,oz1)jNrg',
                               '3(SWi^OE.re?yg%AksLX5wm94GT})q62=b;7v-8*{Uj&dN$t,RBaKVz~!0CcZ1H@lMfPp_uxJYQ:FnhI+Do',
                               'cWr@MNsSo0HKIyp8i^L$*AU-tJ=6gTYC9+PVquxw_Q7E}!km):FZj4vaf3O%e5h(Rz~XnGBbld1?,.D2;{&',
                               'wgOerQ45273j%oDu0I*:MATVGXhSi^sJ1pCLv_$&B.8d~!(mR{EUz,;c=-?kP)fYtqn9WbyFa6l@x+HN}KZ',
                               'vQEGgAZ+@^o4=BtS6;f.d($Dr0OmTPNUzVeY_)pj~JMcH%2!&kIl3,n8W9:7*X1s}Kah{5-Fqu?bLxRCwiy',
                               ',W%94xR$}sFi;V^o.uc*TD&fmy07zN)pke-:BJMt3wI~8@EQLj=nU!5v_r{ZA(6qla2hHbgXO+C?Yd1KSPG',
                               '1jI8F;w-s&@QVarBfybCNJh6Pn4R%^DuTx?9iH=2U3G7.YO)e,$EWLZ{}tp(lSck50A:v+oz~g!_dXMqK*m']

    def initBin(self, sh, sk):
        self.sBin = sh + sk

    def escapeURL(self, s):
        _local1 = self.string2Hex(s)
        _local2 = self.escapeString(_local1)
        return _local2

    def string2Hex(self, s):
        _cipherText = ""
        _randomIndex = random.randrange(0, len(self.vigenereCipher))
        _cipherRow = self.vigenereCipher[_randomIndex]
        _binCount = 0
        for _character in s:
            try:
                _index = _cipherRow.index(_character)
                _index = (_index + _cipherRow.index(self.sBin[_binCount % len(self.sBin)])) % len(_cipherRow)
                _cipherText += _cipherRow[_index]
            except:
                _cipherText += _character
            _binCount += 1
        _cipherText += str(_randomIndex).zfill(2)
        return _cipherText

    def hex2String(self, s):
        _plainText = ""
        _cipherText = ""
        for i in range(0,len(s),3):
            _cipherText += chr(int(s[i:i+3]))
        _randomIndex = int(_cipherText[-2:])
        _cipherRow = self.vigenereCipher[_randomIndex]
        _cipherText = _cipherText[:-2]
        _binCount = 0
        for _character in s:
            try:
                _index = _cipherRow.index(_character)
                _index = (_index + _cipherRow.index(self.sBin[_binCount % len(self.sBin)])) % len(_cipherRow)
                _plainText += _cipherRow[_index]
            except:
                _plainText += _character
            _binCount += 1
        return _plainText

    def escapeString(self, s):
        _escapedString = ''.join([str(ord(_letter)).zfill(3) for _letter in s])
        return _escapedString

