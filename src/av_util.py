import datetime as dt
from enum import StrEnum
from typing import TypedDict


def obfuscate_api_key(api_key: str) -> str:
    if api_key == "demo":  # Don't have to obfuscate demo account
        return api_key

    return api_key[:2] + "..." + api_key[-2:]


def obfuscate_request_url(request_url: str, api_key: str) -> str:
    first_part = request_url.split("&apikey=")[0]
    return first_part + f"&apikey={obfuscate_api_key(api_key)}"


def get_utc_timestamp_ms() -> int:
    return int(dt.datetime.now(tz=dt.timezone.utc).timestamp() * 1000)


class AV_DATA_CANDLE(TypedDict, total=False):
    __annotations__ = {
        "1. open": str,
        "2. high": str,
        "3. low": str,
        "4. close": str,
        "5. volume": str,
    }


class AV_SYMBOL(StrEnum):
    AAPL = "AAPL"
    IBM = "IBM"
    TSCO_LON = "TSCO.LON"
    SHOP_TRT = "SHOP.TRT"
    GPV_TRV = "GPV.TRV"
    MBG_DEX = "MBG.DEX"
    RELIANCE_BSE = "RELIANCE.BSE"
    _600104_SHH = "600104.SHH"
    _000002_SHZ = "000002.SHZ"


class AV_CANDLE_TF(StrEnum):
    MIN = "1min"
    MIN5 = "5min"
    MIN15 = "15min"
    MIN30 = "30min"
    HOUR = "60min"
    DAY = "1day"
    WEEKLY = "1week"
    MONTHLY = "1month"


class AV_CURRENCY(StrEnum):  # As of 2024-11-29
    AED = "AED"
    AFN = "AFN"
    ALL = "ALL"
    AMD = "AMD"
    ANG = "ANG"
    AOA = "AOA"
    ARS = "ARS"
    AUD = "AUD"
    AWG = "AWG"
    AZN = "AZN"
    BAM = "BAM"
    BBD = "BBD"
    BDT = "BDT"
    BGN = "BGN"
    BHD = "BHD"
    BIF = "BIF"
    BMD = "BMD"
    BND = "BND"
    BOB = "BOB"
    BRL = "BRL"
    BSD = "BSD"
    BTN = "BTN"
    BWP = "BWP"
    BZD = "BZD"
    CAD = "CAD"
    CDF = "CDF"
    CHF = "CHF"
    CLF = "CLF"
    CLP = "CLP"
    CNH = "CNH"
    CNY = "CNY"
    COP = "COP"
    CUP = "CUP"
    CVE = "CVE"
    CZK = "CZK"
    DJF = "DJF"
    DKK = "DKK"
    DOP = "DOP"
    DZD = "DZD"
    EGP = "EGP"
    ERN = "ERN"
    ETB = "ETB"
    EUR = "EUR"
    FJD = "FJD"
    FKP = "FKP"
    GBP = "GBP"
    GEL = "GEL"
    GHS = "GHS"
    GIP = "GIP"
    GMD = "GMD"
    GNF = "GNF"
    GTQ = "GTQ"
    GYD = "GYD"
    HKD = "HKD"
    HNL = "HNL"
    HRK = "HRK"
    HTG = "HTG"
    HUF = "HUF"
    ICP = "ICP"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    IQD = "IQD"
    IRR = "IRR"
    ISK = "ISK"
    JEP = "JEP"
    JMD = "JMD"
    JOD = "JOD"
    JPY = "JPY"
    KES = "KES"
    KGS = "KGS"
    KHR = "KHR"
    KMF = "KMF"
    KPW = "KPW"
    KRW = "KRW"
    KWD = "KWD"
    KYD = "KYD"
    KZT = "KZT"
    LAK = "LAK"
    LBP = "LBP"
    LKR = "LKR"
    LRD = "LRD"
    LSL = "LSL"
    LYD = "LYD"
    MAD = "MAD"
    MDL = "MDL"
    MGA = "MGA"
    MKD = "MKD"
    MMK = "MMK"
    MNT = "MNT"
    MOP = "MOP"
    MRO = "MRO"
    MRU = "MRU"
    MUR = "MUR"
    MVR = "MVR"
    MWK = "MWK"
    MXN = "MXN"
    MYR = "MYR"
    MZN = "MZN"
    NAD = "NAD"
    NGN = "NGN"
    NOK = "NOK"
    NPR = "NPR"
    NZD = "NZD"
    OMR = "OMR"
    PAB = "PAB"
    PEN = "PEN"
    PGK = "PGK"
    PHP = "PHP"
    PKR = "PKR"
    PLN = "PLN"
    PYG = "PYG"
    QAR = "QAR"
    RON = "RON"
    RSD = "RSD"
    RUB = "RUB"
    RUR = "RUR"
    RWF = "RWF"
    SAR = "SAR"
    SBDF = "SBDf"
    SCR = "SCR"
    SDG = "SDG"
    SDR = "SDR"
    SEK = "SEK"
    SGD = "SGD"
    SHP = "SHP"
    SLL = "SLL"
    SOS = "SOS"
    SRD = "SRD"
    SYP = "SYP"
    SZL = "SZL"
    THB = "THB"
    TJS = "TJS"
    TMT = "TMT"
    TND = "TND"
    TOP = "TOP"
    TRY = "TRY"
    TTD = "TTD"
    TWD = "TWD"
    TZS = "TZS"
    UAH = "UAH"
    UGX = "UGX"
    USD = "USD"
    UYU = "UYU"
    UZS = "UZS"
    VND = "VND"
    VUV = "VUV"
    WST = "WST"
    XAF = "XAF"
    XCD = "XCD"
    XDR = "XDR"
    XOF = "XOF"
    XPF = "XPF"
    YER = "YER"
    ZAR = "ZAR"
    ZMW = "ZMW"
    ZWL = "ZWL"


class AV_CURRENCY_DIGITAL(StrEnum):  # As of 2024-11-29
    _1ST = "1ST"
    _2GIVE = "2GIVE"
    _808 = "808"
    AAVE = "AAVE"
    ABT = "ABT"
    ABY = "ABY"
    AC = "AC"
    ACT = "ACT"
    ADA = "ADA"
    ADT = "ADT"
    ADX = "ADX"
    AE = "AE"
    AEON = "AEON"
    AGI = "AGI"
    AGRS = "AGRS"
    AI = "AI"
    AID = "AID"
    AION = "AION"
    AIR = "AIR"
    AKY = "AKY"
    ALGO = "ALGO"
    ALIS = "ALIS"
    AMBER = "AMBER"
    AMP = "AMP"
    AMPL = "AMPL"
    ANC = "ANC"
    ANT = "ANT"
    APPC = "APPC"
    APX = "APX"
    ARDR = "ARDR"
    ARK = "ARK"
    ARN = "ARN"
    AST = "AST"
    ATB = "ATB"
    ATM = "ATM"
    ATOM = "ATOM"
    ATS = "ATS"
    AUR = "AUR"
    AVAX = "AVAX"
    AVT = "AVT"
    B3 = "B3"
    BAND = "BAND"
    BAT = "BAT"
    BAY = "BAY"
    BBR = "BBR"
    BCAP = "BCAP"
    BCC = "BCC"
    BCD = "BCD"
    BCH = "BCH"
    BCN = "BCN"
    BCPT = "BCPT"
    BCX = "BCX"
    BCY = "BCY"
    BDL = "BDL"
    BEE = "BEE"
    BELA = "BELA"
    BET = "BET"
    BFT = "BFT"
    BIS = "BIS"
    BITB = "BITB"
    BITBTC = "BITBTC"
    BITCNY = "BITCNY"
    BITEUR = "BITEUR"
    BITGOLD = "BITGOLD"
    BITSILVER = "BITSILVER"
    BITUSD = "BITUSD"
    BIX = "BIX"
    BLITZ = "BLITZ"
    BLK = "BLK"
    BLN = "BLN"
    BLOCK = "BLOCK"
    BLZ = "BLZ"
    BMC = "BMC"
    BNB = "BNB"
    BNT = "BNT"
    BNTY = "BNTY"
    BOST = "BOST"
    BOT = "BOT"
    BQ = "BQ"
    BRD = "BRD"
    BRK = "BRK"
    BRX = "BRX"
    BSV = "BSV"
    BTA = "BTA"
    BTC = "BTC"
    BTCB = "BTCB"
    BTCD = "BTCD"
    BTCP = "BTCP"
    BTG = "BTG"
    BTM = "BTM"
    BTS = "BTS"
    BTSR = "BTSR"
    BTT = "BTT"
    BTX = "BTX"
    BURST = "BURST"
    BUSD = "BUSD"
    BUZZ = "BUZZ"
    BYC = "BYC"
    BYTOM = "BYTOM"
    C20 = "C20"
    CAKE = "CAKE"
    CANN = "CANN"
    CAT = "CAT"
    CCRB = "CCRB"
    CDT = "CDT"
    CFI = "CFI"
    CHAT = "CHAT"
    CHIPS = "CHIPS"
    CLAM = "CLAM"
    CLOAK = "CLOAK"
    CMP = "CMP"
    CMT = "CMT"
    CND = "CND"
    CNX = "CNX"
    COFI = "COFI"
    COMP = "COMP"
    COSS = "COSS"
    COVAL = "COVAL"
    CRBIT = "CRBIT"
    CREA = "CREA"
    CREDO = "CREDO"
    CRO = "CRO"
    CRW = "CRW"
    CSNO = "CSNO"
    CTR = "CTR"
    CTXC = "CTXC"
    CURE = "CURE"
    CVC = "CVC"
    DAI = "DAI"
    DAR = "DAR"
    DASH = "DASH"
    DATA = "DATA"
    DAY = "DAY"
    DBC = "DBC"
    DBIX = "DBIX"
    DCN = "DCN"
    DCR = "DCR"
    DCT = "DCT"
    DDF = "DDF"
    DENT = "DENT"
    DFS = "DFS"
    DGB = "DGB"
    DGC = "DGC"
    DGD = "DGD"
    DICE = "DICE"
    DLT = "DLT"
    DMD = "DMD"
    DMT = "DMT"
    DNT = "DNT"
    DOGE = "DOGE"
    DOPE = "DOPE"
    DOT = "DOT"
    DRGN = "DRGN"
    DTA = "DTA"
    DTB = "DTB"
    DYN = "DYN"
    EAC = "EAC"
    EBST = "EBST"
    EBTC = "EBTC"
    ECC = "ECC"
    ECN = "ECN"
    EDG = "EDG"
    EDO = "EDO"
    EFL = "EFL"
    EGC = "EGC"
    EGLD = "EGLD"
    EKT = "EKT"
    ELA = "ELA"
    ELEC = "ELEC"
    ELF = "ELF"
    ELIX = "ELIX"
    EMB = "EMB"
    EMC = "EMC"
    EMC2 = "EMC2"
    ENG = "ENG"
    ENJ = "ENJ"
    ENRG = "ENRG"
    EOS = "EOS"
    EOT = "EOT"
    EQT = "EQT"
    ERC = "ERC"
    ETC = "ETC"
    ETH = "ETH"
    ETHD = "ETHD"
    ETHOS = "ETHOS"
    ETN = "ETN"
    ETP = "ETP"
    ETT = "ETT"
    EVE = "EVE"
    EVX = "EVX"
    EXCL = "EXCL"
    EXP = "EXP"
    FCT = "FCT"
    FIL = "FIL"
    FLDC = "FLDC"
    FLO = "FLO"
    FLT = "FLT"
    FRST = "FRST"
    FTC = "FTC"
    FTT = "FTT"
    FUEL = "FUEL"
    FUN = "FUN"
    GAM = "GAM"
    GAME = "GAME"
    GAS = "GAS"
    GBG = "GBG"
    GBX = "GBX"
    GBYTE = "GBYTE"
    GCR = "GCR"
    GEO = "GEO"
    GLD = "GLD"
    GNO = "GNO"
    GNT = "GNT"
    GOLOS = "GOLOS"
    GRC = "GRC"
    GRT = "GRT"
    GRS = "GRS"
    GRWI = "GRWI"
    GTC = "GTC"
    GTO = "GTO"
    GUP = "GUP"
    GVT = "GVT"
    GXS = "GXS"
    HBAR = "HBAR"
    HBN = "HBN"
    HEAT = "HEAT"
    HMQ = "HMQ"
    HPB = "HPB"
    HSR = "HSR"
    HT = "HT"
    HUSH = "HUSH"
    HVN = "HVN"
    HXX = "HXX"
    ICN = "ICN"
    ICX = "ICX"
    IFC = "IFC"
    IFT = "IFT"
    IGNIS = "IGNIS"
    INCNT = "INCNT"
    IND = "IND"
    INF = "INF"
    INK = "INK"
    INS = "INS"
    INSTAR = "INSTAR"
    INT = "INT"
    INXT = "INXT"
    IOC = "IOC"
    ION = "ION"
    IOP = "IOP"
    IOST = "IOST"
    IOTA = "IOTA"
    IOTX = "IOTX"
    IQT = "IQT"
    ITC = "ITC"
    IXC = "IXC"
    IXT = "IXT"
    J8T = "J8T"
    JNT = "JNT"
    KCS = "KCS"
    KICK = "KICK"
    KIN = "KIN"
    KLAY = "KLAY"
    KMD = "KMD"
    KNC = "KNC"
    KORE = "KORE"
    KSM = "KSM"
    LBC = "LBC"
    LCC = "LCC"
    LEND = "LEND"
    LEO = "LEO"
    LEV = "LEV"
    LGD = "LGD"
    LINDA = "LINDA"
    LINK = "LINK"
    LKK = "LKK"
    LMC = "LMC"
    LOCI = "LOCI"
    LOOM = "LOOM"
    LRC = "LRC"
    LSK = "LSK"
    LTC = "LTC"
    LUN = "LUN"
    LUNA = "LUNA"
    MAID = "MAID"
    MANA = "MANA"
    MATIC = "MATIC"
    MAX = "MAX"
    MBRS = "MBRS"
    MCAP = "MCAP"
    MCO = "MCO"
    MDA = "MDA"
    MEC = "MEC"
    MED = "MED"
    MEME = "MEME"
    MER = "MER"
    MGC = "MGC"
    MGO = "MGO"
    MINEX = "MINEX"
    MINT = "MINT"
    MIOTA = "MIOTA"
    MITH = "MITH"
    MKR = "MKR"
    MLN = "MLN"
    MNE = "MNE"
    MNX = "MNX"
    MOD = "MOD"
    MONA = "MONA"
    MRT = "MRT"
    MSP = "MSP"
    MTH = "MTH"
    MTN = "MTN"
    MUE = "MUE"
    MUSIC = "MUSIC"
    MYB = "MYB"
    MYST = "MYST"
    MZC = "MZC"
    NAMO = "NAMO"
    NANO = "NANO"
    NAS = "NAS"
    NAV = "NAV"
    NBT = "NBT"
    NCASH = "NCASH"
    NDC = "NDC"
    NEBL = "NEBL"
    NEO = "NEO"
    NEOS = "NEOS"
    NET = "NET"
    NLC2 = "NLC2"
    NLG = "NLG"
    NMC = "NMC"
    NMR = "NMR"
    NOBL = "NOBL"
    NOTE = "NOTE"
    NPXS = "NPXS"
    NSR = "NSR"
    NTO = "NTO"
    NULS = "NULS"
    NVC = "NVC"
    NXC = "NXC"
    NXS = "NXS"
    NXT = "NXT"
    OAX = "OAX"
    OBITS = "OBITS"
    OCL = "OCL"
    OCN = "OCN"
    ODEM = "ODEM"
    ODN = "ODN"
    OF = "OF"
    OK = "OK"
    OMG = "OMG"
    OMNI = "OMNI"
    ONION = "ONION"
    ONT = "ONT"
    OPT = "OPT"
    ORN = "ORN"
    OST = "OST"
    PART = "PART"
    PASC = "PASC"
    PAY = "PAY"
    PBL = "PBL"
    PBT = "PBT"
    PFR = "PFR"
    PING = "PING"
    PINK = "PINK"
    PIVX = "PIVX"
    PIX = "PIX"
    PLBT = "PLBT"
    PLR = "PLR"
    PLU = "PLU"
    POA = "POA"
    POE = "POE"
    POLY = "POLY"
    POSW = "POSW"
    POT = "POT"
    POWR = "POWR"
    PPC = "PPC"
    PPT = "PPT"
    PPY = "PPY"
    PRG = "PRG"
    PRL = "PRL"
    PRO = "PRO"
    PST = "PST"
    PTC = "PTC"
    PTOY = "PTOY"
    PURA = "PURA"
    QASH = "QASH"
    QAU = "QAU"
    QLC = "QLC"
    QRK = "QRK"
    QRL = "QRL"
    QSP = "QSP"
    QTL = "QTL"
    QTUM = "QTUM"
    QUICK = "QUICK"
    QWARK = "QWARK"
    R = "R"
    RADS = "RADS"
    RAIN = "RAIN"
    RBIES = "RBIES"
    RBX = "RBX"
    RBY = "RBY"
    RCN = "RCN"
    RDD = "RDD"
    RDN = "RDN"
    REC = "REC"
    RED = "RED"
    REP = "REP"
    REQ = "REQ"
    RHOC = "RHOC"
    RIC = "RIC"
    RISE = "RISE"
    RLC = "RLC"
    RLT = "RLT"
    RPX = "RPX"
    RRT = "RRT"
    RUFF = "RUFF"
    RUNE = "RUNE"
    RUP = "RUP"
    RVT = "RVT"
    SAFEX = "SAFEX"
    SALT = "SALT"
    SAN = "SAN"
    SBD = "SBD"
    SBTC = "SBTC"
    SC = "SC"
    SEELE = "SEELE"
    SEQ = "SEQ"
    SHIB = "SHIB"
    SHIFT = "SHIFT"
    SIB = "SIB"
    SIGMA = "SIGMA"
    SIGT = "SIGT"
    SJCX = "SJCX"
    SKIN = "SKIN"
    SKY = "SKY"
    SLR = "SLR"
    SLS = "SLS"
    SMART = "SMART"
    SMT = "SMT"
    SNC = "SNC"
    SNGLS = "SNGLS"
    SNM = "SNM"
    SNRG = "SNRG"
    SNT = "SNT"
    SOC = "SOC"
    SOL = "SOL"
    SOUL = "SOUL"
    SPANK = "SPANK"
    SPC = "SPC"
    SPHR = "SPHR"
    SPR = "SPR"
    SNX = "SNX"
    SRN = "SRN"
    START = "START"
    STEEM = "STEEM"
    STK = "STK"
    STORJ = "STORJ"
    STORM = "STORM"
    STQ = "STQ"
    STRAT = "STRAT"
    STX = "STX"
    SUB = "SUB"
    SWFTC = "SWFTC"
    SWIFT = "SWIFT"
    SWT = "SWT"
    SYNX = "SYNX"
    SYS = "SYS"
    TAAS = "TAAS"
    TAU = "TAU"
    TCC = "TCC"
    TFL = "TFL"
    THC = "THC"
    THETA = "THETA"
    TIME = "TIME"
    TIX = "TIX"
    TKN = "TKN"
    TKR = "TKR"
    TKS = "TKS"
    TNB = "TNB"
    TNT = "TNT"
    TOA = "TOA"
    TRAC = "TRAC"
    TRC = "TRC"
    TRCT = "TRCT"
    TRIBE = "TRIBE"
    TRIG = "TRIG"
    TRST = "TRST"
    TRUE = "TRUE"
    TRUST = "TRUST"
    TRX = "TRX"
    TUSD = "TUSD"
    TX = "TX"
    UBQ = "UBQ"
    UKG = "UKG"
    ULA = "ULA"
    UNB = "UNB"
    UNI = "UNI"
    UNITY = "UNITY"
    UNO = "UNO"
    UNY = "UNY"
    UP = "UP"
    URO = "URO"
    USDT = "USDT"
    UST = "UST"
    UTK = "UTK"
    VEE = "VEE"
    VEN = "VEN"
    VERI = "VERI"
    VET = "VET"
    VIA = "VIA"
    VIB = "VIB"
    VIBE = "VIBE"
    VIVO = "VIVO"
    VOISE = "VOISE"
    VOX = "VOX"
    VPN = "VPN"
    VRC = "VRC"
    VRM = "VRM"
    VRS = "VRS"
    VSL = "VSL"
    VTC = "VTC"
    VTR = "VTR"
    WABI = "WABI"
    WAN = "WAN"
    WAVES = "WAVES"
    WAX = "WAX"
    WBTC = "WBTC"
    WCT = "WCT"
    WDC = "WDC"
    WGO = "WGO"
    WGR = "WGR"
    WINGS = "WINGS"
    WPR = "WPR"
    WTC = "WTC"
    WTT = "WTT"
    XAS = "XAS"
    XAUR = "XAUR"
    XBC = "XBC"
    XBY = "XBY"
    XCN = "XCN"
    XCP = "XCP"
    XDN = "XDN"
    XEL = "XEL"
    XEM = "XEM"
    NEM = "NEM"
    XHV = "XHV"
    XID = "XID"
    XLM = "XLM"
    XMG = "XMG"
    XMR = "XMR"
    XMT = "XMT"
    XMY = "XMY"
    XPM = "XPM"
    XRL = "XRL"
    XRP = "XRP"
    XSPEC = "XSPEC"
    XST = "XST"
    XTZ = "XTZ"
    XUC = "XUC"
    XVC = "XVC"
    XVG = "XVG"
    XWC = "XWC"
    XZC = "XZC"
    XZR = "XZR"
    YEE = "YEE"
    YOYOW = "YOYOW"
    ZCC = "ZCC"
    ZCL = "ZCL"
    ZCO = "ZCO"
    ZEC = "ZEC"
    ZEN = "ZEN"
    ZET = "ZET"
    ZIL = "ZIL"
    ZLA = "ZLA"
    ZRX = "ZRX"


class AV_SENTIMENT(StrEnum):  # as of 2024-11-29
    BLOCKCHAIN = "blockchain"
    EARNINGS = "earnings"
    IPO = "ipo"
    MNA = "mergers_and_acquisitions"
    FINANCIAL_MARKETS = "financial_markets"
    ECON_FISCAL = "economy_fiscal"
    ECON_MONETARY = "economy_monetary"
    ECON_MACRO = "ecenomy_macro"
    ENERGY_TRANSPORT = "energy_transportation"
    FINANCE = "finance"
    LIFE_SCIENCES = "life_sciences"
    MANUFACTURING = "manufacturing"
    REAL_ESTATE = "real_estate"
    RETAIL_WHOLESALE = "retail_wholesale"
    TECH = "technology"


class _TOPIC(TypedDict):
    topic: str
    relevance_score: str


class _TICKER_SENTIMENT(TypedDict):
    ticker: str
    relevance_score: str
    ticker_sentiment_score: str
    ticker_sentiment_label: str


class AV_SENTIMENT_ARTICLE(TypedDict):
    title: str
    url: str
    time_published: str
    authors: list[str]
    summary: str
    banner_image: str
    source: str
    category_within_source: str
    source_domain: str
    topics: list[_TOPIC]
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: list[_TICKER_SENTIMENT]
