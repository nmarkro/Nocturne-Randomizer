# rules define the core of the logic
def set_rules(world):
	def set_rule(a, rule):
		a.rule = rule
	def set_boss_rule(a, rule):
		a.boss_rule = rule

	# Area access rules
	set_rule(
		world.get_area('Shibuya'), 
		lambda state: state.has_checked('Forneus') or (state.has_terminal('Shibuya'))
	)
	set_rule(
		world.get_area('Amala Network 1'), 
		lambda state: state.has_checked('Forneus') or state.has_terminal('Shibuya')
	)
	set_rule(
		world.get_area('Ginza'), 
		lambda state: state.has_checked('Specter 1') or (state.has_terminal('Ginza'))
	)
	set_rule(
		world.get_area('Ginza Underpass'), 
		lambda state: state.has_terminal('Ginza Underpass') or state.has_terminal('Ginza')
	)
	set_rule(
		world.get_area('Ikebukuro'),
		lambda state: state.has_terminal('Ikebukuro') or state.has_checked('Matador')
	)
	set_rule(
		world.get_area('Nihilo East'), 
		lambda state: state.has_terminal('Nihilo East') or state.has_checked('Dante 1')
	)
	set_rule(
		world.get_area('Ikebukuro Tunnel'), 
		lambda state: state.has_terminal('Ikebukuro Tunnel') or state.has_checked('Ose')
	)
	set_rule(
		world.get_area('Kabukicho Prison'), 
		lambda state: state.has_terminal('Kabukicho Prison') or state.has_terminal('Ikebukuro Tunnel')
	)
	set_rule(
		world.get_area('Asakusa'), 
		lambda state: state.has_terminal('Asakusa') or state.has_checked('Mizuchi')
	)
	set_rule(
		world.get_area('Obelisk'), 
		lambda state: state.has_terminal('Obelisk') or state.has_terminal('Asakusa')
	)
	set_rule(
		world.get_area('Amala Network 2'), 
		lambda state: state.has_terminal('Asakusa') and state.has_checked('Sisters')
	)
	set_rule(
		world.get_area('Yoyogi Park'), 
		lambda state: state.has_terminal('Yoyogi Park') or state.has_checked('Specter 2')
	)
	set_rule(
		world.get_area('Amala Network 3'),
		lambda state: state.has_terminal('Asakusa') and state.has_checked('Girimehkala') and state.has_checked('Specter 2')
	)
	set_rule(
		world.get_area('Amala Temple'),
		lambda state: state.has_terminal('Amala Temple') or state.has_checked('Specter 3')
	)
	set_rule(
		world.get_area('Mifunashiro'),
		lambda state: state.has_terminal('Mifunashiro') or 
			(state.has_checked('Albion') and state.has_checked('Aciel') and state.has_checked('Skadi'))
	)
	set_rule(
		world.get_area('Yurakucho Tunnel'),
		lambda state: state.has_terminal('Yurakucho Tunnel') or state.has_checked('Futomimi')
	)
	set_rule(
		world.get_area('Diet Building'),
		lambda state: state.has_terminal('Diet Building') or state.has_terminal('Yurakucho Tunnel')
	)
	set_rule(
		world.get_area('Labyrinth of Amala'),
		lambda state: state.has_checked('Specter 1')
	)
	set_rule(
		world.get_area('ToK'),
		lambda state: state.has_terminal('Obelisk') and state.has_checked('Samael') and state.has_terminal('Amala Temple') and state.has_checked('Metatron')
	)

	# Check access rules
	set_rule(
		world.get_check('Noah'),
		lambda state: state.has_checked('Ahriman')
	)
	set_rule(
		world.get_check('Thor 2'),
		lambda state: state.has_checked('Ahriman')
	)
	set_rule(
		world.get_check('Baal Avatar'),
		lambda state: state.has_checked('Thor 2')
	)
	set_rule(
		world.get_check('Kagutsuchi'),
		lambda state: state.has_checked('Baal Avatar')
	)
	set_rule(
		world.get_check('Lucifer'),
		lambda state: state.has_checked('Kagutsuchi') and state.has_checked('Metatron')
	)
	set_rule(
		world.get_check('Futomimi'),
		lambda state: state.has_checked('Albion') and state.has_checked('Aciel') and state.has_checked('Skadi')
	)
	set_rule(
		world.get_check('The Harlot'),
		lambda state: state.has_checked('Girimehkala')
	)
	set_rule(
		world.get_check('Black Rider'),
		lambda state: state.has_checked('Red Rider')
	)
	set_rule(
		world.get_check('Mara'),
		lambda state: state.has_checked('Sisters')
	)
	set_rule(
		world.get_check('Troll'),
		lambda state: state.has_terminal('Ginza') and state.has_terminal('Ginza Underpass')
	)
	set_rule(
		world.get_check('Matador'),
		lambda state: state.has_checked('Troll')
	)
	set_rule(
		world.get_check('Red Rider'),
		lambda state: state.has_checked('White Rider')
	)
	set_rule(
		world.get_check('Yaksini'),
		lambda state: state.has_checked('Orthrus')
	)
	set_rule(
		world.get_check('Thor 1'),
		lambda state: state.has_checked('Yaksini')
	)
	set_rule(
		world.get_check('Dante 1'),
		lambda state: state.has_checked('Thor 1')
	)
	set_rule(
		world.get_check('Daisoujou'),
		lambda state: state.has_checked('Dante 1')
	)
	set_rule(
		world.get_check('Hell Biker'),
		lambda state: state.has_checked('Ose')
	)
	set_rule(
		world.get_check('Ongyo-Ki'),
		lambda state: state.has_checked('Kin-Ki') and state.has_checked('Sui-Ki') and state.has_checked('Fuu-Ki')
	)
	set_rule(
		world.get_check('Black Frost'),
		lambda state: state.has_checked('Mizuchi') and state.has_checked('Girimehkala')
	)
	set_rule(
		world.get_check('Pale Rider'),
		lambda state: state.has_checked('Black Rider')
	)
	set_rule(
		world.get_check('White Rider'),
		lambda state: state.has_checked('Matador') and state.has_checked('Daisoujou') and state.has_checked('Hell Biker')
	)
	set_rule(
		world.get_check('Mada'),
		lambda state: state.has_checked('Surt')
	)
	set_rule(
		world.get_check('Mot'),
		lambda state: state.has_checked('Mada')
	)
	set_rule(
		world.get_check('Mithra'),
		lambda state: state.has_checked('Mot')
	)
	set_rule(
		world.get_check('Samael'),
		lambda state: state.has_checked('Mithra')
	)
	set_rule(
		world.get_check('Dante 2'),
		lambda state: state.has_checked('White Rider') and state.has_checked('Red Rider') and state.has_checked('Black Rider')
	)
	set_rule(
		world.get_check('Beelzebub'),
		lambda state: state.has_checked('Dante 2') and state.has_checked('Trumpeter') and 
			state.has_checked('The Harlot') and state.has_checked('Pale Rider')
	)
	set_rule(
		world.get_check('Metatron'),
		lambda state: state.has_checked('Beelzebub') and state.has_terminal('Ginza') and state.has_terminal('Asakusa')
	)

	# Boss Magatama rules
	set_rule(
		world.get_check('Girimehkala'),
		lambda state: state.has_resistance('Mind')
	)
	set_rule(
		world.get_boss('The Harlot'),
		lambda state: state.has_resistance("Mind")
	)
	set_rule(
		world.get_boss('Matador'),
		lambda state: state.has_resistance("Force")
	)
	set_rule(
		world.get_boss('Thor 2'),
		lambda state: state.has_resistance('Elec')
	)
	set_rule(
		world.get_boss('Daisoujou'),
		lambda state: state.has_resistance('Expel') or state.has_resistance('Death') or state.has_resistance('Mind')
	)
	set_rule(
		world.get_boss('Ose'),
		lambda state: state.has_resistance('Phys')
	)
	set_rule(
		world.get_boss('Hell Biker'),
		lambda state: state.has_resistance("Force")
	)
	set_rule(
		world.get_boss('Kin-Ki'),
		lambda state: state.has_resistance("Phys")
	)
	set_rule(
		world.get_boss('Sui-Ki'),
		lambda state: state.has_resistance('Ice')
	)
	set_rule(
		world.get_boss('Fuu-Ki'),
		lambda state: state.has_resistance('Force')
	)
	set_rule(
		world.get_boss('Mizuchi'),
		lambda state: state.has_resistance('Mind')
	)
	set_rule(
		world.get_boss('Black Frost'),
		lambda state: state.has_resistance('Ice') or state.has_resistance('Death')
	)
	set_rule(
		world.get_boss('White Rider'),
		lambda state: state.has_resistance('Fire')
	)
	set_rule(
		world.get_boss('Surt'),
		lambda state: state.has_resistance('Fire')
	)
	set_rule(
		world.get_boss('Mada'),
		lambda state: state.has_resistance('Curse')
	)
	set_rule(
		world.get_boss('Mot'),
		lambda state: state.has_resistance("Force")
	)
	set_rule(
		world.get_boss('Mithra'),
		lambda state: state.has_resistance('Expel') or state.has_resistance('Death') or state.has_resistance('Mind')
	)
	set_rule(
		world.get_boss('Samael'),
		lambda state: state.has_resistance('Mind')
	)
	set_rule(
		world.get_boss('Skadi'),
		lambda state: state.has_resistance('Force') or state.has_resistance('Phys')
	)
	set_rule(
		world.get_boss('Beelzebub'),
		lambda state: state.has_resistance('Death')
	)
	set_rule(
		world.get_boss('Metatron'),
		lambda state: state.has_resistance("Expel")
	)

	# Make sure Resist/Null/Absorb/Repel Phys bosses aren't in SMC
	set_boss_rule(
		world.get_area('SMC'),
		lambda boss: not boss.phys_invalid
	)