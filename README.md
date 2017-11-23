# wtgpipeline
Scripts used to process cluster lensing data for the Weighing the Giants Project

## What is wtgpipeline?
The wtgpipeline is a gravitational lensing data analysis pipeline which seeks to take raw images of galaxy cluster fields and turn them into accurate measurments of galaxy cluster mass using the methods described in the *Weighing the Giants Papers* section below. See those papers for how these methods were used on real data, and see the [wtgpipeline wiki](https://github.com/deapplegate/wtgpipeline/wiki) for details on the code that's available in this repository.

This software was a spinoff of the gabods/theli/bonnpipeline. It was developed by Anja von der Linden (@anjavdl), Mark Allen, Pat Kelley (@patkel), and Doug Applegate (@deapplegate) as part of the Weighing the Giants (WtG) project. Currently Adam Wright is doing the majority of the development (email awright3@stanford.edu for assistance) on the code, documentation, and is managing the github page (so email awright3@stanford.edu for assistance).

## How does wtgpipeline work?

The goal of wtgpipeline is to deliver accurate weak-lensing mass measurements. This requires a careful measurement of systematic uncertainties leading to robust weak-lensing shape measurements and precision photometry. Cluster masses are measured by two different methods: traditional color-cuts measurements are carried out on every cluster and for clusters with 5-filter photometry another technique is used: a Bayesian weak-lensing approach using the full photometric redshift probability distribution for each background galaxy.

Beginning with raw images, this pipeline carries out the instrument signature removal (ISR), performs astrometric and photometric calibration, performs an illumination correction, coadds images, masks defects, and measures photometric redshifts. Currently there is a 10-step structure to the pipeline:

1. Preprocessing/ISR/Brighter-Fatter Correction
2. Distribute Sets and Mask
3. Directories and Headers changed. Cross-talk Correction applied.
4. Initial Astrometry
5. Illumination Correction
6. Final astrometry
7. Coadding
8. Coadd Masking
9. Photometric Measurement and Calibration
10. Photometric Redshifts

Steps 11 (measure CC masses) and 12 (measure p(z) masses) are yet to come.

## Should I clone or fork the wtgpipeline repo and use it for my personal lensing project?
That depends. If you are part of, or connected to, the X-ray Astronomy and Observational Cosmology (XOC) group at Stanford, then yes! If not, then it might be useful to do so, but it's important to point out that this pipeline is a work in progress. Certain parts of the pipeline are ready to go and could be useful for your, other parts are a bit clunky and might require some work to get them up and running, and lastly some parts likely have been surpassed by better methods which you should use instead. If there is a specific part of the WtG methodology which you would like to impliment, feel free to clone/fork the repo and try it out (see the [wtgpipeline wiki](https://github.com/deapplegate/wtgpipeline/wiki) to find out which scripts correspond to which data processing steps)

The primary goal of this github repo is to get all of our code organized and documented, this is mainly the concern of our XOC cluster lensing group. The secondary goal (which, as of Nov 2017 is still far off), is to make the code available for others to use in the astronomy community's push to develop the tools and techniques needed to do cluster cosmology with LSST.

## Weighing the Giants Papers
Please cite the Weighing the Giants core papers if you use any material from this repository. The abstracts and bibtex entries are provided below.


Title:              Weighing the Giants - I. Weak-lensing masses for 51 
                    massive galaxy clusters: project overview, data 
                    analysis methods and cluster images
                    
Authors:            von der Linden, Anja; Allen, Mark T.;
                    Applegate, Douglas E.; Kelly, Patrick L.;
                    Allen, Steven W.; Ebeling, Harald;
                    Burchat, Patricia R.; Burke, David L.;
                    Donovan, David; Morris, R. Glenn; Blandford, Roger;
                    Erben, Thomas; Mantz, Adam
                    
Publication:        Monthly Notices of the Royal Astronomical Society, 
                    Volume 439, Issue 1, p.2-27
                    
Publication Date:   03/2014
Origin:             OUP
Abstract Copyright: The Authors 2014. Published by Oxford University 
                    Press on behalf of The Royal Astronomical Society.

DOI:                10.1093/mnras/stt1945

Bibliographic Code: 2014MNRAS.439....2V

Abstract: This is the first in a series of papers in which we measure accurate 
weak-lensing masses for 51 of the most X-ray luminous galaxy clusters 
known at redshifts 0.15 ≲ z<SUB>Cl</SUB> ≲ 0.7, in order to 
calibrate X-ray and other mass proxies for cosmological cluster 
experiments. The primary aim is to improve the absolute mass calibration 
of cluster observables, currently the dominant systematic uncertainty 
for cluster count experiments. Key elements of this work are the 
rigorous quantification of systematic uncertainties, high-quality data 
reduction and photometric calibration, and the 'blind' nature of the 
analysis to avoid confirmation bias. Our target clusters are drawn from 
X-ray catalogues based on the ROSAT All-Sky Survey, and provide a 
versatile calibration sample for many aspects of cluster cosmology. We 
have acquired wide-field, high-quality imaging using the Subaru 
Telescope and Canada-France-Hawaii Telescope for all 51 clusters, in at 
least three bands per cluster. For a subset of 27 clusters, we have data 
in at least five bands, allowing accurate photometric redshift estimates 
of lensed galaxies. In this paper, we describe the cluster sample and 
observations, and detail the processing of the SuprimeCam data to yield 
high-quality images suitable for robust weak-lensing shape measurements 
and precision photometry. For each cluster, we present wide-field 
three-colour optical images and maps of the weak-lensing mass 
distribution, the optical light distribution and the X-ray emission. 
These provide insights into the large-scale structure in which the 
clusters are embedded. We measure the offsets between X-ray flux 
centroids and the brightest cluster galaxies in the clusters, finding 
these to be small in general, with a median of 20 kpc. For offsets 
≲100 kpc, weak-lensing mass measurements centred on the brightest 
cluster galaxies agree well with values determined relative to the X-ray 
centroids; miscentring is therefore not a significant source of 
systematic uncertainty for our weak-lensing mass measurements. In 
accompanying papers, we discuss the key aspects of our photometric 
calibration and photometric redshift measurements (Kelly et al.), and 
measure cluster masses using two methods, including a novel Bayesian 
weak-lensing approach that makes full use of the photometric redshift 
probability distributions for individual background galaxies (Applegate 
et al.). In subsequent papers, we will incorporate these weak-lensing 
mass measurements into a self-consistent framework to simultaneously 
determine cluster scaling relations and cosmological parameters. 




Title:              Weighing the Giants - II. Improved calibration of 
                    photometry from stellar colours and accurate 
                    photometric redshifts
                    
Authors:            Kelly, Patrick L.; von der Linden, Anja;
                    Applegate, Douglas E.; Allen, Mark T.;
                    Allen, Steven W.; Burchat, Patricia R.;
                    Burke, David L.; Ebeling, Harald; Capak, Peter;
                    Czoske, Oliver; Donovan, David; Mantz, Adam;
                    Morris, R. Glenn
                    
Publication:        Monthly Notices of the Royal Astronomical Society, 
                    Volume 439, Issue 1, p.28-47
                    
Publication Date:   03/2014
Origin:             OUP
Abstract Copyright: 2014 The Authors Published by Oxford University 
                    Press on behalf of the Royal Astronomical Society

DOI:                10.1093/mnras/stt1946

Bibliographic Code: 2014MNRAS.439...28K

Abstract: We present improved methods for using stars found in astronomical 
exposures to calibrate both star and galaxy colours as well as to adjust 
the instrument flat-field. By developing a spectroscopic model for the 
Sloan Digital Sky Survey (SDSS) stellar locus in colour-colour space, 
synthesizing an expected stellar locus, and simultaneously solving for 
all unknown zero-points when fitting to the instrumental locus, we 
increase the calibration accuracy of stellar locus matching. We also use 
a new combined technique to estimate improved flat-field models for the 
Subaru SuprimeCam camera, forming `star flats' based on the magnitudes 
of stars observed in multiple positions or through comparison with 
available measurements in the SDSS catalogue. These techniques yield 
galaxy magnitudes with reliable colour calibration (≲0.01-0.02 mag 
accuracy) that enable us to estimate photometric redshift probability 
distributions without spectroscopic training samples. We test the 
accuracy of our photometric redshifts using spectroscopic redshifts 
z<SUB>s</SUB> for ˜5000 galaxies in 27cluster fields with at least 
five bands of photometry, as well as galaxies in the Cosmic Evolution 
Survey (COSMOS) field, finding σ((z<SUB>p</SUB> - 
z<SUB>s</SUB>)/(1 + z<SUB>s</SUB>)) ≈ 0.03 for the most probable 
redshift z<SUB>p</SUB>. We show that the full posterior probability 
distributions for the redshifts of galaxies with five-band photometry 
exhibit good agreement with redshifts estimated from thirty-band 
photometry in the COSMOS field. The growth of shear with increasing 
distance behind each galaxy cluster shows the expected redshift-distance 
relation for a flat Λ cold dark matter (Λ-CDM) cosmology. 
Photometric redshifts and calibrated colours are used in subsequent 
papers to measure the masses of 51 galaxy clusters from their weak 
gravitational shear and determine improved cosmological constraints. We 
make our PYTHON code for stellar locus matching publicly available at 
http://big-macs-calibrate.googlecode.com; the code requires only input 
catalogues and filter transmission functions. 

Title:              Weighing the Giants - III. Methods and measurements 
                    of accurate galaxy cluster weak-lensing masses
                    
Authors:            Applegate, Douglas E.; von der Linden, Anja;
                    Kelly, Patrick L.; Allen, Mark T.; Allen, Steven W.;
                    Burchat, Patricia R.; Burke, David L.;
                    Ebeling, Harald; Mantz, Adam; Morris, R. Glenn
                    
Publication:        Monthly Notices of the Royal Astronomical Society, 
                    Volume 439, Issue 1, p.48-72
                    
Publication Date:   03/2014
Origin:             OUP
Abstract Copyright: 2014 The Authors Published by Oxford University 
                    Press on behalf of the Royal Astronomical Society

DOI:                10.1093/mnras/stt2129

Bibliographic Code: 2014MNRAS.439...48A

Abstract: We report weak-lensing masses for 51 of the most X-ray luminous galaxy 
clusters known. This cluster sample, introduced earlier in this series 
of papers, spans redshifts 0.15 ≲ z<SUB>cl</SUB> ≲ 0.7, and is 
well suited to calibrate mass proxies for current cluster cosmology 
experiments. Cluster masses are measured with a standard 'colour-cut' 
lensing method from three-filter photometry of each field. Additionally, 
for 27 cluster fields with at least five-filter photometry, we measure 
high-accuracy masses using a new method that exploits all information 
available in the photometric redshift posterior probability 
distributions of individual galaxies. Using simulations based on the 
COSMOS-30 catalogue, we demonstrate control of systematic biases in the 
mean mass of the sample with this method, from photometric redshift 
biases and associated uncertainties, to better than 3 per cent. In 
contrast, we show that the use of single-point estimators in place of 
the full photometric redshift posterior distributions can lead to 
significant redshift-dependent biases on cluster masses. The performance 
of our new photometric redshift-based method allows us to calibrate 
'colour-cut' masses for all 51 clusters in the present sample to a total 
systematic uncertainty of ≈7 per cent on the mean mass, a level 
sufficient to significantly improve current cosmology constraints from 
galaxy clusters. Our results bode well for future cosmological studies 
of clusters, potentially reducing the need for exhaustive spectroscopic 
calibration surveys as compared to other techniques, when deep, 
multifilter optical and near-IR imaging surveys are coupled with robust 
photometric redshift methods. 



@ARTICLE{2014MNRAS.439...48A,
   author = {{Applegate}, D.~E. and {von der Linden}, A. and {Kelly}, P.~L. and 
	{Allen}, M.~T. and {Allen}, S.~W. and {Burchat}, P.~R. and {Burke}, D.~L. and 
	{Ebeling}, H. and {Mantz}, A. and {Morris}, R.~G.},
    title = "{Weighing the Giants - III. Methods and measurements of accurate galaxy cluster weak-lensing masses}",
  journal = {\mnras},
archivePrefix = "arXiv",
   eprint = {1208.0605},
 keywords = {gravitational lensing: weak, methods: data analysis, methods: statistical, galaxies: clusters: general, galaxies: distances and redshifts, cosmology: observations},
     year = 2014,
    month = mar,
   volume = 439,
    pages = {48-72},
      doi = {10.1093/mnras/stt2129},
   adsurl = {http://adsabs.harvard.edu/abs/2014MNRAS.439...48A},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{2014MNRAS.439....2V,
   author = {{von der Linden}, A. and {Allen}, M.~T. and {Applegate}, D.~E. and 
	{Kelly}, P.~L. and {Allen}, S.~W. and {Ebeling}, H. and {Burchat}, P.~R. and 
	{Burke}, D.~L. and {Donovan}, D. and {Morris}, R.~G. and {Blandford}, R. and 
	{Erben}, T. and {Mantz}, A.},
    title = "{Weighing the Giants - I. Weak-lensing masses for 51 massive galaxy clusters: project overview, data analysis methods and cluster images}",
  journal = {\mnras},
archivePrefix = "arXiv",
   eprint = {1208.0597},
 keywords = {gravitational lensing: weak, methods: data analysis, galaxies: clusters: general, galaxies: elliptical and lenticular, cD, cosmology: observations},
     year = 2014,
    month = mar,
   volume = 439,
    pages = {2-27},
      doi = {10.1093/mnras/stt1945},
   adsurl = {http://adsabs.harvard.edu/abs/2014MNRAS.439....2V},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{2014MNRAS.439...28K,
   author = {{Kelly}, P.~L. and {von der Linden}, A. and {Applegate}, D.~E. and 
	{Allen}, M.~T. and {Allen}, S.~W. and {Burchat}, P.~R. and {Burke}, D.~L. and 
	{Ebeling}, H. and {Capak}, P. and {Czoske}, O. and {Donovan}, D. and 
	{Mantz}, A. and {Morris}, R.~G.},
    title = "{Weighing the Giants - II. Improved calibration of photometry from stellar colours and accurate photometric redshifts}",
  journal = {\mnras},
archivePrefix = "arXiv",
   eprint = {1208.0602},
 keywords = {gravitational lensing: weak, methods: observational, techniques: photometric},
     year = 2014,
    month = mar,
   volume = 439,
    pages = {28-47},
      doi = {10.1093/mnras/stt1946},
   adsurl = {http://adsabs.harvard.edu/abs/2014MNRAS.439...28K},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
