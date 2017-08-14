#

BIN = biasslope
OBJS = FitsObj

PROPEROBJS = $(addprefix objects/,$(addsuffix .o, $(OBJS)))


CC = g++
CCFLAGS = -g -O3

LD = g++
LDFLAGS = 

INCS = -I/afs/slac/g/ki/include

LOCAL_LIBS = 

LIBS = -L/afs/slac/g/ki/lib -lgsl -lgslcblas -lm -lcfitsio

all: objects $(PROPEROBJS) $(LOCAL_LIBS) $(BIN) install

biasslope: objects/biasslope.o $(PROPEROBJS)
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
