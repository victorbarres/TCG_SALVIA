# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 14:48:11 2015

@author: Victor Barres

Defines the interface between the Matlab SaliencyToolbox and TCG

Uses scipy.io to read .mat files.
Uses numpy for the saliency map.

The matlab saliency toolbox should have already generated the .mat files containing bottom-up saliency information.
"""
import scipy.io as sio

class SALIENCY_PARAMS:
    """
    Stores the parameters used in computing the bottom-up saliency data.
    
    Data:
        - foaSize (INT)
        - pyramidType (STR)
        - features ([STR])
        - weights ([FLOAT])
        - IORtype (STR)
        - shapeMode (STR)
        - levelParams (DICT) : minLevel:INT, maxlevel:INT, minDelta:INT, maxDelta:INT, mapLevel:INT
        - normtype (STR)
        - numIter (INT)
        - useRandom (BOOL)
        - segmentComputeType (STR)
        - IORdecay (FLOAT)
        - smOutputRange (FLOAT)
        - noiseAmpl (FLOAT)
        - noiseConst (FLOAT)
        - gaborParams (DICT): filterPeriod:INT, elongation:INT, filterSize:INT, stddev:INT, phasese:[INT]
        - oriAngles ([FLOAT])
        - oriComputeMode (STR)
        - visualizationStyle (STR)
        - exclusionMask ([])
    """
    def __init__(self):
        self.foaSize = 64
        self.pyramidType = 'dyadic'
        self.features = ['Color', 'Intensities', 'Orientations']
        self.weights = [1,1,1]
        self.IORtype = 'shape'
        self.shapeMode = 'shapeFM'
        self.levelParams = {'minLevel':3, 'maxlevel':5, 'minDelta':3, 'maxDelta':4, 'mapLevel':5}
        self.normtype = 'Iterative'
        self.numIter = 3
        self.useRandom = True
        self.segmentComputeType = 'Fast'
        self.IORdecay = 0.9999
        self.smOutputRange = 1.0e-09
        self.noiseAmpl = 1.0e-17
        self.noiseConst = 1.0e-14
        self.gaborParams = {'filterPeriod':7, 'elongation':1, 'filterSize':9, 'stddev':2.3333, 'phasese':[0,90]}
        self.oriAngles = [0,45, 90, 135]
        self.oriComputeMode = 'efficient'
        self.visualizationStyle = 'Contour'
        self.exclusionMask =[]

class ORIG_IMAGE:
    """
    Stores the original image information.
    Data:
        - filename (STR)
        - data (ARRAY)
        - type (STR)
        - size ([INT])
        - dims (INT)
    """
    def __init__(self):
        self.fileName = None
        self.data = None
        self.type = None
        self.size = None
        self.dims = None

class SALIENCY_MAP:
    """
    Stores the saliency map.
    Data:
        - label (STR)
        - data (ARRAY)
    """
    def __init__(self):
        self.label = 'SaliencyMap'
        self.data = None

class FEATURE_MAP:
    """
    Data:
        - label (STR)
        - data (ARRAY)
        - 
    """

class CONSPICUITY_MAP:
    """
    """

class PYRAMID_LEVEL:
    """
    Data:
        - label (STR)
        - data (ARRAY)
    """

class PYRAMID:
    """
    Data:
         - lablel (STR)
         - type (STR)
         - levels ([PYRAMID_LEVEL])
    """

class SALIENCY_FEATURE_DATA:
    """
    Data:
        - label (STR)
        - pyramid ([PYRAMID])
        - FM (ARRAY[FEATURE_MAP])
        - csLevels
        - CM (CONSPICUITY_MAP)
    """
    


def load(self, file_name):
    mat_content = sio.loadmat(file_name)
    BU_saliency = mat_content['BU_saliency']
        