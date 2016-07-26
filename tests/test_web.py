from allauth.socialaccount.providers import registry


def test_battlenet_auth_loaded():
	assert registry.loaded
	provider = registry.by_id("battlenet")
	assert provider.id == "battlenet"
