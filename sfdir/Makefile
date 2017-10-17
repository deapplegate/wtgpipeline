#CVSID $Id: Makefile.dac,v 1.3 2010-02-09 02:13:47 dapple Exp $

BIN = spikefinder satfinder shadowfinder expand_cosmics_mask
OBJS = leastsq

PROPEROBJS = $(addprefix objects/,$(addsuffix .o, $(OBJS)))


CC = g++
CCFLAGS = -g -O3

LD = g++
LDFLAGS =  -L/afs/slac/g/ki/software/cfitsio/3.34/lib -Wl,-rpath,/afs/slac/g/ki/software/cfitsio/3.34/lib

INCS =  -I/afs/slac/g/ki/software/cfitsio/3.34/include

LOCAL_LIBS = 

LIBS = -lgsl -lgslcblas -lm -lcfitsio

all: objects $(PROPEROBJS) $(LOCAL_LIBS) $(BIN) install

spikefinder: objects/spikefinder.o $(PROPEROBJS)
	@echo "Building $@"
	g++ $(LDFLAGS) $^ $(LIBS) -o $@
	chmod a+x $@
	@echo "done."

satfinder: objects/satfinder.o $(PROPEROBJS)
	@echo "Building $@"
	g++ $(LDFLAGS) $^ $(LIBS) -o $@
	chmod a+x $@
	@echo "done."

shadowfinder: objects/shadowfinder.o $(PROPEROBJS)
	@echo "Building $@"
	g++ $(LDFLAGS) $^ $(LIBS) -o $@
	chmod a+x $@
	@echo "done."

expand_cosmics_mask: objects/expand_cosmics_mask.o $(PROPEROBJS)
	@echo "Building $@"
	g++ $(LDFLAGS) $^ $(LIBS) -o $@
	chmod a+x $@
	@echo "done."



objects:
	mkdir objects

objectDir:
	@mkdir objects

clean:
	@echo "Cleaning..."
	@rm -f objects/*.o
	@rm -f $(LOCAL_LIBS)
	@echo "done."

install:
	@echo "Installing..."
	@echo "done."

objects/%.o: %.cxx %.h
	@echo "Building $@"
	@g++ $(CCFLAGS) $(INCS) -c -o $@ $<
	@echo "done."

objects/%.o: %.cc
	@echo "Building $@"
	@g++ $(CCFLAGS) $(INCS) -c -o $@ $<
	@echo "done."

objects/%.o: %.C
	@echo "Building $@"
	@gcc $(CCFLASGS) $(INCS) -c -o $@ $<
	@echo "done."
