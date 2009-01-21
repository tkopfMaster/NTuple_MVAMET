#ifndef HcalGeometry_h
#define HcalGeometry_h

#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloTopology/interface/HcalTopology.h"
#include "CondFormats/AlignmentRecord/interface/HcalAlignmentRcd.h"
#include "Geometry/Records/interface/HcalGeometryRecord.h"

class HcalGeometry : public CaloSubdetectorGeometry 
{
   public:

      typedef HcalAlignmentRcd   AlignmentRecord ;
      typedef HcalGeometryRecord AlignedRecord   ;
      typedef PHcalRcd           PGeometryRecord ;
      typedef HcalDetId          DetIdType       ;

      enum { k_NumberOfCellsForCorners = HcalDetId::kSizeForDenseIndexing } ;

      enum { k_NumberOfShapes = 17 } ;

      enum { k_NumberOfParametersPerShape = 11 } ;

      static std::string dbString() { return "PHcalRcd" ; }

      virtual unsigned int numberOfShapes() const { return k_NumberOfShapes ; }
      virtual unsigned int numberOfParametersPerShape() const { return k_NumberOfParametersPerShape ; }


      HcalGeometry();

      HcalGeometry(const HcalTopology * topology);

      /// The HcalGeometry will delete all its cell geometries at destruction time
      virtual ~HcalGeometry();
  
      virtual const std::vector<DetId>& getValidDetIds(
	 DetId::Detector det    = DetId::Detector ( 0 ), 
	 int             subdet = 0 ) const;

      virtual DetId getClosestCell(const GlobalPoint& r) const ;
      
      virtual CaloSubdetectorGeometry::DetIdSet getCells( const GlobalPoint& r,
							  double             dR ) const ;


      static std::string producerName() { return "Hcal" ; }

      static unsigned int numberOfAlignments() { return 36 ; }

      static unsigned int alignmentTransformIndexLocal( const DetId& id ) ;

      static unsigned int alignmentTransformIndexGlobal( const DetId& id ) ;

      static std::vector<HepPoint3D> localCorners( const double* pv, 
						   unsigned int  i,
						   HepPoint3D&   ref ) ;

      static CaloCellGeometry* newCell( const GlobalPoint& f1 ,
					const GlobalPoint& f2 ,
					const GlobalPoint& f3 ,
					CaloCellGeometry::CornersMgr* mgr,
					const double*      parm ) ;
					

   private:

      /// helper methods for getClosestCell
      int etaRing(HcalSubdetector bc, double abseta) const;
      int phiBin(double phi, int etaring) const;


      const HcalTopology * theTopology;
      mutable DetId::Detector lastReqDet_;
      mutable int lastReqSubdet_;

      mutable std::vector<DetId> m_validIds ;
      bool m_ownsTopology ;
};


#endif

