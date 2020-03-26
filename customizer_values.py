'''
To be mostly removed by Markro's FileSystem stuff.

The set of values that are usable with a customizer. Contains no actual code.
A customizer decompresses field scripts and adds space at the end of each script. That space is used as a stack.
version: Version string.
extended_sizes: Amount of bytes extended to each script.
customizer_offsets: Absolute offsets of each script to the ISO.
hint_msgs: Tuples of script names and message labels to be used (or at least looked at) for hint usage.
'''

version = "0p2a"
extended_sizes = 1000
script_sizes = {
    'e601': 0x166d,
    'e634': 12887,
    'e658': 5875,
    'e673': 5885,
    'e674': 25048,
    'e723': 5317,
    'e731': 3854,
    'e740': 4665,
    'e741': 3032,
    'e742': 3260,
    'e743': 3291,
    'e744': 2709,
    'e745': 2561,
    'e746': 2887,
    'e747': 4757,
    'e748': 4343,
    'e749': 6346,
    'e750': 3994,
    'f001': 20950,
    'f002': 18635,
    'f003': 17621,
    'f004': 19914,
    'f005': 13178,
    'f006': 13326,
    'f007': 13779,
    'f008': 13234,
    'f011': 19121,
    'f012': 15981,
    'f013': 13990,
    'f014': 43202,
    'f015': 70423,
    'f016': 91809,
    'f017': 41669,
    'f018': 32427,
    'f019': 44682,
    'f020': 67530,
    'f021': 38853,
    'f022': 47062,
    'f023': 39986,
    'f024': 76511,
    'f025': 73863,
    'f026': 33819,
    'f027': 44046,
    'f028': 40055,
    'f029': 19187,
    'f030': 14336,
    'f031': 128151,
    'f032': 63730,
    'f033': 87249,
    'f034': 82000,
    'f035': 34928,
    'f036': 43634,
    'f037': 57289,
    'f038': 29942,
    'f039': 18702,
    'f040': 21120,
    'f041': 60446,
    'f042': 51521,
    'f043': 93887,
    'f044': 69839,
    'f045': 88575
}
customizer_offsets = {
    'e506': 0xd7310800,
    'e601': 0xd85dd000,
    'e618': 0xdc39b800,
    'e634': 0xdf3cd000,
    'e658': 0xe2af9800,
    'e673': 0xe6166800,
    'e674': 0xe6756800,
    'e723': 0xf0e67000,
    'e731': 0xf1ec1800,
    'e740': 0xf2090000,
    'e741': 0xf22c8800,
    'e742': 0xf2418000,
    'e743': 0xf262f800,
    'e744': 0xf2794000,
    'e745': 0xf28e7000,
    'e746': 0xf2a5a000,
    'e747': 0xf2cad800,
    'e748': 0xf2ed5000,
    'e749': 0xf3235800,
    'e750': 0xf349e800,
    'f001': 0x855CA210,
    'f002': 0x85B59210,
    'f003': 0x861D4210,
    'f004': 0x86743210,
    'f005': 0x86C24A10,
    'f006': 0x87179210,
    'f007': 0x8759C210,
    'f008': 0x87A6DA10,
    'f011': 0x87DE3A10,
    'f012': 0x882AFA10,
    'f013': 0x887A4A10,
    'f014': 0x88a51210,
    'f015': 0x89707210,
    'f016': 0x8B4CF210,
    'f017': 0x8F00AA10,
    'f018': 0x903EF210,
    'f019': 0x911DAA10,
    'f020': 0x91F55210,
    'f021': 0x95ED3210,
    'f022': 0x97D3EA10,
    'f023': 0x9A4B7A10,
    'f024': 0x9B37AA10,
    'f025': 0x9D33DA10,
    'f026': 0x9ed79210,
    'f027': 0xA0698A10,
    'f028': 0xa2621210,
    'f029': 0xa329c210,
    'f030': 0xa4256210,
    'f031': 0xa4429a10,
    'f032': 0xA64BAA10,
    'f033': 0xa862c210,
    'f034': 0xab9b3210,
    'f035': 0xADE67210,
    'f036': 0xAF165A10,
    'f037': 0xB0F78210,
    'f038': 0xB3674210,
    'f039': 0xB3A59A10,
    'f040': 0xB3CF8210,
    'f041': 0xB4031A10,
    'f042': 0xB6387210,
    'f043': 0xB97DFA10,
    'f044': 0xBCD29A10,
    'f045': 0xC053BA10
}
hint_msgs = [
    ('f015',"F015_SINEN02"),
    ('f015',"F015_SINEN03"),
    ('f015',"F015_SINEN13"),
    ('f015',"F015_SINEN10_01"),
    ('f015',"F015_SINEN16_YES_02"),
    ('f015',"F015_SINEN21"),
    ('f015',"F015_SINEN22"),
    ('f002',"F002_SINEN_02"),
    ('f002',"F002_SINEN_03"),
    ('f002',"F002_SINEN_04"),
    ('f016',"F016_INKYU01_02"),
    ('f016',"F016_SINEN03_05"),
    ('f017',"F017_SINEN_01_01"),
    ('f017',"F017_SINEN_02"),
    ('f017',"F017_SINEN_03_02"),
    ('f017',"F017_SINEN_03"),
    ('f017',"F017_SINEN_05_02"),
    ('f017',"F017_SINEN_06"),
    ('f019',"F019_SINEN11_02"),
    ('f019',"F019_SINEN01"),
    ('f019',"F019_SINEN03_01"),
    ('f019',"F019_BAR_SINEN01_03"),
    ('f003',"F003_SINEN05"),
    ('f003',"F003_SINEN03_00"),
    ('f003',"F003_SINEN06"),
    ('f022',"F022_SINEN01"),
    ('f023',"F023_DEVIL_TARM_05"),
    ('f023',"F023_SINEN01_02"),
    ('f024',"ONI_003_03"),
    ('f004',"F004_SINEN03_02"),
    ('f004',"F004_SINEN04"),
    ('f026',"F026_SINEN01"),
    ('f026',"F026_SINEN04"),
    ('f026',"F026_SINEN08"),
    ('f026',"F026_SINEN05_01"),
    ('f026',"F26_AREA12_NPC1"),
    ('f026',"F026_MANE03"),
    ('f026',"F026_MANE05"),
    ('f031',"F031_SINEN_01_01"),
    ('f031',"F031_SINEN_04_01"),
    ('f031',"F031_SINEN_10"),
    ('f031',"F031_SINEN_11_01"),
    ('f029',"F029_SINEN01_02"),
    ('f029',"F029_SINEN02_02"),
    ('f016',"F016_SINEN09_02"),
    ('f016',"F016_SINEN06_02"),
    ('f016',"F016_SINEN10_02"),
    ('f016',"F016_SINEN07_02"),
    ('f016',"F016_SINEN13_02"),
    ('f021',"F021_SINEN02_02"),
    ('f021',"F021_SINEN01"),
    ('f021',"F021_SINEN03"),
    ('f033',"F033_SINEN02"),
    ('f033',"F033_SINEN01_02"),
    ('f033',"F033_SINEN06_02"),
    ('f033',"F033_SINEN05"),
    ('f033',"F033_SINEN07_02"),
]

SCRIPT_OBJ_PATH = {
    ###Event scripts###
    'e500':'/event/e500/e500/scr/e500.bf',
    'e501':'/event/e500/e501/scr/e501.bf',
    'e502':'/event/e500/e502/scr/e502.bf',
    'e503':'/event/e500/e503/scr/e503.bf',
    'e506':'/event/e500/e506/scr/e506.bf', #Originally unused, rewritten and used as an initialization script
    'e510':'/event/e510/e510/scr/e510.bf',
    'e512':'/event/e510/e512/scr/e512.bf',
    'e550':'/event/e550/e550/scr/e550.bf', #Isamu calls in intro (probably debug test)
    'e601':'/event/e600/e601/scr/e601.bf', #Starting intro
    'e602':'/event/e600/e602/scr/e602.bf', #Intro Yoyogi Park with Hijiri
    'e603':'/event/e600/e603/scr/e603.bf', #Intro Chiaki
    'e604':'/event/e600/e604/scr/e604.bf', #Intro finding Isamu
    'e605':'/event/e600/e605/scr/e605.bf', #Intri Chiaki & Isamu with basement card
    'e607':'/event/e600/e607/scr/e607.bf',
    'e608':'/event/e600/e608/scr/e608.bf',
    'e611':'/event/e610/e611/scr/e611.bf',
    'e614':'/event/e610/e614/scr/e614.bf', #Just before waking up
    'e615':'/event/e610/e615/scr/e615.bf', #Intro Hikawa
    'e616':'/event/e610/e616/scr/e616.bf', #World Ends
    'e617':'/event/e610/e617/scr/e617.bf', #Intro getting magatama'd
    'e618':'/event/e610/e618/scr/e618.bf', #Waking up in bed
    'e619':'/event/e610/e619/scr/e619.bf', #Hijiri in SMC
    'e621':'/event/e620/e621/scr/e621.bf', #Chiaki in Shibuya
    'e623':'/event/e620/e623/scr/e623.bf', #Hijiri 2
    'e624':'/event/e620/e624/scr/e624.bf', 
    'e628':'/event/e620/e628/scr/e628.bf', #Isamu smacked in Ikebukuro
    'e629':'/event/e620/e629/scr/e629.bf', #Gozu Tennoh 1st (+2 demons)
    'e632':'/event/e630/e632/scr/e632.bf', #In Nihilo w/Hijiri
    'e634':'/event/e630/e634/scr/e634.bf', #Defeating Ose
    'e635':'/event/e630/e635/scr/e635.bf', #Ikebukuro front w/Chiaki
    'e636':'/event/e630/e636/scr/e636.bf', #Gozu Tennoh 2nd - post Nihilo
    'e639':'/event/e630/e639/scr/e639.bf', #Kabukicho Prison Isamu scene
    'e640':'/event/e640/e640/scr/e640.bf', #With Hijiri at Terminal (Ginza?)
    'e644':'/event/e640/e644/scr/e644.bf', #Sakahagi intro scene
    'e646':'/event/e640/e646/scr/e646.bf', #With Hijiri at Terminal (Asakusa?)
    'e650':'/event/e650/e650/scr/e650.bf', #Talking to Lucy in Obelisk
    'e651':'/event/e650/e651/scr/e651.bf', #Saving Yuko in Obelisk (+2 Demons)
    'e652':'/event/e650/e652/scr/e652.bf', #Post-Obelisk Hijiri
    'e655':'/event/e650/e655/scr/e655.bf', #Isamu in Amala Network 2
    'e656':'/event/e650/e656/scr/e656.bf', #Hijiri after Amala Network 2
    'e657':'/event/e650/e657/scr/e657.bf', #Yuko in Yoyogi (Yoyogi Key)
    'e658':'/event/e650/e658/scr/e658.bf', #Sakahagi + Girimehkala Fight
    'e659':'/event/e650/e659/scr/e659.bf', #Giving Yuko pyrmadion back in Yoyogi
    'e660':'/event/e660/e660/scr/e660.bf', #Hijiri Asakusa again
    'e661':'/event/e660/e661/scr/e661.bf', #Gozu Tennoh 3rd - Chiaki growing arm
    'e662':'/event/e660/e662/scr/e662.bf', #Asakusa going into Amala Network 3
    'e670':'/event/e670/e670/scr/e670.bf', #Isamu dumping Hijiri in Amala Temple
    'e671':'/event/e670/e671/scr/e671.bf', #Isamu turning into Noah
    'e672':'/event/e670/e672/scr/e672.bf', #Mifunashiro boss decision
    'e673':'/event/e670/e673/scr/e673.bf', #Mifunashiro post-boss. Opens Yurakucho Tunnel
    'e674':'/event/e670/e674/scr/e674.bf', #Diet Building Yuko & Hikawa
    'e677':'/event/e670/e677/scr/e677.bf', #Beating Noah
    'e678':'/event/e670/e678/scr/e678.bf', #Beating Ahriman
    'e679':'/event/e670/e679/scr/e679.bf', #Beating Baal
    'e680':'/event/e680/e680/scr/e680.bf', #Encountering Noah
    'e681':'/event/e680/e681/scr/e681.bf', #Encountering Ahriman
    'e682':'/event/e680/e682/scr/e682.bf', #Encountering Baal
    'e684':'/event/e680/e684/scr/e684.bf', #Yosuga Ending
    'e686':'/event/e680/e686/scr/e686.bf', #Shijima Ending
    'e688':'/event/e680/e688/scr/e688.bf', #Musubi Ending
    'e692':'/event/e690/e692/scr/e692.bf', #Clear data save
    'e693':'/event/e690/e693/scr/e693.bf', #Neutral Ending
    'e694':'/event/e690/e694/scr/e694.bf', #Demon Ending
    'e697':'/event/e690/e697/scr/e697.bf', #Hikawa in Ikebukuro
    'e700':'/event/e700/e700/scr/e700.bf', 
    'e701':'/event/e700/e701/scr/e701.bf', #Yuko in Yoyogi Park. Jumps to pre or post Gary
    'e702':'/event/e700/e702/scr/e702.bf', #Mifunashiro. Jumps to pre or post boss
    'e703':'/event/e700/e703/scr/e703.bf', #Amala Temple dumping Hijiri (maybe decision?)
    'e704':'/event/e700/e704/scr/e704.bf', #Kagutsuchi Decision into ToK
    'e705':'/event/e700/e705/scr/e705.bf', #Kagutsuchi Demon ending (?)
    'e799':'/event/e700/e799/scr/e799.bf',
    'e710':'/event/e710/e710/scr/e710.bf', #LoA Lobby Cutscene 1
    'e711':'/event/e710/e711/scr/e711.bf', #LoA Lobby Cutscene 2
    'e712':'/event/e710/e712/scr/e712.bf', #LoA 1st Kalpa Cutscene
    'e713':'/event/e710/e713/scr/e713.bf', #LoA 2nd Kalpa Cutscene
    'e714':'/event/e710/e714/scr/e714.bf', #LoA 3rd Kalpa Cutscene
    'e715':'/event/e710/e715/scr/e715.bf', #LoA 4th Kalpa Cutscene
    'e716':'/event/e710/e716/scr/e716.bf', #LoA Afterlife Bell Cutscene
    'e717':'/event/e710/e717/scr/e717.bf', #LoA Repeat
    'e718':'/event/e710/e718/scr/e718.bf', #LoA Complete
    'e719':'/event/e710/e719/scr/e719.bf', #LoA Complete 2
    'e720':'/event/e720/e720/scr/e720.bf', #LoA Repeat 2
    'e721':'/event/e720/e721/scr/e721.bf', #LoA Repeat 3
    'e722':'/event/e720/e722/scr/e722.bf', #LoA Repeat 4
    'e723':'/event/e720/e723/scr/e723.bf', #Dante 1 (Ikebukuro)
    'e726':'/event/e720/e726/scr/e726.bf', #Fight Lucy
    'e727':'/event/e720/e727/scr/e727.bf', #TDE
    'e728':'/event/e720/e728/scr/e728.bf', #Meet Dante 2
    'e729':'/event/e720/e729/scr/e729.bf', #Dante 2 Start
    'e730':'/event/e730/e730/scr/e730.bf', #Recruit Dante
    'e731':'/event/e730/e731/scr/e731.bf', #Dante 2 End
    'e740':'/event/e740/e740/scr/e740.bf', #Matador Fight
    'e741':'/event/e740/e741/scr/e741.bf', #Hell Biker Fight 
    'e742':'/event/e740/e742/scr/e742.bf', #Daisoujou
    'e743':'/event/e740/e743/scr/e743.bf', #White Rider
    'e744':'/event/e740/e744/scr/e744.bf', #Red Rider
    'e745':'/event/e740/e745/scr/e745.bf', #Black Rider
    'e746':'/event/e740/e746/scr/e746.bf', #Pale Rider
    'e747':'/event/e740/e747/scr/e747.bf', #The Harlot
    'e748':'/event/e740/e748/scr/e748.bf', #Trumpeter
    'e749':'/event/e740/e749/scr/e749.bf', #Beelzebub
    'e750':'/event/e750/e750/scr/e750.bf', #Metatron
    'e751':'/event/e750/e751/scr/e751.bf',
    'e752':'/event/e750/e752/scr/e752.bf',
    'e753':'/event/e750/e753/scr/e753.bf',
    'e754':'/event/e750/e754/scr/e754.bf',
    'e755':'/event/e750/e755/scr/e755.bf',
    'e799':'/event/e790/e799/scr/e799.bf',
    'e800':'/event/e800/e800/scr/e800.bf', #Mido
    'e801':'/event/e800/e801/scr/e801.bf', #Heal spot
    'e802':'/event/e800/e802/scr/e802.bf', #Manikin shop
    'e803':'/event/e800/e803/scr/e803.bf', #Rag's
    'e804':'/event/e800/e804/scr/e804.bf', #Terminal
    'e805':'/event/e800/e805/scr/e805.bf', #Small Terminal
    'e806':'/event/e800/e806/scr/e806.bf', #Small Terminal Amala Network
    'e807':'/event/e800/e807/scr/e807.bf', #Normal Fusion
    'e809':'/event/e800/e809/scr/e809.bf', #Evolution
    'e810':'/event/e810/e810/scr/e810.bf',
    #'ctest01':'/event/scr/ctest01.bf',
    #'ctest02':'/event/scr/ctest02.bf',
    #'ctest07':'/event/scr/ctest07.bf',
    #'gameover':'/event/scr/gameover.bf',
    #'scene01':'/event/scr/scene01.bf',
    #'scene02':'/event/scr/scene02.bf',
    #'scene03':'/event/scr/scene03.bf',
    #'scene04':'/event/scr/scene04.bf',
    #'scene05':'/event/scr/scene05.bf',
    #'scene06':'/event/scr/scene06.bf',
    #'scene07':'/event/scr/scene07.bf',
    #'scene08':'/event/scr/scene08.bf',
    #'scene09':'/event/scr/scene09.bf',
    #'scene11':'/event/scr/scene11.bf',
    ###Field scripts## - Read only. Needs to be written in respective LB0_PATH
    'f001':'/fld/f/f001/f001.bf', #Pre-Conception outside
    'f002':'/fld/f/f002/f002.bf', #Shinjuku/Yoyogi/Shibuya Area
    'f003':'/fld/f/f003/f003.bf', #Ginza Area
    'f004':'/fld/f/f004/f004.bf', #Ikebukuro Area
    'f005':'/fld/f/f005/f005.bf', #Asakusa Area
    'f006':'/fld/f/f006/f006.bf', #Obelisk Area
    'f007':'/fld/f/f007/f007.bf', #Obelisk Area w/ToK
    'f008':'/fld/f/f008/f008.bf', 
    'f011':'/fld/f/f011/f011.bf', #Yoyogi Park Station - Pre-Conception
    'f012':'/fld/f/f012/f012.bf', #Afterlife Bell and event test ???
    'f013':'/fld/f/f013/f013.bf', 
    'f014':'/fld/f/f014/f014.bf', #SMC Front (pre and post)
    'f015':'/fld/f/f015/f015.bf', #SMC Annex
    'f016':'/fld/f/f016/f016.bf', #Yoyogi Park
    'f017':'/fld/f/f017/f017.bf', #Shibuya
    'f018':'/fld/f/f018/f018.bf', #Amala Network 1
    'f019':'/fld/f/f019/f019.bf', #Ginza
    'f020':'/fld/f/f020/f020.bf', #East Nihilo
    'f021':'/fld/f/f021/f021.bf', #Yurakucho Tunnel
    'f022':'/fld/f/f022/f022.bf', #Ginza Underpass
    'f023':'/fld/f/f023/f023.bf', #Ikebukuro
    'f024':'/fld/f/f024/f024.bf', #Mantra HQ
    'f025':'/fld/f/f025/f025.bf', #Kabukucho Prison
    'f026':'/fld/f/f026/f026.bf', #Ikebukuro Tunnel
    'f027':'/fld/f/f027/f027.bf', #Asakusa
    'f028':'/fld/f/f028/f028.bf', #Amala Network 2
    'f029':'/fld/f/f029/f029.bf', #Asakusa Tunnel 
    'f030':'/fld/f/f030/f030.bf', #Amala Network 3
    'f031':'/fld/f/f031/f031.bf', #Obelisk
    'f032':'/fld/f/f032/f032.bf', #ToK1
    'f033':'/fld/f/f033/f033.bf', #Diet Building
    'f034':'/fld/f/f034/f034.bf', #Amala Temple
    'f035':'/fld/f/f035/f035.bf', #Mifunashiro
    'f036':'/fld/f/f036/f036.bf', #ToK2
    'f037':'/fld/f/f037/f037.bf', #ToK3
    'f038':'/fld/f/f038/f038.bf', #Bandou Shrine
    'f039':'/fld/f/f039/f039.bf', #Bishamon Temple
    'f040':'/fld/f/f040/f040.bf', #LoA Lobby
    'f041':'/fld/f/f041/f041.bf', #1st Kalpa
    'f042':'/fld/f/f042/f042.bf', #2nd Kalpa
    'f043':'/fld/f/f043/f043.bf', #3rd Kalpa
    'f044':'/fld/f/f044/f044.bf', #4th Kalpa
    'f045':'/fld/f/f045/f045.bf' #5th Kalpa
    #'f100':'/fld/f/f100/f100.bf' #(unused) Ikebukuro Tunnel in Japanese???
}
LB0_PATH = {
    'f001':'/fld/f/f001/f001_000.LB',
    'f002':'/fld/f/f002/f002_000.LB',
    'f003':'/fld/f/f003/f003_000.LB',
    'f004':'/fld/f/f004/f004_000.LB',
    'f005':'/fld/f/f005/f005_000.LB',
    'f006':'/fld/f/f006/f006_000.LB',
    'f007':'/fld/f/f007/f007_000.LB',
    'f008':'/fld/f/f008/f008_000.LB',
    'f011':'/fld/f/f011/f011_000.LB',
    'f012':'/fld/f/f012/f012_000.LB',
    'f013':'/fld/f/f013/f013_000.LB',
    'f014':'/fld/f/f014/f014_000.LB',
    'f015':'/fld/f/f015/f015_000.LB',
    'f016':'/fld/f/f016/f016_000.LB',
    'f017':'/fld/f/f017/f017_000.LB',
    'f018':'/fld/f/f018/f018_000.LB',
    'f019':'/fld/f/f019/f019_000.LB',
    'f020':'/fld/f/f020/f020_000.LB',
    'f021':'/fld/f/f021/f021_000.LB',
    'f022':'/fld/f/f022/f022_000.LB',
    'f023':'/fld/f/f023/f023_000.LB',
    'f024':'/fld/f/f024/f024_000.LB',
    'f024b':'/fld/f/f024/f024_00b.LB',#It is a mystery
    'f024c':'/fld/f/f024/f024_00c.LB',#It is a mystery
    'f025':'/fld/f/f025/f025_000.LB',
    'f026':'/fld/f/f026/f026_000.LB',
    'f027':'/fld/f/f027/f027_000.LB',
    'f028':'/fld/f/f028/f028_000.LB',
    'f029':'/fld/f/f029/f029_000.LB',
    'f030':'/fld/f/f030/f030_000.LB',
    'f031':'/fld/f/f031/f031_000.LB',
    'f032':'/fld/f/f032/f032_000.LB',
    'f033':'/fld/f/f033/f033_000.LB',
    'f034':'/fld/f/f034/f034_000.LB',
    'f035':'/fld/f/f035/f035_000.LB',
    'f036':'/fld/f/f036/f036_000.LB',
    'f037':'/fld/f/f037/f037_000.LB',
    'f038':'/fld/f/f038/f038_000.LB',
    'f039':'/fld/f/f039/f039_000.LB',
    'f040':'/fld/f/f040/f040_000.LB',
    'f041':'/fld/f/f041/f041_000.LB',
    'f042':'/fld/f/f042/f042_000.LB',
    'f043':'/fld/f/f043/f043_000.LB',
    'f044':'/fld/f/f044/f044_000.LB',
    'f045':'/fld/f/f045/f045_000.LB'
}
WAP_PATH = {
    'f001':'/fld/f/f001/F001.WAP',
    'f002':'/fld/f/f002/F002.WAP',
    'f003':'/fld/f/f003/F003.WAP',
    'f004':'/fld/f/f004/F004.WAP',
    'f005':'/fld/f/f005/F005.WAP',
    'f006':'/fld/f/f006/F006.WAP',
    'f007':'/fld/f/f007/F007.WAP',
    'f008':'/fld/f/f008/F008.WAP',
    'f011':'/fld/f/f011/F011.WAP',
    'f012':'/fld/f/f012/F012.WAP',
    'f013':'/fld/f/f013/F013.WAP',
    'f014':'/fld/f/f014/F014.WAP',
    'f015':'/fld/f/f015/F015.WAP',
    'f016':'/fld/f/f016/F016.WAP',
    'f017':'/fld/f/f017/F017.WAP',
    'f018':'/fld/f/f018/F018.WAP',
    'f019':'/fld/f/f019/F019.WAP',
    'f020':'/fld/f/f020/F020.WAP',
    'f021':'/fld/f/f021/F021.WAP',
    'f022':'/fld/f/f022/F022.WAP',
    'f023':'/fld/f/f023/F023.WAP',
    'f024':'/fld/f/f024/F024.WAP',
    'f025':'/fld/f/f025/F025.WAP',
    'f026':'/fld/f/f026/F026.WAP',
    'f027':'/fld/f/f027/F027.WAP',
    'f028':'/fld/f/f028/F028.WAP',
    'f029':'/fld/f/f029/F029.WAP',
    'f030':'/fld/f/f030/F030.WAP',
    'f031':'/fld/f/f031/F031.WAP',
    'f032':'/fld/f/f032/F032.WAP',
    'f033':'/fld/f/f033/F033.WAP',
    'f034':'/fld/f/f034/F034.WAP',
    'f035':'/fld/f/f035/F035.WAP',
    'f036':'/fld/f/f036/F036.WAP',
    'f037':'/fld/f/f037/F037.WAP',
    'f038':'/fld/f/f038/F038.WAP',
    'f039':'/fld/f/f039/F039.WAP',
    'f040':'/fld/f/f040/F040.WAP',
    'f041':'/fld/f/f041/F041.WAP',
    'f042':'/fld/f/f042/F042.WAP',
    'f043':'/fld/f/f043/F043.WAP',
    'f044':'/fld/f/f044/F044.WAP',
    'f045':'/fld/f/f045/F045.WAP'
}