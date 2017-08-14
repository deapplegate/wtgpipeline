#!/usr/bin/env python
######################
#
# A module that generically handles configuration issues to wrap around analysis functions
#
########################

import inspect, copy, sys
from optparse import OptionParser

########################

__cvs_id__ = "$Id: manageconfigs.py,v 1.6 2010-02-06 18:47:16 dapple Exp $"

########################

class Configuration(object):
    def __init__( self, *args, **kw ):
        for arg in args:
            self.__dict__.update(arg)
        self.__dict__.update( kw )
    def __str__(self):
        return str(self.__dict__)
    def __eq__(self, other):
        return self.__dict__ ==  other.__dict__
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    def __delitem__(self, key):
        del self.__dict__[key]
    def __iter__(self):
        return self.__dict__.__iter__()
    def __contains__(self, item):
        return item in self.__dict__

    def toFile(self, file):

        closeFile = False
        if isinstance(file, str):
            output = open(file, 'w')
            closeFile = True
        else:
            output = file

        for key, val in self.__dict__.iteritems():
            if inspect.isfunction(val):
                output.write('%s=%s\n' % (key, val.__name__))
            else:
                output.write('%s=%s\n' % (key, repr(val)))

        if closeFile:
            output.close()


################################################################

class manageConfigs(object):
    def __init__(self, func):
        self.func = func
        argnames, defaults = self.readArguments(func)
        self.argnames = argnames
        self._defaults = defaults

    def getDefaults(self):
        return copy.deepcopy(self._defaults)
    
    defaults = property(getDefaults)

    def loadConfig(self, filename):
        
        context = sys.modules[self.func.__module__].__dict__
        config = self.defaults
        execfile(filename, context, config)

        return config

    def readArguments(self, func):
        args, varargs, keywords, defaults = inspect.getargspec(func)
        args.reverse()
        defaults = list(defaults)
        defaults.reverse()

        nargs = len(args)
        ndefaults = len(defaults)
        defaults.extend( (nargs-ndefaults) * [None] )
        
        arguments = {}
        for arg, default in zip(args, defaults):
            arguments[arg] = default

        args.reverse()

        return args, Configuration(**arguments)


    def addConfigToParser(self, parser):
        
        parser.add_option('-c', '--config', action='callback',
                          type='string', callback=_loadConfig_callback,
                          help = 'Load a configuration file',
                          callback_args=(self,))

        parser.add_option('-d', '--dump', action='callback',
                          callback=_dumpDefault_callback,
                          help = 'Dump default configuration to stdout',
                          callback_args=(self,))


        
    def __call__(self, *args, **keywords):


        if 'config' in keywords:

            if isinstance(keywords['config'], str):
                currentConfig = self.loadConfig(keywords['config'])
            elif not isinstance(keywords['config'], Configuration):
                currentConfig = Configuration(keywords['config'])
            else:
                currentConfig = copy.deepcopy(keywords['config'])

            del keywords['config']

        else:
            currentConfig = self.defaults


        configDumpTarget = None
        if 'dumpConfig' in keywords:

            configDumpTarget = keywords['dumpConfig']
            del keywords['dumpConfig']
            


        if len(args) > 0:
            for argname, val in zip(self.argnames, args):
                currentConfig.__dict__[argname] = val

        currentConfig.__dict__.update(keywords)
        
        argsForFunction = {}
        for argname in self.argnames:
            print argname
            argsForFunction[argname] = currentConfig[argname]
        
        results = self.func(**argsForFunction)

        if isinstance(configDumpTarget, str):
            currentConfig.toFile(configDumpTarget)
            return results
        elif configDumpTarget:
            return results, currentConfig
        else:
            return results

#####################################################


def _loadConfig_callback(option, opt, configFile, parser, func):
    
    config = func.loadConfig(configFile)

    parser.config = config

def _dumpDefault_callback(option, opt, configFile, parser, func):

    func.defaults.toFile(sys.stdout)
    sys.exit(0)


######################################################
    

#########################
#########################


########################

