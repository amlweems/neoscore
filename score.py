import collections
import requests
import urlparse
import random
import re

def login(session, username, password):
    url = "http://www.neopets.com/login.phtml"
    data = {"username":username,
            "password":password}
    r = session.post(url, params=data)
    if r.status_code != 200:
        return False
    error = re.findall('<b>Error: </b>([^<]+)</div>',r.content)
    if error:
        return False
    return True

def submit(session, gameID, score):
    flashvars = fetchData(session, gameID)
    flashvars['iGameScore'] = score
    s = ScoreSubmission(session, flashvars)
    url = "http://www.neopets.com/high_scores/process_flash_score.phtml"
    data = s.ch(score)
    headers = {"Origin": "http://images.neopets.com",
               "Referer": "http://images.neopets.com/games/gaming_system/np6_include_v16.swf"}
    r = session.post(url, headers=headers, params=data, data="onData=%5Btype%20Function%5D")
    return r

def fetchData(session, gameID):
    qtof = {"g":"sFilename",
            "p":"sPreloader",
            "q":"sQuality",
            "f":"iFramerate",
            "v":"iVersion",
            "id":"iGameID",
            "n":"iNPRatio",
            "c":"iNPCap",
            "username":"sUsername",
            "age":"iAge13",
            "nsm":"iNsm",
            "nsid":"iNsid",
            "nc_referer":"sNcReferer",
            "lang":"sLang",
            "sh":"sHash",
            "sk":"sSK",
            "calibration":"iCalibration",
            "baseurl":"sBaseURL",
            "typeID":"iTypeID",
            "itemID":"iItemID",
            "sp":"iScorePosts",
            "va":"iVerifiedAct",
            "hiscore":"iHiscore",
            "destination":"sDestination",
            "chall":"iChallenge",
            "psurl":"sPSurl",
            "t":"iTracking",
            "multiple":"iMultiple",
            "member":"iIsMember",
            "isAdmin":"iIsAdmin",
            "isSponsor":"iIsSponsor",
            "ms":"iPlaysAllowed",
            "dc":"iDailyChallenge",
            "dict_ver":"iDictVersion",
            "image_host":"sImageHost",
            "include_movie":"sIncludeMovie",
            "ddNcChallenge":"iDdNcChallenge",
            "forceScore":"iForceScore"}
    url = "http://www.neopets.com/games/game.phtml?game_id={0}".format(gameID)
    r = session.get(url)
    rand = re.findall("&r=([^&]+)", r.content)[0]
    data = {"va":"",
            "game_id":gameID,
            "nc_referer":"",
            "age":1,
            "hiscore":"",
            "sp":0,
            "questionSet":"",
            "r":rand,
            "":"",
            "width":640,
            "height":500,
            "quality":"high",
            "inpage":1}
    url = "http://neopets.com/games/play_flash.phtml"
    r = session.get(url, params=data)
    u = re.findall('"gameURL":"([^"]+)"', r.content)[0]
    query = urlparse.parse_qs(urlparse.urlparse(u).query)
    flashvars = collections.defaultdict(lambda: 0)
    for k in query:
        if k in qtof:
            flashvars.update({qtof[k]:query[k][0]})
    headers = {"Origin": "http://images.neopets.com",
               "Referer": "http://www.neopets.com/games/play_flash.phtml?game_id={}".format(gameID)}
    session.get(u, headers=headers)
    headers = {"Origin": "http://images.neopets.com",
               "Referer": u}
    if 'sIncludeMovie' in flashvars:
        session.get(headers["Origin"] + "/" + flashvars['sIncludeMovie'], headers=headers)
    session.get("http://images.neopets.com/games/preloaders/ml_mystery_island.swf", headers=headers)
    session.get("http://www.neopets.com/crossdomain.xml", headers=headers)
    session.get("http://www.neopets.com/crossdomain.xml", headers=headers)
    data = {"item_id":gameID,
            "type_id":4,
            "lang":"EN",
            "randomNumber":random.randint(0, 9999999),
            "onData":"[type Function]",
            "onLoad":"[type Function]",
            "translator":"[_global.NPTranslator]"}
    session.post("http://www.neopets.com/transcontent/gettranslationxml.phtml", data=data, headers=headers)
    session.get("http://images.neopets.com/games/utilities/flash_bios/bios.swf?r={}".format(random.randint(0, 99999)), headers=headers)
    return flashvars

class ScoreSubmission:

    def __init__(self, _session, _flashvars):
        self.session = _session
        self.flashvars = _flashvars

    def ch(self, _score):
        _gameID = int(self.flashvars["iGameID"]) * 300
        _gameTime = random.randint(1000, 9000) * 10
        _urlForHashing = "ssnhsh={0}&ssnky={1}&gmd={2}&scr={3}&frmrt={4}&chllng={5}&gmdrtn={6}"
        _urlForHashing = _urlForHashing.format(self.flashvars["sHash"],
                                               self.flashvars["sSK"],
                                               self.flashvars["iGameID"],
                                               self.flashvars["iGameScore"],
                                               self.flashvars["iFramerate"],
                                               self.flashvars["iChallenge"],
                                               _gameTime)
        _crypt = Crypto()
        _crypt.initBin(self.flashvars["sHash"], self.flashvars["sSK"])
        _urlHash = _crypt.escapeURL(_urlForHashing)
        _data = {"cn":_gameID,
                 "gd":_gameTime,
                 "r":"{0:.15f}".format(random.random()),
                 "gmd_g":self.flashvars["iGameID"],
                 "mltpl_g":self.flashvars["iMultiple"],
                 "gmdt_g":_urlHash,
                 "sh_g":self.flashvars["sHash"],
                 "sk_g":self.flashvars["sSK"],
                 "usrnm_g":self.flashvars["sUsername"],
                 "dc_g":self.flashvars["iDailyChallenge"],
                 "cmgd_g":89198,
                 "ddNcChallenge":self.flashvars["iDdNcChallenge"],
                 "asp_fs_g":''}
        return _data

class Crypto:

    def __init__(self):
        self.vigenereCipher = ['$Et-*Bmy);MH:vqwdf&XU~=72PhbWp.}3rN_LZO,sonY(cFT9{a16@!keKIlQxjVJg5+iS%D^GA0?Cu4zR8',
                               '%xy1LRKsjn;6lgFA,8@{+fOM-}!DcUoav*e=(iZWQt4d$E:Yb_9kV30qB7zmP~h?)NH5CTJpI^wSr2&XG.u',
                               'F8T=sl3.vfMS?nJu^r)h%$gc{@I9kqB}_+2,o1U:Qj!HaZWKeibztEwOp*y-DP0RN(5&;4L6V~mCdYxAX7G',
                               '{8PjWUF_bsG+EtHv.O@0?i$~L,a2yNozQDh%=^eYx*dwV3B&7Zl;SM1nTI9(:6qC4pJ}fAgk)Kc!r-RuXm5',
                               '!3g@b_Gn1ENeS0xqzJDc*pU}X%)osMd-Qku{~:7RI;?fT$WhAi&m5+t69yVBa=.8FKjZYl,4wO(PLCH2rv^',
                               'oLEUbQMNpPA^J}=,u258rKZHmB(Y3q{etG$1!wDIRy;d?:j+FS.~49_fX6*kT70lxWOsg)@%-&aCihvcVnz',
                               '~loagX)8=r4{:-zWB1O(+?KEL9IS$^.Chj0TqdG2w%FeU}uypA*V&5!@Q7c,NZJ6Db;xt_PskRfmiY3HMnv',
                               'z5&=UhA)rd.;Im0bvS6?x@uZ9Gj(liR7q$NX:WaHTe{,Ok!^JyQFVscKg8nECoM+D%PY3~4L_t2w}f1-Bp*',
                               '$&,l}Gc.RDE:(BkhpIw;zHCs{56xgY!)7LjAd1%PX24VyMUbQ3rom_-9v~f8tN*^SWT?qZnieOK+ua=FJ0@',
                               'lvEbI4y+O1D8SH_fiLQY5Tk-2XW!^K.quJcnd7ja$x~om=Gp*r0:{A,CR}P@(MVtNw&hF3Z;?s%zB6)eUg9',
                               'Y$*GJwqt^ZN{:pu.v(;c2O30~aD!Vsmd1%7SiHjIe@A5glP}EMnbUWf+_&BQoCKh)RTx4-698Xzky,?Lr=F',
                               'ft2dMW~ncsZY:3-J%yhi{8j)*aQxA^!?z9bXpS+RuOFLwqk(B&P_HCrUl1},N@Em.TgoI547vDVGe0;$K=6',
                               'U;)=iw:6(uoR7!05VHC-BsyfAcSPG~3@ZmWF_tDX8}xOk1vpNET$Y?jb&*%492e.LJ,zglaMr{d+KQnh^Iq',
                               '?mF-P0Mb8,~5J(kQys$KzOL6^@2)V%w+9d}CN:n;lWjE.qH3x7RScYo!g={4teT_*iU&1GfXDBurhAIapvZ',
                               '&hlS9G(Qe?^!;%scB~4r+YFDPt$uj3Nm{:5v}861z=wAo0Ly@KROp.qM-HXZ*W,2_kUIJiECdVgxb)nfTa7',
                               'ZUu+NfclrKiRYAI;vM!O?L*et=~},)7@FQ:sPp$W5yEXbT8V(-qhmzw{J^nD2S.%j0da&xC1G_gBo6H943k',
                               'bWT?_fMev,HVmXyNSI2GR@&$Zt=O.uQ(gLErY3Ac!*jlD9kUqad~-P14%n8xsi6p7Fh{}Jz:KC;^+0o5)Bw',
                               'sy,X4O)(KS!0~{=+LbZD8edapAg%_v@:z-EuTh;xcMkVRri?F36$&tQHfl5nqIYNGj^PmUBCo.}Jw*2W719',
                               ')izKWhTc%4E-IrmJ,.MZ8+bjp;2Fwu7X{stl56S9_*D=C?0o}PQqAVBHRUNaey^!&f$kYOv3L1:dn~(g@xG',
                               'J=w%QM@4Ixt2!R&q0oBh*YakcXT6{g;K3CyZSFujfsEPUV,1vz.O-9(Li}_?Am+rN:bH5D$W7Gdp^~)l8ne']

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
            if _character in _cipherRow:
                _index = _cipherRow.index(_character)
                _index = (_index + _cipherRow.index(self.sBin[_binCount % len(self.sBin)])) % len(_cipherRow)
                _cipherText += _cipherRow[_index]
            else:
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
        for _character in _cipherText:
            try:
                _index = _cipherRow.index(_character)
                _index = (_index - _cipherRow.index(self.sBin[_binCount % len(self.sBin)])) % len(_cipherRow)
                _plainText += _cipherRow[_index]
            except:
                _plainText += _character
            _binCount += 1
        return _plainText

    def escapeString(self, s):
        _escapedString = ''.join([str(ord(_letter)).zfill(3) for _letter in s])
        return _escapedString

