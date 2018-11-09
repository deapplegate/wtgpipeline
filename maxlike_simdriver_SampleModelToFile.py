#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################
#adam-example# ./maxlike_simdriver.py -o /u/ki/dapple/nfs22/cosmossims2017/UGRIZ/nocontam/maxlike/cutout_z_drawn_z=0.20_mass=12.00_44.out -i /u/ki/dapple/nfs22/cosmossims2017/UGRIZ/cutout_z_drawn_z=0.20_mass=12.00_44.cat -p /u/ki/dapple/nfs22/cosmossims2017/UGRIZ/pdz.pkl -b /u/ki/dapple/nfs22/cosmossims2017/UGRIZ/bpz.cat
#adam-example#  ./maxlike_simdriver.py -o test.out -i ~/nfs12/cosmos/simulations/clusters_2012-05-17/fake/cutout_z_drawn_z=0.56_mass=5.00_20.cat -p ~/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity/BVRIZ.pdz.cat -b ~/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity/BVRIZ.rawbpz.cat

#cp maxlike_simdriver.py maxlike_simdriver_SampleModelToFile.py
import maxlike_controller, maxlike_masses, nfwmodel_normshapedistro, maxlike_sim_filehandler
makeController = lambda : maxlike_controller.Controller(modelbuilder = nfwmodel_normshapedistro.NormShapedistro(),
                                           filehandler = maxlike_sim_filehandler.SimFilehandler(),
                                           runmethod = maxlike_masses.SampleModelToFile())

#####################
if __name__ == '__main__':
    controller = makeController()
    controller.run_all()
