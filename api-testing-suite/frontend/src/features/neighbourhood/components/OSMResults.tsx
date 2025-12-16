import { 
  TreePine, 
  MapPin, 
  Clock, 
  ShoppingCart,
  Coffee,
  UtensilsCrossed,
  Building,
  Landmark,
  Heart,
  GraduationCap,
  BookOpen,
  Film,
  Bus,
  Footprints,
  Lightbulb,
  CheckCircle,
  XCircle,
  ChevronUp,
  Info
} from 'lucide-react';
import { useState } from 'react';
import type { OSMWalkScore, OSMAmenitiesResult, OSMInfrastructure } from '../types';

interface Props {
  walkScore?: OSMWalkScore;
  amenities?: OSMAmenitiesResult;
  infrastructure?: OSMInfrastructure;
}

export default function OSMResults({ walkScore, amenities, infrastructure }: Props) {
  return (
    <div className="space-y-6">
      {/* Walk Score Section */}
      {walkScore && <WalkScoreSection data={walkScore} />}
      
      {/* Care Home Relevance */}
      {walkScore?.care_home_relevance && (
        <CareHomeRelevanceSection data={walkScore.care_home_relevance} />
      )}
      
      {/* Amenities Section */}
      {amenities && <AmenitiesSection data={amenities} />}
      
      {/* Infrastructure Section */}
      {infrastructure && <InfrastructureSection data={infrastructure} />}
    </div>
  );
}

function WalkScoreSection({ data }: { data: OSMWalkScore }) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-blue-600 bg-blue-100';
    if (score >= 50) return 'text-yellow-600 bg-yellow-100';
    if (score >= 25) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Footprints className="w-4 h-4 text-green-500" />
        Walk Score
      </h4>
      
      {/* Main Score */}
      <div className="flex items-center gap-6 mb-4">
        <div className={`px-6 py-4 rounded-xl ${getScoreColor(data.walk_score)}`}>
          <div className="text-4xl font-bold">{data.walk_score}</div>
          <div className="text-sm">out of 100</div>
        </div>
        <div>
          <div className="text-xl font-semibold text-gray-800">{data.rating}</div>
          <div className="text-sm text-gray-600">{data.description}</div>
        </div>
      </div>
      
      {/* Highlights */}
      {data.highlights && data.highlights.length > 0 && (
        <div className="mb-4 p-3 bg-green-50 rounded-lg">
          <div className="text-sm font-medium text-green-800 mb-2">Highlights</div>
          <ul className="space-y-1">
            {data.highlights.map((highlight, i) => (
              <li key={i} className="text-sm text-green-700 flex items-start gap-2">
                <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                {highlight}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Category Breakdown */}
      <div>
        <div className="text-sm font-medium text-gray-700 mb-3">Category Breakdown</div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {data.category_breakdown && Object.entries(data.category_breakdown).map(([category, info]) => (
            <CategoryScoreCard 
              key={category} 
              category={category} 
              score={info.score}
              count={info.count}
              nearest={info.nearest_m}
            />
          ))}
        </div>
      </div>
      
      <div className="mt-3 text-xs text-gray-500 flex items-center gap-1">
        <Info className="w-3 h-3" />
        {data.methodology}
      </div>
    </div>
  );
}

function CategoryScoreCard({ 
  category, 
  score, 
  count,
  nearest 
}: { 
  category: string; 
  score: number;
  count: number;
  nearest: number | null;
}) {
  const icons: Record<string, React.ReactNode> = {
    grocery: <ShoppingCart className="w-4 h-4" />,
    restaurants: <UtensilsCrossed className="w-4 h-4" />,
    shopping: <Building className="w-4 h-4" />,
    coffee: <Coffee className="w-4 h-4" />,
    banks: <Landmark className="w-4 h-4" />,
    parks: <TreePine className="w-4 h-4" />,
    schools: <GraduationCap className="w-4 h-4" />,
    books: <BookOpen className="w-4 h-4" />,
    entertainment: <Film className="w-4 h-4" />,
    healthcare: <Heart className="w-4 h-4" />,
  };
  
  const getScoreBg = (s: number) => {
    if (s >= 70) return 'bg-green-100';
    if (s >= 40) return 'bg-yellow-100';
    return 'bg-gray-100';
  };
  
  return (
    <div className={`rounded-lg p-3 ${getScoreBg(score)}`}>
      <div className="flex items-center gap-2 mb-1">
        {icons[category] || <MapPin className="w-4 h-4" />}
        <span className="text-sm font-medium capitalize">{category}</span>
      </div>
      <div className="text-lg font-bold">{Math.round(score)}</div>
      <div className="text-xs text-gray-600">
        {count} found {nearest && `• ${nearest}m nearest`}
      </div>
    </div>
  );
}

function CareHomeRelevanceSection({ data }: { data: OSMWalkScore['care_home_relevance'] }) {
  const getRelevanceColor = (rating: string) => {
    if (rating.includes('Excellent')) return 'bg-green-50 border-green-200';
    if (rating.includes('Good')) return 'bg-blue-50 border-blue-200';
    if (rating.includes('Adequate')) return 'bg-yellow-50 border-yellow-200';
    return 'bg-gray-50 border-gray-200';
  };
  
  return (
    <div className={`border rounded-lg p-4 ${getRelevanceColor(data.rating)}`}>
      <h4 className="font-medium text-gray-800 mb-3">Care Home Suitability</h4>
      
      <div className="flex items-center gap-4 mb-4">
        <div className="text-3xl font-bold">{data.score}</div>
        <div>
          <div className="font-semibold">{data.rating}</div>
        </div>
      </div>
      
      {/* Key Factors */}
      <div className="mb-4">
        <div className="text-sm font-medium mb-2">Key Factors</div>
        <ul className="space-y-1">
          {data.key_factors.map((factor, i) => (
            <li key={i} className="text-sm flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
              {factor}
            </li>
          ))}
        </ul>
      </div>
      
      {/* Access Ratings */}
      <div className="grid grid-cols-3 gap-3">
        <AccessRating label="Healthcare" status={data.healthcare_access} />
        <AccessRating label="Outdoor Spaces" status={data.outdoor_spaces} />
        <AccessRating label="Dining Options" status={data.dining_options} />
      </div>
    </div>
  );
}

function AccessRating({ label, status }: { label: string; status: string }) {
  const isGood = status === 'Good' || status === 'Available';
  
  return (
    <div className={`rounded p-2 text-center ${isGood ? 'bg-green-100' : 'bg-gray-100'}`}>
      <div className="text-xs text-gray-600">{label}</div>
      <div className={`text-sm font-medium ${isGood ? 'text-green-700' : 'text-gray-700'}`}>
        {status}
      </div>
    </div>
  );
}

function AmenitiesSection({ data }: { data: OSMAmenitiesResult }) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  
  const categoryIcons: Record<string, React.ReactNode> = {
    grocery: <ShoppingCart className="w-4 h-4" />,
    restaurants: <UtensilsCrossed className="w-4 h-4" />,
    shopping: <Building className="w-4 h-4" />,
    coffee: <Coffee className="w-4 h-4" />,
    banks: <Landmark className="w-4 h-4" />,
    parks: <TreePine className="w-4 h-4" />,
    schools: <GraduationCap className="w-4 h-4" />,
    books: <BookOpen className="w-4 h-4" />,
    entertainment: <Film className="w-4 h-4" />,
    healthcare: <Heart className="w-4 h-4" />,
  };
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <MapPin className="w-4 h-4 text-blue-500" />
        Nearby Amenities
        <span className="text-sm font-normal text-gray-500">
          ({data.total_amenities} found within {data.radius_m}m)
        </span>
      </h4>
      
      {/* Summary Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
        {data.summary && Object.entries(data.summary).map(([category, info]) => (
          <button
            key={category}
            onClick={() => setExpandedCategory(expandedCategory === category ? null : category)}
            className={`text-left rounded-lg p-3 transition-colors ${
              expandedCategory === category ? 'bg-blue-100' : 'bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              {categoryIcons[category] || <MapPin className="w-4 h-4" />}
              <span className="text-xs font-medium capitalize">{category}</span>
            </div>
            <div className="text-lg font-bold">{info.count}</div>
            <div className="text-xs text-gray-500">
              {info.within_400m} within 5 min
            </div>
          </button>
        ))}
      </div>
      
      {/* Expanded Category Details */}
      {expandedCategory && data.by_category[expandedCategory as keyof typeof data.by_category] && (
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <h5 className="font-medium capitalize">{expandedCategory} Details</h5>
            <button 
              onClick={() => setExpandedCategory(null)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              <ChevronUp className="w-4 h-4" />
            </button>
          </div>
          <div className="max-h-60 overflow-y-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left">Name</th>
                  <th className="px-3 py-2 text-left">Type</th>
                  <th className="px-3 py-2 text-right">Distance</th>
                  <th className="px-3 py-2 text-left">Wheelchair</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data.by_category[expandedCategory as keyof typeof data.by_category]?.map((amenity, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{amenity.name}</td>
                    <td className="px-3 py-2 text-gray-500">{amenity.type}</td>
                    <td className="px-3 py-2 text-right font-mono">{amenity.distance_m}m</td>
                    <td className="px-3 py-2">
                      {amenity.wheelchair === 'yes' ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : amenity.wheelchair === 'no' ? (
                        <XCircle className="w-4 h-4 text-red-500" />
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function InfrastructureSection({ data }: { data: OSMInfrastructure }) {
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Bus className="w-4 h-4 text-purple-500" />
        Infrastructure & Safety
      </h4>
      
      {/* Safety Score */}
      <div className="mb-4 p-3 bg-purple-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm text-purple-800">Safety Score</span>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-purple-600">{data.safety_score}</span>
            <span className={`px-2 py-0.5 text-xs rounded-full ${
              data.safety_rating === 'Good' ? 'bg-green-200 text-green-800' :
              data.safety_rating === 'Average' ? 'bg-yellow-200 text-yellow-800' :
              'bg-red-200 text-red-800'
            }`}>
              {data.safety_rating}
            </span>
          </div>
        </div>
      </div>
      
      {/* Infrastructure Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Public Transport */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Bus className="w-4 h-4 text-blue-500" />
            <span className="font-medium text-sm">Public Transport</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Bus stops (800m)</span>
              <span className="font-medium">{data.public_transport.bus_stops_800m}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Rail stations (1.6km)</span>
              <span className="font-medium">{data.public_transport.rail_stations_1600m}</span>
            </div>
            <div className={`text-center py-1 rounded ${
              data.public_transport.rating === 'Good' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            }`}>
              {data.public_transport.rating}
            </div>
          </div>
        </div>
        
        {/* Pedestrian Safety */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Footprints className="w-4 h-4 text-green-500" />
            <span className="font-medium text-sm">Pedestrian Safety</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Crossings</span>
              <span className="font-medium">{data.pedestrian_safety.pedestrian_crossings}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Lit roads</span>
              <span className="font-medium">{data.pedestrian_safety.lit_roads_nearby}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Footways</span>
              <span className="font-medium">{data.pedestrian_safety.footways}</span>
            </div>
          </div>
        </div>
        
        {/* Accessibility */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="w-4 h-4 text-yellow-500" />
            <span className="font-medium text-sm">Accessibility</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Benches nearby</span>
              <span className="font-medium">{data.accessibility.benches_nearby}</span>
            </div>
            <div className={`text-center py-1 rounded ${
              data.accessibility.rest_points === 'Available' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            }`}>
              Rest points: {data.accessibility.rest_points}
            </div>
          </div>
        </div>
      </div>
      
      {/* Metadata */}
      <div className="mt-3 text-xs text-gray-500 flex items-center gap-1">
        <Clock className="w-3 h-3" />
        Fetched: {new Date(data.fetched_at).toLocaleString()}
      </div>
    </div>
  );
}
