from fake_db import Db


def _check_action(action):
    if action not in ["start", "stop"]:
        raise BaseException("Action must be string with value start or stop")  # raise exception if action is not valid


def get_users(records: list, action: str, start: int, stop: int) -> list:
    """
    This function returns list of user id matching query. Users are
    filtered by start or stop time depends on action
    """

    _check_action(action)

    return list(  # use set to make user id unique
        set(
            x.get("user_id") for x in
            filter(
                lambda r: start == r["date_actioned"] and r["action"] == "start" if action == "start" else stop == r["date_actioned"] and r["action"] == "stop",
                records
            )
        )
    )


class TimeSequence:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        self.finished = False

    def duration(self):
        return self.stop - self.start


def get_playback_time(user_id: int, records: list) -> int:
    """ This functions returns playback time for user on all devices """
    user_records = filter(lambda r: r["user_id"] == user_id, records)

    starts_per_device = dict()
    time_sequences = list()  # unique time sequences
    sum_time = 0

    for record in user_records:
        _check_action(record["action"])

        if record["action"] == "start":
            starts_per_device[record["device"]] = record["date_actioned"]

            if len(time_sequences) == 0:  # set start for first time sequence
                time_sequences.append(TimeSequence(record["date_actioned"], record["date_actioned"]))
            elif time_sequences[-1].finished:
                time_sequences.append(TimeSequence(record["date_actioned"], record["date_actioned"]))

        else:
            if not record["device"] in starts_per_device:
                raise BaseException("Tried to stop device wich is not started")

            time_sequences[-1].stop = record["date_actioned"]
            del starts_per_device[record["device"]]

            if len(starts_per_device.keys()) == 0:
                time_sequences[-1].finished = True

    for sequence in list(filter(lambda x: x.finished, time_sequences)):
        sum_time += sequence.duration()

    return sum_time


def user_features_per_app(
        user_id: int,
        user_apps_relation: list,
        app_features_relation: list,
        user_features_relation: list
) -> dict:
    """
    Function that returns a dictionary object which shows,
    for all allowed applications, the allowed features for a user.
    """

    application_permissions = list()

    user_allowed_features = next(filter(lambda x: x["user_id"] == user_id, user_features_relation))["features_allowed"]

    for app in user_apps_relation:
        current_app_features = list(filter(lambda x: x["app_id"] == app["app_id"], app_features_relation))

        if len(current_app_features):
            current_app_features = current_app_features[0]
            current_app_features['features_allowed'] = \
                list(filter(lambda x: x in user_allowed_features, current_app_features['features_available']))

            del current_app_features["features_available"]

            application_permissions.append(current_app_features)

    return {
        "user_id": user_id,
        "application_permissions": application_permissions
    }


if __name__ == '__main__':
    db = Db()
    data = db.data()  # get data from fake db
    actions = data["actions"]
    user_apps = data["user_apps"]
    app_features = data["app_features"]
    user_features = data["user_features"]

    users = get_users(actions, "start", 700, 900)
    print(users)

    playback_time = get_playback_time(1, actions)
    print(playback_time)

    application_permissions_output = user_features_per_app(1, user_apps, app_features, user_features)
    print(application_permissions_output)
