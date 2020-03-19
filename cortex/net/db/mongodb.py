from pymongo import MongoClient


# TODO: Add documentation on how to add support for new databases
# TODO: Document how the database looks like
class SaverClient:
    def __init__(self, host, port):
        self.client = MongoClient(host=host, port=port)
        self.db = self.client.hivemind
        self.users = self.db.users

    def save(self, field, data):
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
    def __init__(self, host, port):
        self.client = MongoClient(host=host, port=port)
        self.db = self.client.hivemind
        self.users = self.db.users

    # TODO: Add result validation
    def get_users(self):
        result = self.users.find(projection={'_id': False, 'uid': True, 'name': True})
        users = list(result)
        return users

    def get_user(self, user_id):
        user = self.users.find_one(filter={'uid': user_id},
                                   projection={'_id': False, 'snapshots': False})
        return user

    def get_user_snapshots(self, user_id):
        result = self.users.aggregate([{'$match': {'uid': user_id}},
                                       {'$project': {'_id': False, 'datetime': {'$map': {'input': '$snapshots', 'as': 's', 'in': '$$s.timestamp_ms'}}}}
                                       ])
        ss_date = result.next()
        snapshots = [{'id': i, 'datetime': date} for i, date in enumerate(ss_date['datetime'])]
        return snapshots

    def get_user_snapshot(self, user_id, ss_id):
        result = self.users.aggregate([{'$match': {'uid': user_id}},
                                       {'$project': {'_id': False, 'snapshot': {'$arrayElemAt': ['$snapshots', ss_id]}}}
                                       ])
        snapshot = result.next()['snapshot']
        snapshot_details = {'ss_id': ss_id,
                            'datetime': snapshot.pop('timestamp_ms'),
                            'fields': list(snapshot.keys())}
        return snapshot_details

    def get_user_snapshot_field(self, user_id, ss_id, field):
        result = self.users.aggregate([{'$match': {'uid': user_id}},
                                       {'$project': {'_id': False, 'snapshot': {'$arrayElemAt': ['$snapshots', ss_id]}}},
                                       {'$project': {'field': f'$snapshot.{field}'}}
                                       ])
        # TODO: Handle error if field not found
        result = result.next()['field']
        return result

    def get_user_snapshot_field_data(self, user_id, ss_id, field):
        result = self.get_user_snapshot_field(user_id, ss_id, field)
        with open(result[field], 'rb') as fd:
            data = fd.read()
        return data

