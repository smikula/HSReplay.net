from hearthstone import cardxml, enums
from hsreplaynet.cards.models import Card


carddb = cardxml.load()[0]


def test_load_al_akir():
	id = "NEW1_010"
	card = carddb[id]
	obj = Card.from_cardxml(card)

	assert obj.id == id
	assert obj.name == "Al'Akir the Windlord"
	assert obj.divine_shield
	assert obj.taunt
	assert obj.windfury
	assert obj.card_class == enums.CardClass.SHAMAN
	assert obj.card_set == enums.CardSet.EXPERT1
	assert not obj.spell_damage


def test_load_evolved_kobold():
	id = "OG_082"
	card = carddb[id]
	obj = Card.from_cardxml(card)

	assert obj.id == id
	assert obj.name == "Evolved Kobold"
	assert obj.card_class == enums.CardClass.NEUTRAL
	assert obj.card_set == enums.CardSet.OG
	assert obj.spell_damage == 2


def test_load_velens_chosen():
	id = "GVG_010"
	card = carddb[id]
	obj = Card.from_cardxml(card)

	assert obj.id == id
	assert obj.name == "Velen's Chosen"
	assert obj.type == enums.CardType.SPELL
	assert obj.card_class == enums.CardClass.PRIEST
	assert obj.card_set == enums.CardSet.GVG
	assert not obj.spell_damage
