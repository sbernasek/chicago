from os.path import join
import pandas as pd
import re
import geopandas as gpd


zip_pattern = re.compile('\d{5}')
def format_zip(zipstr):
    """ Format zipcode string. """
    matches = zip_pattern.findall(zipstr)
    if len(matches) >= 1:
        return int(matches[0])
    else:
        return -1


def format_datestr(datestr):
    if type(datestr) == str:
        return pd.datetime.strptime(datestr, '%m/%d/%Y')
    else:
        return None


class LicensingData:
    """
    Class for preprocessing business licensing data.
    """

    def __init__(self,
                 datadir = './chicago',
                 licensing_file='licensing.csv',
                 geo_file='chicago_zips.geojson'):

        self.geo = gpd.read_file(join(datadir, geo_file))
        self.geo.zip = self.geo.zip.astype(int)
        self.df = self.preprocess(self.read(join(datadir, licensing_file)))

    @staticmethod
    def read(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            df = pd.read_csv(file, dtype=dtypes)
        return df

    def preprocess(self, df):
        """ Process data. """

        # limit to IL and zip codes beginning with '6'
        #df = df[df['STATE']=='IL']
        #df = df[df['ZIP CODE'].apply(lambda x: str(x)[0]=='6')]

        # exclude licenses without zip codes
        df = df[~df['ZIP CODE'].isna()]
        df.loc[:, 'ZIP CODE'] = df['ZIP CODE'].apply(format_zip)

        # limit to zipcodes within chicago city limits
        cityzips = self.geo.zip.unique()
        df = df[df['ZIP CODE'].isin(cityzips)]

        # format datestrings
        for DATEVAR in DATEVARS:
            df.loc[:, DATEVAR] = df[DATEVAR].apply(format_datestr)

        # sort by application date
        df = df.sort_values(by='DATE ISSUED')

        return df

    @staticmethod
    def load(src='./chicago/licensing.hdf'):
        """ Load preprocessed license data from <src>. """
        df = pd.read_hdf(src, 'licenses')
        return df

    def save(self, dst='./chicago/licensing.hdf'):
        """ Save licensing data to <dst>. """
        self.df.to_hdf(dst, 'licenses', mode='w')


DATEVARS = [
    'APPLICATION CREATED DATE',
    'APPLICATION REQUIREMENTS COMPLETE',
    'PAYMENT DATE',
    'LICENSE TERM START DATE',
    'LICENSE TERM EXPIRATION DATE',
    'LICENSE APPROVED FOR ISSUANCE',
    'DATE ISSUED',
    'LICENSE STATUS CHANGE DATE']

dtypes = {
    'ID': str,
    'LICENSE ID': int,
    'ACCOUNT NUMBER': int,
    'SITE NUMBER': int,
    'LEGAL NAME': str,
    'DOING BUSINESS AS NAME': str,
    'ADDRESS': str,
    'CITY': str,
    'STATE': str,
    'ZIP CODE': str,
    'WARD': float,
    'PRECINCT': float,
    'WARD PRECINCT': str,
    'POLICE DISTRICT': str,
    'LICENSE CODE': int,
    'LICENSE DESCRIPTION': str,
    'BUSINESS ACTIVITY ID': str,
    'BUSINESS ACTIVITY': str,
    'LICENSE NUMBER': float,
    'APPLICATION TYPE': str,
    'APPLICATION CREATED DATE': str,
    'APPLICATION REQUIREMENTS COMPLETE': str,
    'PAYMENT DATE': str,
    'CONDITIONAL APPROVAL': str,
    'LICENSE TERM START DATE': str,
    'LICENSE TERM EXPIRATION DATE': str,
    'LICENSE APPROVED FOR ISSUANCE': str,
    'DATE ISSUED': str,
    'LICENSE STATUS': str,
    'LICENSE STATUS CHANGE DATE': str,
    'SSA': float,
    'LATITUDE': float,
    'LONGITUDE': float,
    'LOCATION': str
}
