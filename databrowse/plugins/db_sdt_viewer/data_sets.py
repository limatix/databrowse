import os
import subprocess
from multiprocessing import Process
from packaging import version
import matplotlib
from matplotlib import animation
BACKEND = 'Agg'
if matplotlib.get_backend().lower() != BACKEND.lower():
    matplotlib.use(BACKEND)
import matplotlib.pyplot as plt


def save_animation(filepath, shp, ds, color):
    print("Starting to generate %s" % filepath)
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ims = []
    print("Generating images.")
    for i in range(0, shp[2]):
        ttl = plt.text(0.5, 1.01, "Depth: %s" % i, horizontalalignment='center', verticalalignment='bottom', transform=ax.transAxes)
        im = plt.imshow(ds['v'][:, :, i], animated=True, cmap=color)
        plt.xlabel("x")
        plt.ylabel("y")
        ims.append([im, ttl])
    print("Generating animation.")
    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True)

    print("Saving animation. Please wait to close this window until saving is completed.")
    ani.save(filepath, writer='imagemagick')
    print("%s is done being generated. Please refresh." % filepath)
    return 0


class SDTDataSets:

    def __init__(self, parent):
        self.parent = parent
        self.contenttype = None
        self.size = None
        self.ext = None
        self.shp = None
        self.ds = None
        self.pd = None
        self.vunits = None
        self.fprefix = None
        self.paramdict = None
        self.color = None

        self.check_preexisting()
        if self.size is None:
            plt.figure()
            self.gen_images()
        plt.close("all")

    def load(self):
        ft = self.parent.getCacheFileHandler('rb', self.fprefix, self.ext)
        return ft

    def save(self):
        ft = self.parent.getCacheFileHandler('wb', self.fprefix, self.ext)
        plt.savefig(ft)
        ft.close()
        plt.clf()

    def check_preexisting(self):
        if 'color' not in self.parent._web_support.req.form:
            self.color = 'binary'
        else:
            self.color = self.parent._web_support.req.form['color'].value

        if "frame" in self.parent._web_support.req.form:
            fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) + "_Frame" + str(
                self.parent._web_support.req.form['frame'].value) + "_" + self.color
            if self.parent.CacheFileExists(fprefix, 'png'):
                contenttype = 'image/png'
                size = os.path.getsize(self.parent.getCacheFileName(fprefix, 'png'))
                ext = 'png'
            else:
                contenttype = None
                size = None
                ext = None
        else:
            fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) + "_" + self.color
            if self.parent.CacheFileExists(fprefix, 'png'):
                contenttype = 'image/png'
                size = os.path.getsize(self.parent.getCacheFileName(fprefix, 'png'))
                ext = 'png'
            elif self.parent.CacheFileExists(fprefix, 'gif') and os.path.getsize(self.parent.getCacheFileName(fprefix, 'gif')) > 0:
                contenttype = 'image/gif'
                size = os.path.getsize(self.parent.getCacheFileName(fprefix, 'gif'))
                ext = 'gif'
            else:
                contenttype = None
                size = None
                ext = None
        self.fprefix = fprefix
        self.contenttype = contenttype
        self.size = size
        self.ext = ext

    def gen_images(self):
        g = open(self.parent._fullpath)
        self.paramdict, datasets, xmltree = self.parent.parse_sdt(g)
        g.close()

        dsetname = self.parent._web_support.req.form['dataset'].value

        if dsetname not in datasets:
            raise self.parent.RendererException("Dataset '%s' Not Found" % dsetname)

        self.ds = datasets[dsetname]

        self.shp = self.ds['v'].shape

        for i in self.paramdict:
            if i.startswith('-- Data Subset'):
                if self.paramdict[i]['Subset Label'] == dsetname:
                    self.pd = self.paramdict[i]
                    pass
                pass
            pass

        if self.pd is None:
            raise self.parent.RendererException("Unable to locate '%s' in Parameter List" % dsetname)

        vmin = float(self.pd['Measurement Range'].split()[0])
        vmax = float(self.pd['Measurement Range'].split()[1]) + vmin
        try:
            self.vunits = self.pd['Measurement Range'].split()[2]
        except:
            self.vunits = "unitless"

        if len(self.shp) == 4:
            # Ray data
            if self.shp[0] > 1 and self.shp[1] > 1 and self.shp[2] > 1 and self.shp[3] > 1:
                # x, y, z, t
                pass
            else:
                self.parent.RendererException("Unknown plot type of shape 4.")
        elif len(self.shp) == 3:
            # Ascan
            if self.shp[0] == 1 and self.shp[1] == 1 and self.shp[2] > 1:
                self.ascan()
                pass
            # Bscan
            elif self.shp[0] > 1 and self.shp[1] == 1 and self.shp[2] > 1:
                self.bscan_1()
                pass
            # Bscan
            elif self.shp[1] > 1 and self.shp[0] == 1 and self.shp[2] > 1:
                self.bscan_2()
                pass
            # Gated CScan Output - i.e. Both Positions And No Time
            elif self.shp[0] > 1 and self.shp[1] > 1 and self.shp[2] == 1:
                self.gated_cscan()
                pass
            # CScan
            elif self.shp[0] > 1 and self.shp[1] > 1 and self.shp[2] > 1:
                self.cscan()
                pass
            else:
                self.parent.RendererException("Unknown plot type of shape 3.")
            pass
        else:
            self.parent.RendererException("Unknown plot type.")

    # Scan methods:
    def ascan(self):
        plt.plot(self.ds['t'], self.ds['v'][0, 0, :])
        plt.xlabel('Time, t (%s)' % (self.parent.check_units(self.pd['Sample Resolution'])[1]))
        plt.ylabel('Amplitude (%s)' % (self.vunits))

        self.fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) + "_" + self.color
        self.ext = "png"
        self.contenttype = 'image/png'
        self.save()
        self.size = os.path.getsize(self.parent.getCacheFileName(self.fprefix, self.ext))

    def bscan_1(self):
        # Beware - this one probably doesn't work
        # Also, this situation probably doesn't actually happen
        plt.imshow(self.ds['v'][:, 0, :], cmap=self.color,
                   origin='lower', extent=[self.ds['x'][0],
                                           self.ds['x'][-1],
                                           self.ds['t'][0],
                                           self.ds['t'][-1]])
        axis = 'Axis 1'
        aunits = 'None'
        for i in self.paramdict:
            if i.startswith('--- First Axis ---'):
                axis = i[i.find('(') + 1:i.find(')')]
                aunits = self.parent.check_units(self.paramdict[i]['Sample Resolution'])[1]
                pass
            pass
        plt.xlabel('Position, %s (%s)' % (axis, aunits))
        plt.ylabel('Time, t (%s)' % (self.parent.check_units(self.pd['Sample Resolution'])[1]))
        cb = plt.colorbar()
        cb.set_label('Amplitude (%s)' % self.vunits)

        self.fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) + "_" + self.color
        self.ext = "png"
        self.contenttype = 'image/png'
        self.save()
        self.size = os.path.getsize(self.parent.getCacheFileName(self.fprefix, self.ext))

    def bscan_2(self):
        plt.imshow(self.ds['v'][0, :, :], cmap=self.color,
                   origin='lower', extent=[self.ds['y'][0],
                                           self.ds['y'][-1],
                                           self.ds['t'][0],
                                           self.ds['t'][-1]])
        axis = 'Axis 2'
        aunits = 'None'
        for i in self.paramdict:
            if i.startswith('--- Second Axis ---'):
                axis = i[i.find('(') + 1:i.find(')')]
                aunits = self.parent.check_units(self.paramdict[i]['Sample Resolution'])[1]
                pass
            pass
        plt.xlabel('Position, %s (%s)' % (axis, aunits))
        plt.ylabel('Time, t (%s)' % (self.parent.check_units(self.pd['Sample Resolution'])[1]))
        cb = plt.colorbar()
        cb.set_label('Amplitude (%s)' % self.vunits)

        self.fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) + "_" + self.color
        self.ext = "png"
        self.contenttype = 'image/png'
        self.save()
        self.size = os.path.getsize(self.parent.getCacheFileName(self.fprefix, self.ext))

    def gated_cscan(self):
        plt.imshow(self.ds['v'][:, :, 0], cmap=self.color,
                   origin='lower', extent=[self.ds['x'][0],
                                           self.ds['x'][-1],
                                           self.ds['y'][0],
                                           self.ds['y'][-1]])
        axis1 = 'Axis 1'
        a1units = 'None'
        axis2 = 'Axis 2'
        a2units = 'None'
        for i in self.paramdict:
            if i.startswith('--- First Axis ---'):
                axis1 = i[i.find('(') + 1:i.find(')')]
                a1units = self.parent.check_units(self.paramdict[i]['Sample Resolution'])[1]
                pass
            elif i.startswith('--- Second Axis ---'):
                axis2 = i[i.find('(') + 1:i.find(')')]
                a2units = self.parent.check_units(self.paramdict[i]['Sample Resolution'])[1]
                pass
            pass
        plt.xlabel('Position, %s (%s)' % (axis1, a1units))
        plt.ylabel('Position, %s (%s)' % (axis2, a2units))
        cb = plt.colorbar()
        cb.set_label('Amplitude, (%s)' % self.vunits)

        self.fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) + "_" + self.color
        self.ext = "png"
        self.contenttype = 'image/png'
        self.save()
        self.size = os.path.getsize(self.parent.getCacheFileName(self.fprefix, self.ext))

    def cscan(self):
        if "frame" not in self.parent._web_support.req.form:
            frame = self.ds['v'].max(0).max(0).argmax()
        else:
            frame = int(self.parent._web_support.req.form['frame'].value)

        plt.imshow(self.ds['v'][:, :, frame], cmap=self.color,
                   origin='lower', extent=[self.ds['x'][0],
                                           self.ds['x'][-1],
                                           self.ds['y'][0],
                                           self.ds['y'][-1]])
        axis1 = 'Axis 1'
        a1units = 'None'
        axis2 = 'Axis 2'
        a2units = 'None'
        for i in self.paramdict:
            if i.startswith('--- First Axis ---'):
                axis1 = i[i.find('(') + 1:i.find(')')]
                a1units = self.parent.check_units(self.paramdict[i]['Sample Resolution'])[1]
                pass
            elif i.startswith('--- Second Axis ---'):
                axis2 = i[i.find('(') + 1:i.find(')')]
                a2units = self.parent.check_units(self.paramdict[i]['Sample Resolution'])[1]
                pass
            pass
        plt.xlabel('Position, %s (%s)' % (axis1, a1units))
        plt.ylabel('Position, %s (%s)' % (axis2, a2units))
        cb = plt.colorbar()
        cb.set_label('Amplitude (%s)' % self.vunits)
        plt.title('Time, t=%0.2f %s' % (self.ds['t'][frame],
                                        self.parent.check_units(self.pd['Sample Resolution'])[1]))
        self.fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value + "_Frame%d" % frame) +\
                       "_" + self.color
        self.ext = "png"
        self.contenttype = 'image/png'
        self.save()
        self.size = os.path.getsize(self.parent.getCacheFileName(self.fprefix, self.ext))

        # Experimental gif support
        try:
            if subprocess.call(["magick"], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT) == 0:
                if version.parse(matplotlib.__version__) > version.parse("2.0.0"):
                    fprefix = "Dataset_" + str(self.parent._web_support.req.form['dataset'].value) +\
                              "_" + self.color
                    ext = "gif"
                    if not self.parent.CacheFileExists(fprefix, ext) or os.path.getsize(self.parent.getCacheFileName(fprefix, ext)) == 0:
                        ft = self.parent.getCacheFileHandler('wb', fprefix, ext)
                        ft.close()
                        p = Process(target=save_animation, args=(self.parent.getCacheFileName(fprefix, ext), self.shp, self.ds, self.color))
                        p.daemon = False
                        p.start()
                else:
                    print("Warning: Matplotlib %s does not support gif functionality." % matplotlib.__version__)
            else:
                raise OSError
        except Exception as e:
            print("Warning: Imagemagick is not install or improperly configured. Gif support not available.")
            print(e)
