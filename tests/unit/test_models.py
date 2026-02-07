from src.models.schemas import UserProfile

def test_user_profile_defaults():
    profile = UserProfile(age=30, dietary_restrictions=["Vegan"])
    assert profile.name == "User"
    assert "Vegan" in profile.dietary_restrictions
