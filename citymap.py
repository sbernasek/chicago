from os.path import join
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase
from matplotlib.dates import YearLocator, DateFormatter
from matplotlib.animation import FuncAnimation


class CityMap:

    def __init__(self,
                 timeseries,
                 dirpath='./chicago/',
                 cbar=True,
                 timeline=True,
                 figsize=(6, 6),
                 cmap=None,
                 vmin=-1,
                 vmax=1,
                 label=None,
                 bg='w',
                 **kwargs):

        self.cbar = cbar
        self.timeline = timeline

        # load geomap
        self.citylimits = gpd.read_file(join(dirpath, 'chicago.geojson'))
        self.ziplimits = gpd.read_file(join(dirpath, 'chicago_zips.geojson'))
        self.ziplimits.zip = self.ziplimits.zip.astype(int)

        # add timeseries (smoothed)
        self.timeseries = timeseries.resample('1M', axis=0).interpolate().transpose()

        # set colormap
        if cmap is None:
            cmap = plt.cm.Blues
        cmap.set_bad(bg)
        self.cmap = cmap
        if vmin == 'min':
            vmin = self.timeseries.min().min()
        if vmax == 'max':
            vmax = self.timeseries.max().max()
        self.norm = Normalize(vmin=vmin, vmax=vmax)

        # create figure and plot city limits
        self.create_figure(figsize=figsize, cbar=cbar, timeline=timeline)
        #self.initialize_city_limits(**kwargs)
        self.initialize_zip_codes(**kwargs)

        # add colorbar
        if self.cbar:
            self.draw_colorbar(cmap, vmin, vmax, label=label)

        # add timeline
        if self.timeline:
            self.draw_timeline()

    @property
    def zipcodes(self):
        """ Unique zipcodes. """
        return self.ziplimits.zip.unique().astype(int)

    @property
    def num_frames(self):
        return self.timeseries.shape[1]

    @property
    def ax(self):
        return self.fig.axes[self.map_ax_ind]

    @property
    def cax(self):
        return self.fig.axes[self.cbar_ax_ind]

    @property
    def tax(self):
        return self.fig.axes[self.timeline_ax_ind]

    def create_figure(self, figsize=(4, 4), cbar=True, timeline=True):
        """ Create figure. """
        self.fig = plt.figure(figsize=figsize)

        gs = GridSpec(nrows=3, ncols=3, height_ratios=(1,25,3), width_ratios=[1,2,1])
        gs.update(wspace=0., hspace=0)

        lb = 0

        if cbar:
            self.cbar_ax_ind = len(self.fig.axes)
            self.fig.add_subplot(gs[0, 1])
            lb += 1

        if timeline:
            self.timeline_ax_ind = len(self.fig.axes)
            self.fig.add_subplot(gs[-1, :])

            # add map axis
            self.fig.add_subplot(gs[lb:-1, :])
        else:
            self.fig.add_subplot(gs[lb:, :])

        self.map_ax_ind = len(self.fig.axes) - 1

        # turn off axes
        self.ax.axis('off')
        self.ax.set_aspect(1)

    def draw_timeline(self):
        self.tax.set_yticks([])
        self.tax.spines['top'].set_visible(False)
        self.tax.spines['left'].set_visible(False)
        self.tax.spines['right'].set_visible(False)

        start = self.timeseries.columns.min()
        stop = self.timeseries.columns.max()
        self.tax.plot((start, stop), (0,0), alpha=0)

        self.tax.get_xaxis().set_major_locator(YearLocator(1, month=3))
        self.tax.get_xaxis().set_major_formatter(DateFormatter("%Y"))
        self.tax.xaxis.set_tick_params(rotation=45)
        self.tax.tick_params(pad=0, length=0)
        self.tax.set_ylim(0, 1)

    def draw_colorbar(self, cmap, vmin, vmax, label=None):
        norm = Normalize(vmin=vmin, vmax=vmax)
        cbar = ColorbarBase(self.cax, cmap=cmap, norm=norm, orientation='horizontal')
        cbar.set_ticks([])
        cbar.set_label(label)
        cbar.ax.xaxis.set_label_position('top')

    def initialize_city_limits(self, color='w', edgecolor='k', lw=.5, **kwargs):
        """ Add city limits to axes. """
        self.citylimits.plot(ax=self.ax, color=color, edgecolor=edgecolor, lw=lw, **kwargs)

    def initialize_zip_codes(self, **kwargs):
        """ Add zipcodes to axes. """

        # build shader
        shader = self.build_shader(0)

        # shade zipcode polygons
        shader.plot(column='VALUE', cmap=plt.cm.Greys, vmin=0, vmax=0, ax=self.ax, **kwargs)
        self.shade(0)

        # set date marker
        if self.timeline:
            self.tax.plot(self.timeseries.columns[0], .5, '.k', markersize=10)

    def build_shader(self, index):

        # get color vector
        colors = self.timeseries.iloc[:, index].rename('VALUE')

        # join with zipdata
        shader = self.ziplimits.join(colors, on='zip', how='left')

        return shader

    def shade(self, index):

        # build shader
        shader = self.build_shader(index)

        # shade zipcodes
        colors = self.cmap(np.ma.masked_invalid(self.norm(shader.VALUE.values)))
        self.ax.collections[-1].set_facecolors(colors)

    def set_title(self, index):
        date = self.timeseries.columns[index].strftime('%b-%Y')
        self.ax.set_title(date)

    def update(self, index):
        self.shade(index)
        if self.timeline:
            self.mark_time(index)

    def mark_time(self, index):
        date = self.timeseries.columns[index]
        self.tax.lines[0].set_data(date, 0.5)

    def fix_date(self, date):
        index = self.timeseries.columns.get_loc(date).start
        self.update(index)

    def animate(self, filepath, fps=12, dpi=150):
        vid = FuncAnimation(self.fig, self.update, frames=np.arange(self.num_frames))
        vid.save(filepath, fps=fps, dpi=dpi)
