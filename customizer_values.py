'''
A big fat stack of const values, mostly strings.
'''

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
    'f025b':'/fld/f/f025/f025_00b.LB',
    'f025c':'/fld/f/f025/f025_00c.LB',
    'f026':'/fld/f/f026/f026_000.LB',
    'f027':'/fld/f/f027/f027_000.LB',
    'f028':'/fld/f/f028/f028_000.LB',
    'f029':'/fld/f/f029/f029_000.LB',
    'f030':'/fld/f/f030/f030_000.LB',
    'f031':'/fld/f/f031/f031_000.LB',
    'f032':'/fld/f/f032/f032_000.LB',
    'f033':'/fld/f/f033/f033_000.LB',
    'f034':'/fld/f/f034/f034_000.LB',
    'f034b':'/fld/f/f034/f034_00b.LB',
    'f034c':'/fld/f/f034/f034_00c.LB',
    'f034d':'/fld/f/f034/f034_00d.LB',
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

MAGATAMA_REWARD_MSG = {
    'Marogareh':"You have obtained the Magatama ^bMarogareh^p.",
    'Wadatsumi':"You have obtained the Magatama ^bWadatsumi^p.",
    'Ankh':"You have obtained the Magatama ^bAnkh^p.",
    'Iyomante':"You have obtained the Magatama ^bIyomante^p.",
    'Shiranui':"You have obtained the Magatama ^bShiranui^p.",
    'Hifumi':"You have obtained the Magatama ^bHifumi^p.",
    'Kamudo':"You have obtained the Magatama ^bKamudo^p.",
    'Narukami':"You have obtained the Magatama ^bNarukami^p.",
    'Anathema':"You have obtained the Magatama ^bAnathema^p.",
    'Miasma':"You have obtained the Magatama ^bMiasma^p.",
    'Nirvana':"You have obtained the Magatama ^bNirvana^p.",
    'Murakumo':"You have obtained the Magatama ^bMurakumo^p.",
    'Geis':"You have obtained the Magatama ^bGeis^p.",
    'Djed':"You have obtained the Magatama ^bDjed^p.",
    'Muspell':"You have obtained the Magatama ^bMuspell^p.",
    'Gehenna':"You have obtained the Magatama ^bGehenna^p.",
    'Kamurogi':"You have obtained the Magatama ^bKamurogi^p.",
    'Satan':"You have obtained the Magatama ^bSatan^p.",
    'Adama':"You have obtained the Magatama ^bAdama^p.",
    'Vimana':"You have obtained the Magatama ^bVimana^p.",
    'Gundari':"You have obtained the Magatama ^bGundari^p.",
    'Sophia':"You have obtained the Magatama ^bSophia^p.",
    'Gaea':"You have obtained the Magatama ^bGaea^p.",
    'Kailash':"You have obtained the Magatama ^bKailash^p.",
    'Masakados':"You have obtained the Magatama ^bMasakados^p.",
}
FLAG_REWARD_MSG = {
    0x441: "You now have direct access to the ^rShinjuku Medical Center^p Terminal.",
    0x461: "You now have direct access to the ^rYoyogi Park^p Terminal.",
    0x481: "You now have direct access to the ^rShibuya^p Terminal.",
    0x4C1: "You now have direct access to the ^rGinza^p Terminal.",
    0x4E1: "You now have direct access to the ^rAssembly of Nihilo^p (East) Terminal.",
    0x4E2: "You now have direct access to the ^rAssembly of Nihilo: Marunouchi^p (West) Terminal.",
    0x501: "You now have direct access to the ^rYurakucho Tunnel^p Terminal.",
    0x521: "You now have direct access to the ^rGreat Underpass of Ginza^p Terminal.",
    0x541: "You now have direct access to the ^rIkebukuro^p Terminal.",
    0x581: "You now have direct access to the ^rKabukicho Prison^p Terminal.",
    0x5A1: "You now have direct access to the ^rIkebukuro Tunnel^p Terminal.",
    0x5C1: "You now have direct access to the ^rAsakusa^p Terminal.",
    0x661: "You now have direct access to the ^rTower of Kagutsuchi 1^p Terminal.",
    0x662: "You now have direct access to the ^rTower of Kagutsuchi 2^p Terminal.",
    0x663: "You now have direct access to the ^rTower of Kagutsuchi 3^p Terminal.",
    0x681: "You now have direct access to the ^rDiet Building^p Terminal.",
    0x6A1: "You now have direct access to the ^rAmala Temple^p Terminal.",
    0x6E1: "You now have direct access to the ^rMifunashiro^p Terminal.",
    0x751: "You now have direct access to the ^rLabyrinth of Amala^p Terminal.",
    0x3f1: "You have obtained the ^gBlack Key^p that opens the Black Temple in Amala Temple.",
    0x3f2: "You have obtained the ^gWhite Key^p that opens the White Temple in Amala Temple.",
    0x3f3: "You have obtained the ^gRed Key^p that opens the Red Temple in Amala Temple.",
    0x3f4: "You have obtained the ^gApocalypse Stone^p.",
    0x3f5: "You have obtained the ^gGolden Goblet^p.",
    0x3f6: "You have obtained an ^gEggplant^p.",
    0x3dd: "You have obtained the ^gKey to Yoyogi Park^p.",
    0x3da: "You have obtained the ^gYahirono Himorogi^p.",
    #0x3db: "You have obtained the ^gKimon Stone^p."
    #TODO: Candelabra
    #A key item, or at least message, for Specter 3 unlock.
    #Yellow Kila, Green Kila, White Kila, Red Kila
    #Deathstone
    #1000 Yen Bill
    #Manikin's Letter
} 
BOSS_NAMES = [
    "Forneus", "Ose", "Girimehkala", "Noah", "Ahriman", "Baal Avatar", "Specter 1", "Troll", "Red Rider", "Daisoujou", "Matador", "Black Rider", "Hell Biker", "White Rider", "Pale Rider", "Beelzebub", "Metatron", "The Harlot", "Trumpeter", "Mara", "Orthrus", "Yaksini", "Thor 1", "Mizuchi", "Black Frost", "Sui-Ki", "Kin-Ki", "Fuu-Ki", "Ongyo-Ki", "Specter 2", "Specter 3", "Sisters", "Clotho", "Lachesis", "Atropos", "Thor 2", "Surt", "Mada", "Mithra", "Mot", "Aciel", "Skadi", "Albion", "Bishamon 1", "Koumoku", "Zouchou", "Jikoku", "Bishamon 2", "Dante 1", "Dante 2", "Futomimi", "Archangels"
]
LOCATION_NAMES_BY_CHECK = {
    "Forneus":"Shinjuku Medical Center",
    "Ose":"Assembly of Nihilo", 
    "Girimehkala":"Yoyogi Park", 
    "Noah":"Tower of Kagutsuchi 2", 
    "Ahriman":"Tower of Kagutsuchi 1", 
    "Baal Avatar":"Tower of Kagutsuchi 3", 
    "Specter 1":"Amala Network", 
    "Troll":"Ginza", 
    "Red Rider":"Ginza Underpass", 
    "Daisoujou":"Ikebukuro", 
    "Matador":"Ginza Underpass", 
    "Black Rider":"Shinjuku Medical Center", 
    "Hell Biker":"Ikebukuro", 
    "White Rider":"Shibuya", 
    "Pale Rider":"Asakusa", 
    "Beelzebub":"Labyrinth of Amala", 
    "Metatron":"Labyrinth of Amala", 
    "The Harlot":"Yoyogi Park", 
    "Trumpeter":"Yurakucho Tunnel", 
    "Mara":"Shibuya", 
    "Orthrus":"Mantra HQ", 
    "Yaksini":"Mantra HQ", 
    "Thor 1":"Mantra HQ", 
    "Mizuchi":"Kabukicho Prison", 
    "Black Frost":"Asakusa", 
    "Sui-Ki":"Ikebukuro Tunnel", 
    "Kin-Ki":"Ikebukuro Tunnel", 
    "Fuu-Ki":"Ikebukuro Tunnel", 
    "Ongyo-Ki":"Ikebukuro Tunnel", 
    "Specter 2":"Amala Network", 
    "Specter 3":"Amala Network", 
    "Sisters":"Obelisk", 
    "Clotho":"Obelisk", 
    "Lachesis":"Obelisk", 
    "Atropos":"Obelisk", 
    "Thor 2":"Tower of Kagutsuchi 3", 
    "Surt":"Diet Building", 
    "Mada":"Diet Building", 
    "Mithra":"Diet Building", 
    "Mot":"Diet Building", 
    "Aciel":"Amala Temple", 
    "Skadi":"Amala Temple", 
    "Albion":"Amala Temple", 
    "Bishamon 1":"Asakusa", 
    "Koumoku":"Bandou Shrine", 
    "Zouchou":"Bandou Shrine", 
    "Jikoku":"Bandou Shrine", 
    "Bishamon 2":"Bandou Shrine", 
    "Dante 1":"Ikebukuro", 
    "Dante 2":"Labyrinth of Amala", 
    "Futomimi":"Mifunashiro", 
    "Archangels":"Yurakucho Tunnel"
}
VANILLA_MAGATAMAS = {
    "Forneus": "Wadatsumi",
    "Thor 1": "Narukami",
    "Ose": "Anathema",
    "Mizuchi": "Miasma",
    "Sisters": "Djed",
    "Albion": "Adama"
}
#reward is world.checks['Forneus'].boss.reward
#world.checks['Forneus'].boss.name is name of boss at Forneus check.
#what will be added is world.checks['Forneus'].boss.flag_rewards. A list of flags to be set on defeat.
#Missing Reward Messages:
#Orthrus
#Yaksini
#Berith
#Kaiwan

#Missing Inst Insertion:
#Above