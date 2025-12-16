import { 
  Heart, 
  MapPin, 
  Clock, 
  Building2,
  Users,
  Pill,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle,
  Info,
  ChevronDown,
  ChevronUp,
  Activity
} from 'lucide-react';
import { useState } from 'react';
import type { NHSBSAHealthProfile, NHSBSANearestPractices } from '../types';

interface Props {
  healthProfile?: NHSBSAHealthProfile;
  nearestPractices?: NHSBSANearestPractices;
}

export default function NHSBSAResults({ healthProfile, nearestPractices }: Props) {
  return (
    <div className="space-y-6">
      {/* Health Profile Section */}
      {healthProfile && <HealthProfileSection data={healthProfile} />}
      
      {/* Health Indicators */}
      {healthProfile?.health_indicators && (
        <HealthIndicatorsSection indicators={healthProfile.health_indicators} />
      )}
      
      {/* Top Medications */}
      {healthProfile?.top_medications && (
        <TopMedicationsSection medications={healthProfile.top_medications} />
      )}
      
      {/* Care Home Considerations */}
      {healthProfile?.care_home_considerations && (
        <CareHomeConsiderationsSection considerations={healthProfile.care_home_considerations} />
      )}
      
      {/* Nearest Practices */}
      {nearestPractices && <NearestPracticesSection data={nearestPractices} />}
    </div>
  );
}

function HealthProfileSection({ data }: { data: NHSBSAHealthProfile }) {
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600 bg-green-100';
    if (score >= 50) return 'text-yellow-600 bg-yellow-100';
    if (score >= 30) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Activity className="w-4 h-4 text-red-500" />
        Area Health Profile
        <span className="text-sm font-normal text-gray-500">
          (Data period: {data.data_period})
        </span>
      </h4>
      
      {/* Health Index */}
      <div className="flex items-center gap-6 mb-4">
        <div className={`px-6 py-4 rounded-xl ${getScoreColor(data.health_index.score)}`}>
          <div className="text-4xl font-bold">{data.health_index.score}</div>
          <div className="text-sm">Health Index</div>
        </div>
        <div>
          <div className="text-xl font-semibold text-gray-800">{data.health_index.rating}</div>
          <div className="text-sm text-gray-600">{data.health_index.interpretation}</div>
          <div className="text-xs text-gray-500 mt-1">
            Percentile: {data.health_index.percentile}th
          </div>
        </div>
      </div>
      
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-red-50 rounded-lg p-3">
          <div className="flex items-center gap-2 text-red-600 mb-1">
            <Building2 className="w-4 h-4" />
            <span className="text-xs font-medium">Practices Analyzed</span>
          </div>
          <div className="text-2xl font-bold">{data.practices_analyzed}</div>
        </div>
        
        <div className="bg-red-50 rounded-lg p-3">
          <div className="flex items-center gap-2 text-red-600 mb-1">
            <Users className="w-4 h-4" />
            <span className="text-xs font-medium">Total Patients</span>
          </div>
          <div className="text-2xl font-bold">{data.total_patients.toLocaleString()}</div>
        </div>
        
        {data.nearest_practice && (
          <>
            <div className="bg-red-50 rounded-lg p-3 md:col-span-2">
              <div className="flex items-center gap-2 text-red-600 mb-1">
                <MapPin className="w-4 h-4" />
                <span className="text-xs font-medium">Nearest Practice</span>
              </div>
              <div className="text-sm font-bold">{data.nearest_practice.practice_name}</div>
              <div className="text-xs text-gray-500">{data.nearest_practice.address_1}</div>
            </div>
          </>
        )}
      </div>
      
      <div className="mt-3 text-xs text-gray-500 flex items-center gap-1">
        <Info className="w-3 h-3" />
        {data.methodology}
      </div>
    </div>
  );
}

function HealthIndicatorsSection({ indicators }: { indicators: NHSBSAHealthProfile['health_indicators'] }) {
  const [expanded, setExpanded] = useState(false);
  
  const displayIndicators = expanded 
    ? Object.entries(indicators) 
    : Object.entries(indicators).slice(0, 6);
  
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="w-3 h-3 text-orange-500" />;
      case 'decreasing': return <TrendingDown className="w-3 h-3 text-green-500" />;
      default: return <Minus className="w-3 h-3 text-gray-400" />;
    }
  };
  
  const getSignificanceColor = (significance: string) => {
    if (significance.includes('Higher')) return 'text-orange-600 bg-orange-100';
    if (significance.includes('Lower')) return 'text-green-600 bg-green-100';
    return 'text-gray-600 bg-gray-100';
  };
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Pill className="w-4 h-4 text-purple-500" />
        Prescribing Indicators
      </h4>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {displayIndicators.map(([category, data]) => (
          <div key={category} className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-sm capitalize">
                {category.replace('_', ' ')}
              </span>
              {getTrendIcon(data.trend)}
            </div>
            
            <div className="flex items-end gap-2 mb-1">
              <span className="text-2xl font-bold">{data.items_per_1000_patients}</span>
              <span className="text-xs text-gray-500 mb-1">per 1000 patients</span>
            </div>
            
            <div className="text-xs text-gray-500 mb-2">
              National avg: {data.national_average}
            </div>
            
            <div className="flex items-center justify-between">
              <span className={`text-xs px-2 py-0.5 rounded ${getSignificanceColor(data.significance)}`}>
                {data.vs_national_percent > 0 ? '+' : ''}{data.vs_national_percent}% vs national
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {Object.keys(indicators).length > 6 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-3 flex items-center gap-2 text-sm text-red-600 hover:text-red-800"
        >
          {expanded ? (
            <>
              <ChevronUp className="w-4 h-4" />
              Show less
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4" />
              Show all {Object.keys(indicators).length} indicators
            </>
          )}
        </button>
      )}
    </div>
  );
}

function TopMedicationsSection({ medications }: { medications: NHSBSAHealthProfile['top_medications'] }) {
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Pill className="w-4 h-4 text-blue-500" />
        Top 10 Prescribed Medications
      </h4>
      
      <div className="space-y-2">
        {medications.map((med, index) => {
          const maxItems = medications[0].items;
          const percentage = (med.items / maxItems) * 100;
          
          return (
            <div key={index} className="flex items-center gap-3">
              <span className="w-6 text-sm text-gray-400 text-right">{index + 1}</span>
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">{med.name}</span>
                  <span className="text-gray-500">{med.items.toLocaleString()} items</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CareHomeConsiderationsSection({ 
  considerations 
}: { 
  considerations: NHSBSAHealthProfile['care_home_considerations'] 
}) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-yellow-200 bg-yellow-50';
      default: return 'border-green-200 bg-green-50';
    }
  };
  
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'medium': return <Info className="w-4 h-4 text-yellow-500" />;
      default: return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Heart className="w-4 h-4 text-red-500" />
        Care Home Considerations
      </h4>
      
      <div className="space-y-3">
        {considerations.map((consideration, index) => (
          <div 
            key={index} 
            className={`border rounded-lg p-3 ${getPriorityColor(consideration.priority)}`}
          >
            <div className="flex items-start gap-3">
              {getPriorityIcon(consideration.priority)}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm">{consideration.category}</span>
                  <span className={`text-xs px-2 py-0.5 rounded capitalize ${
                    consideration.priority === 'high' ? 'bg-red-200 text-red-800' :
                    consideration.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-green-200 text-green-800'
                  }`}>
                    {consideration.priority} priority
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-1">{consideration.finding}</p>
                <p className="text-xs text-gray-600">
                  <strong>Implication:</strong> {consideration.implication}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function NearestPracticesSection({ data }: { data: NHSBSANearestPractices }) {
  const getAccessColor = (rating: string) => {
    switch (rating) {
      case 'Excellent': return 'bg-green-100 text-green-800';
      case 'Good': return 'bg-blue-100 text-blue-800';
      case 'Adequate': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-red-100 text-red-800';
    }
  };
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Building2 className="w-4 h-4 text-blue-500" />
        Nearest GP Practices
        <span className="text-sm font-normal text-gray-500">
          ({data.practices_found} within {data.search_radius_km}km)
        </span>
      </h4>
      
      {/* Healthcare Access Rating */}
      <div className={`mb-4 p-3 rounded-lg ${getAccessColor(data.healthcare_access_rating.rating)}`}>
        <div className="flex items-center justify-between">
          <span className="font-medium">Healthcare Access</span>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">{data.healthcare_access_rating.score}</span>
            <span className="text-sm">{data.healthcare_access_rating.rating}</span>
          </div>
        </div>
        <p className="text-sm mt-1">{data.healthcare_access_rating.description}</p>
      </div>
      
      {/* Practices List */}
      <div className="space-y-2">
        {data.nearest_practices.map((practice, index) => (
          <div 
            key={index}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <div className="font-medium text-sm">{practice.data.practice_name}</div>
              <div className="text-xs text-gray-500">{practice.data.address_1}</div>
              <div className="text-xs text-gray-500">{practice.data.postcode}</div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-600">
                {practice.distance_km.toFixed(2)} km
              </div>
              <div className="text-xs text-gray-500">
                {practice.data.patients_registered.toLocaleString()} patients
              </div>
              <div className={`text-xs ${practice.data.accepting_patients ? 'text-green-600' : 'text-red-600'}`}>
                {practice.data.accepting_patients ? 'Accepting patients' : 'Not accepting'}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Metadata */}
      <div className="mt-3 text-xs text-gray-500 flex items-center gap-1">
        <Clock className="w-3 h-3" />
        Fetched: {new Date(data.fetched_at).toLocaleString()}
      </div>
    </div>
  );
}
