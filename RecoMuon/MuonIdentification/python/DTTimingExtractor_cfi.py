import FWCore.ParameterSet.Config as cms

from RecoMuon.TrackingTools.MuonSegmentMatcher_cff import *

DTTimingExtractorBlock = cms.PSet(
  DTTimingParameters = cms.PSet(
    MuonSegmentMatcher,
    ServiceParameters = cms.PSet(
        Propagators = cms.untracked.vstring('SteppingHelixPropagatorAny', 
            'PropagatorWithMaterial', 
            'PropagatorWithMaterialOpposite'),
        RPCLayers = cms.bool(True)
    ),
    DTsegments = cms.InputTag("dt4DSegments"),
    PruneCut = cms.double(10000.),
#    DTTimeOffset = cms.double(2.7),
    DTTimeOffset = cms.double(0.),
    HitsMin = cms.int32(3),
    UseSegmentT0 = cms.bool(False),
    DoWireCorr = cms.bool(False),
    DropTheta = cms.bool(True),
    RequireBothProjections = cms.bool(False),
    debug = cms.bool(False),
  )
)


