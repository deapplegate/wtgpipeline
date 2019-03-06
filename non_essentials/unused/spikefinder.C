void spikefinder(char* filename, char* outputfilename) {
  gSystem->Load("/a/sulky37/g.ki.ki09/mallen/SpikeFinder/libcfitsio.so");
  gSystem->Load("/a/sulky37/g.ki.ki09/mallen/SpikeFinder/MSpikeFinder_C.so");
  MSpikeFinder l(filename,"SCIENCE","CHIP","n");
  l.FindSpike(outputfilename);
}
 
