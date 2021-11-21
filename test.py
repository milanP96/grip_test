import unittest

from fake_db import Db
from main import get_users, get_playback_time, user_features_per_app


class TestFakeDbCase(unittest.TestCase):
    def setUp(self):
        db = Db()
        data = db.data()  # get data from fake db
        self.actions = data["actions"]
        self.user_apps = data["user_apps"]
        self.app_features = data["app_features"]
        self.user_features = data["user_features"]

    def test_get_users(self):
        """
        E.g. getUsers(records, “start”, 700, 900) will return the result [3]
        """

        users = get_users(self.actions, "start", 700, 900)

        self.assertIsInstance(users, list)
        self.assertEqual(users[0], 3)

    def test_get_playback_time(self):
        """ E.g. getPlaybackTime(1, records) will return 310 """

        playback_time = get_playback_time(1, self.actions)

        self.assertEqual(playback_time, 310)

    def test_user_features_per_app(self):
        """
        returns dictionary object that looks something like this:
        {
        "user_id": 1,
            "application_permissions": [
                {
                "app_id": 1,
                "features_allowed": [1, 2]
                },
                {
                "app_id": 2,
                "features_allowed": [5]
                },
                {
                "app_id": 3
                "features_allowed": []
                },
                ...
            ]
        }
        """

        expected_output = {
            "user_id": 1,
            "application_permissions": [
                {
                    "app_id": 1,
                    "features_allowed": [1, 2]
                },
                {
                    "app_id": 2,
                    "features_allowed": [5]
                },
                {
                    "app_id": 3,
                    "features_allowed": []
                }
            ]
        }

        application_permissions_output = user_features_per_app(1, self.user_apps, self.app_features, self.user_features)

        self.assertDictEqual(expected_output, application_permissions_output)


class TestAdditionalCases(TestFakeDbCase):

    def test_get_users_multiple_users(self):
        actions = self.actions
        actions.extend(
            [
                {
                    "user_id": 4,
                    "device": "Windows 10",
                    "action": "start",
                    "date_actioned": 700
                },
                {
                    "user_id": 5,
                    "device": "Windows 10",
                    "action": "start",
                    "date_actioned": 700
                },
            ]
        )

        users = get_users(self.actions, "start", 700, 900)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)

    def test_get_playback_time_with_additional_time_sequence(self):
        actions = self.actions
        actions.extend(
            [
                {
                    "user_id": 1,
                    "device": "Windows 10",
                    "action": "start",
                    "date_actioned": 500
                },
                {
                    "user_id": 1,
                    "device": "Windows 10",
                    "action": "stop",
                    "date_actioned": 600
                },
            ]
        )

        playback_time = get_playback_time(1, actions)

        self.assertEqual(playback_time, 410)

    def test_user_features_per_app_another_user(self):
        permissions = list()
        application_permissions_output = user_features_per_app(2, self.user_apps, self.app_features, self.user_features)

        for permission in application_permissions_output["application_permissions"]:
            permissions.extend(permission["features_allowed"])

        for permission in permissions:
            self.assertIn(
                permission,
                next(filter(lambda x: x["user_id"] == 2, self.user_features))["features_allowed"]
            )

