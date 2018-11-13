import numpy as np
import pandas as pd
import quandl


MY_API_KEY = "DQS8Touz-5JVz9pdSxhf"


class ZillowAPI:
    """
    Interface to Zillow API.
    """

    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        quandl.ApiConfig.api_key = API_KEY

    def query(self, zipcode, indicator):
        """ Query Quandl portal to Zillow API for <area> and <indicator>. """
        return quandl.get('ZILLOW/Z{:d}_{:s}'.format(zipcode, indicator), returns="pandas")

    def query_MVALFAH(self, zipcode):
        """ Query median value per square foot for all houses in <zipcode>. """
        return self.query(zipcode, 'MVALFAH')


class RealEstateData:
    """ Interface to real estate value data. """

    def __init__(self, path='../data/processed/realestate.hdf'):
        self.path = path

        # load keys
        with pd.HDFStore(path=self.path, mode='r') as hdf:
            keys = hdf.keys()

        f = lambda x: int(x.lstrip('/Z'))
        self.zipcodes = np.array([f(k) for k in keys if k[1]=='Z'], dtype=int)

    def __getitem__(self, zipcode):
        return self.load(zipcode)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.num_zipcodes:
            timeseries = self.load(self.zipcodes[self.n])
            self.n += 1
            return timeseries
        else:
            raise StopIteration

    @property
    def num_zipcodes(self):
        return len(self.zipcodes)

    @property
    def missing(self):
        """ Zipcodes for which data were unavailable. """
        with pd.HDFStore(path=self.path, mode='r') as hdf:
            failures = hdf.get('failed')
        return failures

    def load(self, zipcode):
        """ Load market timeseries for <zipcode> from file. """
        with pd.HDFStore(path=self.path, mode='r') as hdf:
            timeseries = hdf.get('Z{:d}'.format(zipcode))
        return timeseries

    @staticmethod
    def download(zipcodes, destination='../data/processed/realestate.hdf'):
        """
        Query real estate value data from Zillow API and save to file.
        """

        # open API interface
        zillow = ZillowAPI(MY_API_KEY)
        failed = []
        with pd.HDFStore(path=destination, mode='a') as hdf:

            # query each zipcode (store failures)
            for i, zc in enumerate(zipcodes):
                try:
                    houseprices = zillow.query_MVALFAH(zc)

                    # skip entries with zero values
                    if (houseprices.values == 0).sum() > 0:
                        failed.append(zc)
                        continue

                    # add zipcode to key
                    houseprices.rename({'Value': zc}, axis=1, inplace=True)

                    # store as hdf5
                    hdf.put('Z{:d}'.format(zc), houseprices, format='fixed')

                except:
                    failed.append(zc)

                if i % 25 == 0:
                    print('{:0.2%} complete'.format(i/zipcodes.size))
