from pymongo import MongoClient


class SaverClient:
    """MongoDB saver client

    A Client that saves data to MongoDB instances

    Args:
        host (:obj:`str`): Hostname of the MongoDB server
        port (:obj:`int`): Port of the MongoDB server
    """
    def __init__(self, host, port):
        self.client = MongoClient(host=host, port=port)
        self.db = self.client.hivemind
        self.users = self.db.users

    def save(self, field, data):
        """Saves data (user info, snapshots) to the appropriate field

        Data generally looks like this:
            {'user': {...},
             'snapshot': {...}}

        Args:
            field (:obj:`str`): Field name the data is related to
            data (:obj:`dict`): BSON dictionary of the data
        """
        user = data['user'].copy()
        user['snapshots'] = []
        snapshot = data['snapshot']

        # Insert user in case it doesn't exist
        self.users.update_one({'uid': user['uid']}, {'$setOnInsert': user}, upsert=True)

        # Insert snapshot in case it doesn't exist
        result = self.users.update_one({'uid': user['uid'], 'snapshots.timestamp_ms': {'$ne': snapshot['timestamp_ms']}},
                                       {'$push': {'snapshots': snapshot}})

        # Update snapshot if it exists
        if result.matched_count == 0:
            self.users.update_one(
                {'uid': user['uid'], 'snapshots.timestamp_ms': {'$eq': snapshot['timestamp_ms']}},
                {'$set': {f'snapshots.$.{field}': snapshot[field]}})


class APIClient:
    """MongoDB API client

    A Client exposes the MongoDB user-snapshot collection

    Args:
        host (:obj:`str`): Hostname of the MongoDB server
        port (:obj:`int`): Port of the MongoDB server
    """

    def __init__(self, host, port):
        self.client = MongoClient(host=host, port=port)
        self.db = self.client.hivemind
        self.users = self.db.users

    def get_users(self):
        """Returns a list of <id,name> of all the users in the DB

        Returns:
            :obj:`list`: List of user dictionaries {'uid': val, 'name': val}
        """
        result = self.users.find(projection={'_id': False, 'uid': True, 'name': True})
        users = list(result)
        return users

    def get_user(self, user_id):
        """Returns the specified user information

        The information includes: UserID, name, date of birth, gender

        Args:
            user_id (:obj:`int`): id of the requested user
        Returns:
            :obj:`dict`: A User dictionary with the keys <uid, name, birthday, gender>
        """
        user = self.users.find_one(filter={'uid': user_id},
                                   projection={'_id': False, 'snapshots': False})
        return user

    def get_user_snapshots(self, user_id):
        """Returns a list of the specified user snapshots information

        The information includes: snapshot id, timestamp

        Args:
            user_id (:obj:`int`): id of the requested user
        Returns:
            :obj:`list`: List of user snapshots {'id': val, 'datetime': val}
        """
        result = self.users.aggregate([{'$match': {'uid': user_id}},
                                       {'$project': {'_id': False, 'datetime': {'$map': {'input': '$snapshots', 'as': 's', 'in': '$$s.timestamp_ms'}}}}
                                       ])
        ss_date = result.next()
        snapshots = [{'id': i, 'datetime': date} for i, date in enumerate(ss_date['datetime'])]
        return snapshots

    def get_user_snapshot(self, user_id, ss_id):
        """Returns a specific snapshot of a specific user

        The snapshot returned includes its id, timestamp and available fields.

        Args:
            user_id (:obj:`int`): id of the requested user
            ss_id (:obj:`int`): id of the requested snapshot
        Returns:
            :obj:`dict`: Snapshot dictionary
        """
        result = self.users.aggregate([{'$match': {'uid': user_id}},
                                       {'$project': {'_id': False, 'snapshot': {'$arrayElemAt': ['$snapshots', ss_id]}}}
                                       ])
        snapshot = result.next()['snapshot']
        snapshot_details = {'ss_id': ss_id,
                            'datetime': snapshot.pop('timestamp_ms'),
                            'fields': list(snapshot.keys())}
        return snapshot_details

    def get_user_snapshot_field(self, user_id, ss_id, field):
        """Returns a specific snapshot field value

        Args:
            user_id (:obj:`int`): id of the requested user
            ss_id (:obj:`int`): id of the requested snapshot
            field (:obj:`str`): name of the requested field
        Returns:
            :obj:`dict`: Snapshot field result
        """
        result = self.users.aggregate([{'$match': {'uid': user_id}},
                                       {'$project': {'_id': False, 'snapshot': {'$arrayElemAt': ['$snapshots', ss_id]}}},
                                       {'$project': {'field': f'$snapshot.{field}'}}
                                       ])
        result = result.next()['field']
        return result

    def get_user_snapshot_field_data(self, user_id, ss_id, field):
        result = self.get_user_snapshot_field(user_id, ss_id, field)
        with open(result[field], 'rb') as fd:
            data = fd.read()
        return data

