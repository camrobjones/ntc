"""
NTC Scratch
-----------
"""
import numpy as np

from main.models import User
from ntc.models import Profile
from ntc import ntc


def generate_profiles(prefix="test", n=20):
    """Generate profiles to create votes"""
    profiles = []
    for i in range(n):
        username = f"{prefix}_{i + 1}"
        email = f"{username}@localhost.com"
        user = User.objects.create(username=username, email=email)
        profile = Profile.objects.create(user=user)
        profiles.append(profile)
    return profiles


profiles = generate_profiles()


def generate_votes(topic_id, profiles, x_mean, x_sd, y_mean, y_sd):

    n = len(profiles)
    x_vals = np.random.normal(x_mean, x_sd, n)
    x_vals = np.minimum(x_vals, 10)
    x_vals = np.maximum(x_vals, -10)

    y_vals = np.random.normal(y_mean, y_sd, n)
    y_vals = np.minimum(y_vals, 10)
    y_vals = np.maximum(y_vals, -10)

    for profile, x, y in zip(profiles, x_vals, y_vals):
        data = {"topic_id": topic_id, "x": x, "y": y}
        ntc.submit_vote(profile, data)


generate_votes(40, profiles, 7, 1, -4.6, 3)

# Scotland
generate_votes(19, profiles, -4, 1, 1.2, 3)

# Globalism
generate_votes(29, profiles, 3, 1, -4, 3)

# Mao
generate_votes(10, profiles, -8.5, 1, 8.4, 3)

# Ghandi
generate_votes(5, profiles, -8.5, 1, -3.4, 3)


"""
"""

from ntc import models, ntc

profile = models.Profile.objects.first()

topic_info = ntc.get_topic_info(40, profile)

