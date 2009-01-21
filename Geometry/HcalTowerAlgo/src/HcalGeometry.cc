#include "Geometry/CaloGeometry/interface/CaloCellGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalGeometry.h"
#include "Geometry/HcalTowerAlgo//src/HcalHardcodeGeometryData.h"

HcalGeometry::HcalGeometry() :
   theTopology    ( new HcalTopology ),
   lastReqDet_    ( DetId::Detector(0) ), 
   lastReqSubdet_ ( 0 ) ,
   m_ownsTopology ( true )
{
}

HcalGeometry::HcalGeometry( const HcalTopology* topology ) :
   theTopology    ( topology ) ,
   lastReqDet_    ( DetId::Detector(0) ) , 
   lastReqSubdet_ ( 0 ) ,
   m_ownsTopology ( false ) 
{
}
  

HcalGeometry::~HcalGeometry() 
{
   if( m_ownsTopology ) delete theTopology ;
}


const std::vector<DetId>& 
HcalGeometry::getValidDetIds( DetId::Detector det,
			      int             subdet ) const 
{
   const std::vector<DetId>& baseIds ( CaloSubdetectorGeometry::getValidDetIds() ) ;
   if( det    == DetId::Detector( 0 ) &&
       subdet == 0                        )
   {
      return baseIds ;
   }
   
   if( lastReqDet_    != det    ||
       lastReqSubdet_ != subdet    ) 
   {
      lastReqDet_     = det    ;
      lastReqSubdet_  = subdet ;
      m_validIds.clear();
      m_validIds.reserve( baseIds.size() ) ;
   }

   if( m_validIds.empty() ) 
   {
      for( unsigned int i ( 0 ) ; i != baseIds.size() ; ++i ) 
      {
	 const DetId id ( baseIds[i] );
	 if( id.det()      == det    &&
	     id.subdetId() == subdet    )
	 { 
	    m_validIds.push_back( id ) ;
	 }
      }
      std::sort(m_validIds.begin(),m_validIds.end());
   }
   return m_validIds;
}


DetId HcalGeometry::getClosestCell(const GlobalPoint& r) const
{
  // Now find the closest eta_bin, eta value of a bin i is average
  // of eta[i] and eta[i-1]
  double abseta = fabs(r.eta());
  
  // figure out subdetector, giving preference to HE in HE/HF overlap region
  HcalSubdetector bc= HcalEmpty;
  if( abseta <= theHBHEEtaBounds[theTopology->lastHBRing()] )
  {
    bc = HcalBarrel;
  }
  else if( abseta <= theHBHEEtaBounds[theTopology->lastHERing()] ) 
  {
    bc = HcalEndcap;
  }
  else
  {
    bc = HcalForward;
  }

  if (bc == HcalForward) {
    static const double z_long=1100.0;
    static const double z_short=1120.0;
    // determine front-face eta
    double radius=sqrt(pow(r.x(),2)+pow(r.y(),2));
    double trueAeta=asinh(z_long/radius);
    // find eta bin
    int etaring = etaRing(bc, trueAeta);
    if (etaring>theTopology->lastHFRing()) etaring=theTopology->lastHFRing(); 
  
    int phibin = phiBin(r.phi(), etaring);

    // add a sign to the etaring
    int etabin = (r.z() > 0) ? etaring : -etaring;
    HcalDetId bestId(bc,etabin,phibin,((fabs(r.z())>=z_short)?(2):(1)));
    return bestId;
  } else {

    // find eta bin
    int etaring = etaRing(bc, abseta);
    
    int phibin = phiBin(r.phi(), etaring);
    
    // add a sign to the etaring
    int etabin = (r.z() > 0) ? etaring : -etaring;
    
    //Now do depth if required
    int dbin = 1;
    double pointradius=r.mag();
    double dradius=99999.;
    HcalDetId currentId(bc, etabin, phibin, dbin);
    HcalDetId bestId;
    for(  ; currentId != HcalDetId(); theTopology->incrementDepth(currentId))
      {    
	const CaloCellGeometry * cell = getGeometry(currentId);
	assert(cell != 0);
	double radius=cell->getPosition().mag();
	if(fabs(pointradius-radius)<dradius) 
	  {
	    bestId = currentId;
	    dradius=fabs(pointradius-radius);
	  }
      }
    
    return bestId;
  }
}


int HcalGeometry::etaRing(HcalSubdetector bc, double abseta) const
{
  int etaring;
  if( bc == HcalForward ) {
    for(etaring = theTopology->firstHFRing();
        etaring <= theTopology->lastHFRing(); ++etaring)
    {
      if(theHFEtaBounds[etaring-theTopology->firstHFRing()+1] > abseta) break;
    }
  }
  else
  {
    for(etaring = 1;
        etaring <= theTopology->lastHERing(); ++etaring)
    {
      if(theHBHEEtaBounds[etaring] >= abseta) break;
    }
  }

  return etaring;
}


int HcalGeometry::phiBin(double phi, int etaring) const
{
   static const double twopi = M_PI+M_PI;
  //put phi in correct range (0->2pi)
  if(phi<0.0) phi += twopi;
  if(phi>twopi) phi -= twopi;
  int nphibins = theTopology->nPhiBins(etaring);
  int phibin= static_cast<int>(phi/twopi*nphibins)+1;
  int iphi;

  // rings 40 and 41 are offset wrt the other phi numbering
  //  1        1         1         2
  //  ------------------------------
  //  72       36        36        1
  if(etaring >= theTopology->firstHFQuadPhiRing())
  {
    phi+=(twopi/36); //shift by half tower.    
    phibin=static_cast<int>(phi/twopi*nphibins);
    if (phibin==0) phibin=18;
    iphi=phibin*4-1; // 71,3,5,
  } else {
    // convert to the convention of numbering 1,3,5, in 36 phi bins
    iphi=(phibin-1)*(72/nphibins) + 1;
  }

  return iphi;
}

CaloSubdetectorGeometry::DetIdSet 
HcalGeometry::getCells( const GlobalPoint& r, 
			double             dR ) const 
{
   CaloSubdetectorGeometry::DetIdSet dis;  // this is the return object

   if( 0.000001 < dR )
   {
      if( dR > M_PI/2. ) // this version needs "small" dR
      {
	 dis = CaloSubdetectorGeometry::getCells( r, dR ) ; // base class version
      }
      else
      {
	 const double dR2     ( dR*dR ) ;
	 const double reta    ( r.eta() ) ;
	 const double rphi    ( r.phi() ) ;
	 const double lowEta  ( reta - dR ) ;
	 const double highEta ( reta + dR ) ;
	 const double lowPhi  ( rphi - dR ) ;
	 const double highPhi ( rphi + dR ) ;
	 
	 const double hfEtaHi ( theHFEtaBounds[ theTopology->lastHFRing() -
						theTopology->firstHFRing() + 1 ] ) ;
	 
	 if( highEta > -hfEtaHi &&
	     lowEta  <  hfEtaHi    ) // in hcal
	 {
	    const HcalSubdetector hs[] = { HcalBarrel, HcalOuter, HcalEndcap, HcalForward } ;

	    for( unsigned int is ( 0 ) ; is != 4 ; ++is )
	    {
	       const int sign        (  reta>0 ? 1 : -1 ) ;
	       const int ieta_center ( sign*etaRing( hs[is], fabs( reta ) ) ) ;
	       const int ieta_lo     ( ( 0 < lowEta*sign ? sign : -sign )*etaRing( hs[is], fabs( lowEta ) ) ) ;
	       const int ieta_hi     ( ( 0 < highEta*sign ? sign : -sign )*etaRing( hs[is], fabs( highEta ) ) ) ;
	       const int iphi_lo     ( phiBin( lowPhi , ieta_center ) ) ;
	       const int iphi_hi     ( phiBin( highPhi, ieta_center ) ) ;
	       const int jphi_lo     ( iphi_lo>iphi_hi ? iphi_lo - 72 : iphi_lo ) ;
	       const int jphi_hi     ( iphi_hi ) ;

	       const int idep_lo     ( 1 == is ? 4 : 1 ) ;
	       const int idep_hi     ( 1 == is ? 4 :
				       ( 2 == is ? 3 : 2 ) ) ;
	       for( int ieta ( ieta_lo ) ; ieta <= ieta_hi ; ++ieta ) // over eta limits
	       {
		  if( ieta != 0 )
		  {
		     for( int jphi ( jphi_lo ) ; jphi <= jphi_hi ; ++jphi )  // over phi limits
		     {
			const int iphi ( 1 > jphi ? jphi+72 : jphi ) ;

			for( int idep ( idep_lo ) ; idep <= idep_hi ; ++idep )
			{
			   if( HcalDetId::validDetId( hs[is], ieta, iphi, idep ) )
			   {
			      const HcalDetId did ( hs[is], ieta, iphi, idep ) ;
			      const CaloCellGeometry* cell ( getGeometry( did ) );
			      if( 0 != cell )
			      {
				 const GlobalPoint& p   ( cell->getPosition() ) ;
				 const double       eta ( p.eta() ) ;
				 const double       phi ( p.phi() ) ;
				 if( reco::deltaR2( eta, phi, reta, rphi ) < dR2 ) dis.insert( did ) ;
			      }
			   }
			}
		     }
		  }
	       }
	    }
	 }
      }
   }
   return dis;
}

