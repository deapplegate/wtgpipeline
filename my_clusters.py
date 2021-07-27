#! /usr/bin/env ipython
'''
this will load in info/data relevant for a specific cluster
'''
#adam-note# a derivative of adam_plot_radial_shear_profile.py
from readtxtfile import readtxtfile
import astropy
import astropy.io.fits
pyfits=astropy.io.fits
from astropy.io import ascii
import sys,os,re,string,time
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import ldac
import commands #commands.getoutput

sys.path.append('/u/ki/awright/quick/pythons')
import imagetools, cattools, pipelinetools
#
ns=globals()
#adam-useful# document this later, it's helpful!

myfgas_worklist = readtxtfile('/u/ki/awright/gravitas/maxlikelensing/FgasThesis_sample_mine.list')
myfgas_clusters = np.array([x[0] for x in myfgas_worklist])
myfgas_filters = np.array([x[1] for x in myfgas_worklist])
myfgas_lenses = np.array([x[2] for x in myfgas_worklist])
othersfgas_worklist = readtxtfile('/u/ki/awright/gravitas/maxlikelensing/FgasThesis_sample_not_mine.list')
othersfgas_clusters = np.array([x[0] for x in othersfgas_worklist])
othersfgas_filters = np.array([x[1] for x in othersfgas_worklist])
othersfgas_lenses = np.array([x[2] for x in othersfgas_worklist])
allfgas_clusters= np.append(myfgas_clusters, othersfgas_clusters)
allfgas_filters= np.append(myfgas_filters, othersfgas_filters)
allfgas_lenses= np.append(myfgas_lenses, othersfgas_lenses)

gpfsSUBARUDIR='/gpfs/slac/kipac/fs1/u/awright/SUBARU/'
ki05SUBARUDIR='/nfs/slac/g/ki/ki05/anja/SUBARU/'
ki18SUBARUDIR='/u/ki/awright/data/'

## define some things for making latex tables:

filter2tex={ 'W-J-B':'{\it B}$_{\rm J}$', 'W-J-V':'{\it V}$_{\rm J}$', 'W-C-RC':'{\it R}$_{\rm C}$', 'W-C-IC':'{\it I}$_{\rm C}$', 'W-S-I+':'{\it i}$^{+}$','W-S-Z+':'{\it z}$^{+}$'}
MegaPrime_filter2tex={ 'u':'{\it u}$^{\star}$', 'g':'{\it g}$^{\star}$', 'r':'{\it r}$^{\star}$', 'i':'{\it i}$^{\star}$', 'z':'{\it z}$^{\star}$'}
filters_BVRIZ=['W-J-B', 'W-J-V', 'W-C-RC', 'W-C-IC', 'W-S-I+', 'W-S-Z+']

my_clusters_ra_dec={
'Zw2089': ('9:00:36.882','+20:53:40.361'),
'MACS0429-02': ( '04:29:36.001', '-02:53:05.63' ),
'MACS1115+01': ( '11:15:51.881', '01:29:54.98' ),
'RXJ2129': ( '21:29:39.727', '00:05:18.15' )
}
cl_short2long_names={
## my clusters
"MACS1115+01": "MACSJ1115.8+0129",
"Zw2089":"Zw2089",
'RXJ2129':"RXJ2129.6+0005",
'MACS0429-02':"MACSJ0429.6-0253",
## fgas_others
"MACS1423+24":"MACSJ1423.8+2404",
"MACS1532+30":"RXJ1532.9+3021", #"MACSJ1532.8+3021",
"MACS1621+38":"MACSJ1621.3+3810",
"MACS1720+35":"MACSJ1720.2+3536",
"MACS2140-23":"MS2137.3-2353",
"MACS1347-11":"RXJ1347.5-1145"
}
#MACSJ2140.2-2339
#MACSJ1347.5-1144
##Post-thesis:
#MACS1427+44:"MACSJ1427.2+4407"
#a1835.lenkrb_auto_renew: Error checking etime (no ticket?)                                                                                                                                         
#a2204.lens
##megaprime only
#3C295
##missing bands
#MACS0159-08
#Zw2701

class my_cluster(object):
    try:
	''' get the properties of this cluster '''

	## here we define global files (lookup tables, for example) as Class Attributes (as opposed to instance attributes starting with self.)
	fl_redshift="/gpfs/slac/kipac/fs1/u/awright/SUBARU/clusters.redshifts"
	fl_lensmag='/u/ki/awright/gravitas/ldaclensing/lensing_coadd_type_filter.list'
	#dir_pzwork = gpfsSUBARUDIR + "/fgas_pz_masses/catalog_backup_thesis_2019-05-27/"
	dir_pzwork = '/gpfs/slac/kipac/fs1/u/awright/SUBARU/fgas_thesis_backup_catalogs_06-03-2019/'
	pixscale = 0.2

	## naming conventions:
	#dir_*    : directory name
	#fl_*     : filename
	#fo_*     : file object
	#cat_*    : catalog file object
	#clprop_* : cluster property
	#lensprop_* : lensing image header property

	def __init__(self,cluster,filter,lens,dir_pzwork=dir_pzwork):
		self.cluster = cluster
		self.filter = filter
		self.lens = lens
		self.props=dict(cluster = cluster,filter = filter,lens = lens,SUBARUDIR=gpfsSUBARUDIR,dir_pzwork=self.dir_pzwork)
		self.clquick='.'.join([cluster,filter,lens])  #tag='_old_unmatched'
		tag=''
		self.dir_cluster= "/%(SUBARUDIR)s/%(cluster)s/" % (self.props)
		self.adam=1
		if not os.path.isdir(self.dir_cluster):
			#if self.cluster in othersfgas_clusters:
			self.adam=0
			#adam-Warning# I think dir_pzwork will have to change: 
			self.props=dict(cluster = cluster,filter = filter,lens = lens,SUBARUDIR=ki05SUBARUDIR,dir_pzwork=self.dir_pzwork)
		self.dir_lens_coadd = "/%(SUBARUDIR)s/%(cluster)s/%(filter)s/SCIENCE/coadd_%(cluster)s_%(lens)s/" % (self.props)
		self.dir_photom = "/%(SUBARUDIR)s/%(cluster)s/PHOTOMETRY_%(filter)s_aper/" % (self.props)
		self.dir_lens = "/%(SUBARUDIR)s/%(cluster)s/LENSING_%(filter)s_%(filter)s_aper/%(lens)s/" % (self.props)
		assert(os.path.isdir(self.dir_photom))
		assert(os.path.isdir(self.dir_lens))

		self.fl_image_lens = "/%(SUBARUDIR)s/%(cluster)s/%(filter)s/SCIENCE/coadd_%(cluster)s_%(lens)s/coadd.fits" % (self.props)
		self.fo_image_lens = astropy.io.fits.open(self.fl_image_lens)[0]
		self.header_lens = self.fo_image_lens.header
		self.lensprop_exptime=self.header_lens['EXPTIME']
		self.lensprop_seeing=self.header_lens['SEEING']

		self.fl_cut_lensing = self.dir_lens + "cut_lensing.cat" +tag
		self.fl_cut_lensing_step = self.dir_lens + "cut_lensing.cat_step" +tag
		self.fl_prof = self.dir_lens + "%(cluster)s_rm1.5_ri0.75_ro3.0_c4.out.prof" % (self.props) +tag
		# '/u/ki/dapple/subaru/doug/publication/ccmass_2012-07-31'
		self.fl_mass = self.dir_lens + "%(cluster)s_rm1.5_ri0.75_ro3.0_c4.out" % (self.props) +tag
		if not self.adam:
			# use like compare_masses.readAnjaMasses('/u/ki/dapple/subaru/doug/publication/ccmass_2012-07-31/')
			self.fl_mass = "/u/ki/dapple/subaru/doug/publication/ccmass_2012-07-31/%(cluster)s.%(filter)s.%(lens)s.out" % (self.props) +tag

		## load in things from ~/gravitas/maxlikelensing/adam_outline.sh
		self.fl_cosmos_rscut = self.dir_lens + '/cosmos_rscut.cat'
		self.fl_cat_rs = self.dir_lens + "%(cluster)s_redsequence.cat" % (self.props) +tag
		self.fl_cat_lensbase = self.dir_lens + "coadd_photo.cat" +tag
		if self.adam:
			self.fl_photom  = self.dir_photom + "%(cluster)s.calibrated_PureStarCalib.cat" % (self.props)
			self.fl_photom_alter  = self.dir_photom + "%(cluster)s.calibrated_PureStarCalib.alter.cat" % (self.props)
		else:
			self.fl_photom  = self.dir_photom + "%(cluster)s.slr.cat" % (self.props)
			self.fl_photom_alter  = self.dir_photom + "%(cluster)s.slr.alter.cat" % (self.props)

		if self.adam:
			self.seeing_mean_rh_entry = commands.getoutput('grep "%(cluster)s" %(dir_pzwork)s/cluster.seeing.dat' % (self.props))
			self.seeing_mean_rh = float(self.seeing_mean_rh_entry.split(lens)[-1])
			self.seeing_mean_rh_arcsec = self.pixscale * (2.0 * self.seeing_mean_rh)
			self.fl_outputpdz= "%(dir_pzwork)s/%(cluster)s.%(filter)s.pdz.cat" % (self.props)
			self.fl_bpzcat= "%(dir_pzwork)s/%(cluster)s.%(filter)s.bpz.tab" % (self.props)

		# get lensing mag
		fo_lensmag=open(self.fl_lensmag)
		lensmag_lines=fo_lensmag.readlines()
		for line in lensmag_lines:
		    if line.startswith(self.cluster) and self.filter in line and self.lens in line:
			line=line.strip()
			lensmag=line.split(' ')[-1]
			if self.filter in lensmag:
				self.lensmag=lensmag.strip()
				break
			else:
				raise Exception('line with our self.cluster in '+self.fl_lensmag+' doesnt match expected format')
		####################################
		## get redshift
		####################################
		fo_redshift=open(self.fl_redshift)
		redshift_lines=fo_redshift.readlines()
		for zl in redshift_lines:
		    if zl.startswith(self.cluster):
			zline=zl.strip()
			znum=zline.split(' ')[-1]
			if imagetools.isfloat(znum):
				self.clprop_z=float(znum)
				break
			else:
				raise Exception('line with our self.cluster in '+self.fl_redshift+' doesnt match expected format')
		try:
			print self.cluster,'at redshift',self.clprop_z
			self.z_cluster=self.clprop_z #make it backwards compatible after name convention change
			fo_redshift.close()
		except:
			raise Exception('line with our self.cluster is missing from '+self.fl_redshift)

	## this gets the cut_lensing.cat file openned if it's needed
	def __getattr__(self,key):
		'''
		What can we do here is get the value when key doesn't already exist

		There are two attribute access methods in python classes: __getattribute__ and __getattr__. The first is called every time an attribute lookup is attempted, the second is called only when the normal attribute lookup system fails (including lookups in superclasses).
		'''

		print key
		if key=='_cat_lens':
			self.set_cat_lens()
			return self.get_cat_lens()

	def get_cat_lens(self):
		return self._cat_lens

	def set_cat_lens(self):
		print("opening "+self.fl_cut_lensing)
		self._cat_lens=ldac.openObjectFile(self.fl_cut_lensing)

	cat_lens = property(get_cat_lens,set_cat_lens)

	def get_cuts(self):
		print '''
		import apply_cuts
		mycuts=apply_cuts.ApplyCuts(cluster,filter,lens,workdir)
		datacuts=mycuts.dataCuts()
		photozcuts=mycuts.photozCuts()
		'''
	def get_latex_table_line(self):
		# Cluster & $z_{\rm Cl}$ & R.A. & Dec. & Filter Bands & Lensing Band  \\
		# & & (J2000) & (J2000) & & (exp. time [s], seeing [\arcsec])  \\
		cluster_line = cl_short2long_names[self.cluster]
		z_line = '%.3f' % (self.clprop_z)

		if self.adam:
			self.ra , self.dec = my_clusters_ra_dec[self.cluster]
			if not self.__dict__.has_key('k_bands'):
				self.get_best_mags()

			filters_line = ''.join([filter2tex[k_band] for k_band in self.k_bands])
			lens_filter = filter2tex[self.filter]
			lens_filter_line='%s (%s,%.2f)' % (lens_filter,int(self.lensprop_exptime),self.lensprop_seeing)
			cols=[cluster_line,z_line, self.ra , self.dec, filters_line, lens_filter_line]
			print repr(' & '.join(cols))
			#print self.cluster, ': seeing_mean_rh_arcsec=',self.seeing_mean_rh_arcsec, 'lensprop_seeing=',self.lensprop_seeing
			return cols
		else:
			oldline = commands.getoutput('grep "%s" doug_thesis_latex_table.tex' % (cluster_line))
			oldline2 = commands.getoutput('grep "%s" doug_fgas4_table.tex' % (cluster_line))
			cluster_nums_only=re.sub("\D", "", self.cluster)
			oldline3 = commands.getoutput('grep "%s" doug_fgas4_table.tex' % (cluster_nums_only))
			if oldline2:
				print oldline2
				return oldline2
			elif oldline:
				print oldline
				return oldline
			elif oldline3:
				print oldline3
				return oldline3

			else:
				print 'problem with cluster:',self.cluster,' cluster_line=',cluster_line
				return cluster_line

	def get_CCmass_props(self):
		'''
		get properties in the cc mass (aka ldaclensing/) script outputs
		'''
		#cattools.ldaccat_to_ds9(incat=self.cat_lens,outcat=self.fl_cut_lensing+'_ra_dec.tsv',keys=['ALPHA_J2000','DELTA_J2000'])

		#MACS1126: z=0.436

		####################################
		## get measurements from mass output file
		####################################
		fo_mass=open(self.fl_mass)
		self.mass_lines=fo_mass.readlines()
		for ml in self.mass_lines:
		    mline=ml.strip()
		    if mline.startswith('bootstrap median mass'):
			mnum=mline.split(': ')[-1]
			if imagetools.isfloat(mnum):
			    self.clprop_ccmass=float(mnum)
			else:
			    raise Exception('line with bootstrap median mass in it doesnt match needed format, it looks like this:\n'+ml)
		    #  Eventually do something that will get this:
		    #  '
		    #  'bootstrap 84th percentile: 1.338070e+15 (median +2.383156e+14)\n',
		    elif mline.startswith('bootstrap 16th percentile'):
			mnum_unit=mline.split(': ')[-1]
			mnum = mnum_unit.split(' (')[0]
			if imagetools.isfloat(mnum):
			    self.clprop_ccmass_errlow=float(mnum)
			else:
			    raise Exception('line with bootstrap 16th percentile in it doesnt match needed format, it looks like this:\n'+ml)
		    elif mline.startswith('bootstrap 84th percentile'):
			mnum_unit=mline.split(': ')[-1]
			mnum = mnum_unit.split(' (')[0]
			if imagetools.isfloat(mnum):
			    self.clprop_ccmass_errhigh = float(mnum)
			else:
			    raise Exception('line with bootstrap 84th percentile in it doesnt match needed format, it looks like this:\n'+ml)
		    elif mline.startswith('x_cluster'):
			mnum_unit=mline.split(': ')[-1]
			mnum = mnum_unit.split('[')[0]
			if imagetools.isfloat(mnum):
			    self.clprop_x_cluster=float(mnum)
			else:
			    raise Exception('line with x_cluster in it doesnt match needed format, it looks like this:\n'+ml)
		    elif mline.startswith('y_cluster'):
			mnum_unit=mline.split(': ')[-1]
			mnum = mnum_unit.split('[')[0]
			if imagetools.isfloat(mnum):
			    self.clprop_y_cluster=float(mnum)
			else:
			    raise Exception('line with y_cluster in it doesnt match needed format, it looks like this:\n'+ml)
		    elif 'r_s' in ml:
			mnum=mline.split(': ')[-1]
			if imagetools.isfloat(mnum):
				self.clprop_r_s=float(mnum)
			else:
				raise Exception('line with r_s in it doesnt match needed format, it looks like this:\n'+ml)
		    elif 'D_d' in ml:
			mnum=mline.split(': ')[-1]
			if imagetools.isfloat(mnum):
				self.clprop_D_d=float(mnum)
			else:
				raise Exception('line with D_d in it doesnt match needed format, it looks like this:\n'+ml)
		    elif 'beta_inf' in ml:
			mnum=mline.split(': ')[-1]
			if imagetools.isfloat(mnum):
				self.clprop_beta_inf=float(mnum)
			else:
				raise Exception('line with beta_inf in it doesnt match needed format, it looks like this:\n'+ml)
		    elif '<beta_s>' in ml:
			mnum=mline.split(': ')[-1]
			if imagetools.isfloat(mnum):
				self.clprop_beta_s=float(mnum)
			else:
				raise Exception('line with beta_s in it doesnt match needed format, it looks like this:\n'+ml)
		    elif '<beta_s^2>' in ml:
			mnum=mline.split(': ')[-1]
			if imagetools.isfloat(mnum):
				self.clprop_beta_s_sq=float(mnum)
			else:
				raise Exception('line with beta_s^2 in it doesnt match needed format, it looks like this:\n'+ml)

		try:
			print ' beta_inf=',self.clprop_beta_inf , ' <beta_s>=',self.clprop_beta_s , ' <beta_s^2>=',self.clprop_beta_s_sq ,' D_d=',self.clprop_D_d , ' r_s=',self.clprop_r_s
			self.beta_inf=self.clprop_beta_inf
			self.beta_s=self.clprop_beta_s
			self.beta_s_sq=self.clprop_beta_s_sq
			self.D_d=self.clprop_D_d
			self.r_s=self.clprop_r_s
		except:
			ns.update(locals())
			raise Exception('problem recovering all properties from '+self.fl_mass)

	def get_best_mags(self):
		self.cat_mag=ldac.openObjectFile(self.fl_photom)

		self.k_mags=[]
		for k in self.cat_mag.keys():
			if k.startswith('FLUX_APER1-SUBARU-9') or k.startswith('FLUX_APER1-SUBARU-10'):
			    if '10_' in k and '-1-' not in k:
				print 'skipping over: ',k
				continue
			    if 'COADD' in k: continue
			    if 'bpz_inputs' in k: continue
			    magk=self.cat_mag[k]
			    if magk.max() > magk.min():
				    #adam-improve# you could improve this by using the extrema to get bins showing the full width!
				    self.k_mags.append(k)

		print 'all mags: ',self.k_mags

		self.k_bands,self.k_mags=pipelinetools.get_best_mags(self.fl_photom)
		print 'best mags: ',self.k_mags
		return self.k_mags

	def PZmass_outputs(self,ml_base):
		self.ml_base = ml_base
		self.fl_pccat = self.ml_base+'-post_cuts.cat'
		#pc_cat=ldac.openObjectFile(pc_catfl)
		self.fl_pz_out_base =  ml_base #"%(dir_pzwork)s/%(cluster)s.%(filter)s.%(lens)s.maxlikelensing" % (self.props)
	def CCmass_cosmo_calcs(self):
		## get radial profile from CCmass info
		self.prof_table=ascii.read(self.fl_prof,names=["radial_arcmin","shear_ave","shear_err"])
		self.prof_rad_arcmin=self.prof_table["radial_arcmin"].data
		self.prof_gt=self.prof_table["shear_ave"].data
		self.prof_gt_err=self.prof_table["shear_err"].data

		####################################
		## assumed cosmology and define H(z)
		####################################
		self.clprop_conc=4.0
		u_convert=(1.0*astropy.units.arcmin).to(astropy.units.rad)
		self.prof_rad_radians = self.prof_rad_arcmin * u_convert.value #r in radians
		self.prof_rad_mpc=self.clprop_D_d*self.prof_rad_radians #Mpcs from center of self.cluster

		self.prof_rad_x = self.prof_rad_mpc / self.clprop_r_s # dimensionless radial distance
		H0=70.0 #km/s/Mpc
		#1 megaparsec = 3.09x10**19 km
		#H0_SI=70.0*(1/3.09e19)
		#Hubble time in years: (70.0*(1/3.09e19))**-1*(3600*24*365.25)**-1
		Om=.3
		Occ=.7
		H = lambda z : H0*np.sqrt(Om*(1+z)**3+Occ)
		H_at_z=H(self.clprop_z)*(1/3.09e19)
		#G_SI=6.67e-11 #SI units (m^3 kg^-1 s^-2)
		#G_const_Mpc_Msun_s = 4.51737014558e-48
		G = 4.51737014558e-48 #cosmo units (Mpc^3 Msun^-1 s^-2)
		c_light_SI = 3.0e8
		#1 megaparsec = 3.09x10**22  m
		c_light = c_light_SI *(1/3.09e22) #cosmo units (Mpc s^-1)

		self.rho_c=3*H_at_z**2/(8*np.pi*G) #yes these units are consistent [Msun / Mpc^3]
		self.delta_c=(200.0/3.0)*(self.clprop_conc**3/(np.log(1+self.clprop_conc)-self.clprop_conc/(1+self.clprop_conc)))

		####################################
		## calculate relevant lensing values
		####################################

		self.clprop_beta = self.clprop_beta_s * self.clprop_beta_inf #beta=D_ds/D_s == beta_s * beta_inf and D_s/(D_d*D_ds)=1/(beta*D_d) eqn #9
		self.clprop_Sigma_c = c_light**2/(4*np.pi*G)* 1/(self.clprop_beta*self.clprop_D_d) #1/(beta*D_d) == D_s/(D_d*D_ds) eqn #9
		self.beta=self.clprop_beta
		self.Sigma_c=self.clprop_Sigma_c
    except:
	ns.update(locals())
	raise


def get_mycls_from_list(clusterlist_fl='/u/ki/awright/gravitas/maxlikelensing/FgasThesis_sample_mine.list'):
	worklist = readtxtfile(clusterlist_fl)
	#worklist = readtxtfile('FgasThesis_sample_not_mine.list')
	#worklist = readtxtfile('FgasThesis_sample_mine.list')
	clusters = [x[0] for x in worklist]
	filters = [x[1] for x in worklist]
	lenses = [x[2] for x in worklist]
	print 'mycls=[my_cluster(cluster,filter,lens) for cluster in %s] ' % (repr(clusterlist_fl))
	mycls=[]
	for cluster,filter,lens in zip(clusters,filters,lenses):
		mycl=my_cluster(cluster,filter,lens)
		mycls.append(mycl)
	return mycls

def get_a_cluster_filter_lens(cluster):
	'''don't overuse this, it's going to re-make an instance of my_cluster each time it's called'''
	if cluster in allfgas_clusters:
		theone=allfgas_clusters==cluster
		filter=allfgas_filters[theone][0]
		lens=allfgas_lenses[theone][0]
		return (cluster,filter,lens)
	else:
		raise Exception('This is not in the `allfgas_clusters` list!')
def get_a_cluster(cluster):
	'''don't overuse this, it's going to re-make an instance of my_cluster each time it's called'''
	if cluster in allfgas_clusters:
		theone=allfgas_clusters==cluster
		filter=allfgas_filters[theone][0]
		lens=allfgas_lenses[theone][0]
		mycl=my_cluster(cluster,filter,lens)
		return mycl
	else:
		raise Exception('This is not in the `allfgas_clusters` list!')

if __name__=='__main__':
	try:

		cluster=os.environ['cluster']
		filter=os.environ['filter']
		lens=os.environ['lens']
		mycl=my_cluster(cluster,filter,lens)
		print 'cluster set by env vars'
		print 'mycl=my_cluster('+cluster+','+filter+','+lens+')'
	except KeyError:
		#worklist = readtxtfile('FgasThesis_sample.list')
		import imagetools, adam_quicktools_ArgCleaner
		args=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
		try:
			clusterlist_fl=args[0]
			print 'cluster list set by input arg: ',clusterlist_fl
		except:
			clusterlist_fl='FgasThesis_sample_mine.list'
			print 'cluster list set by default: ',clusterlist_fl
	
	#mycls=get_mycls_from_list(clusterlist_fl)
	#for mycl in mycls:
	#    mycl.get_best_mags()
	#for mycl in mycls:
	#	oo=mycl.get_latex_table_line()


	#sys.exit()
	#for mycl in mycls:
	#	print ' '.join(['cp',mycl.fl_cut_lensing_step,mycl.fl_pz_out_base.replace('maxlikelensing','cut_lensing.cat')])
	# print out stuff for the latex table!
	#mycls=get_mycls_from_list('/u/ki/awright/gravitas/maxlikelensing/FgasThesis_sample_mine.list')
	#for mycl in mycls: mycl.get_best_mags()
	mycls2=get_mycls_from_list('/u/ki/awright/gravitas/maxlikelensing/FgasThesis_sample_not_mine.list')
	for mycl in mycls2: 
		cc_cuts3fl=mycl.dir_lens+'cc_cuts3.dat'
		print 'grep MAG %s | grep > 22' % (cc_cuts3fl)
	for mycl in mycls2:
	    #mycl.get_best_mags()
	    print mycl.cluster, mycl.lens , mycl.filter , mycl.lensmag
	sys.exit()
	#for mycl in mycls:
	    #print repr(' & '.join(oo))
	for mycl in mycls2:
	    #mycl.get_best_mags()
	    oo=mycl.get_latex_table_line()
	    #print repr(' & '.join(oo))

#        mag_fls = glob.glob("/nfs/slac/g/ki/ki05/anja/SUBARU/%s/PHOTOMETRY_W-*_aper/%s.slr.cat" % (cl,cl))
#        if cl=='MACS1621+38':
#                mag_fl='/nfs/slac/g/ki/ki05/anja/SUBARU/MACS1621+38/PHOTOMETRY_W-C-IC_aper/MACS1621+38.slr.cat'
#        elif cl=='A383':
#                mag_fl='/nfs/slac/g/ki/ki05/anja/SUBARU/A383/PHOTOMETRY_W-S-I+_aper/A383.slr.cat'
#        else:
#                mag_fl=mag_fls[0]
