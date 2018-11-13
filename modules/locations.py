

class Location:
    """
    Class defining an individual location.
    """
    def __init__(self, records):
        self.records = records
        self.original = records.ORIGINAL.any()
        self.start = records.START.min()
        self.end = records.END.max()
        self.active = (records.STATUS == 'ACTIVE').any()
        self.continuous = records.CONTINUOUS.any()
        self.lifespan = records.LIFESPAN.max()
        self.codes = tuple(records.CODE.unique())
        self.activities = records.ACTIVITY_ID.sum()
        self.num_licenses = len(records)

    def aggregate(self):

        # extract nominal properties
        nominal = ['ACCOUNT_ID', 'SITE_ID']
        adict = self.records.iloc[0][nominal].to_dict()

        # append aggregate properties
        properties = dict(
            ORIGINAL=self.original,
            START=self.start,
            END=self.end,
            ACTIVE=self.active,
            CONTINUOUS=self.continuous,
            LIFESPAN=self.lifespan,
            CODES=self.codes,
            ACTIVITIES=self.activities,
            NUM_LICENSES=self.num_licenses)

        adict.update(properties)

        return adict
