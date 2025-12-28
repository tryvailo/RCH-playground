import axios from 'axios';
import type { ProfessionalQuestionnaireResponse, ProfessionalCareHome } from '../types';

// Use Enhanced MVP algorithm from backend (100-point, medical+safety+location)
export async function matchHomes(
  enrichedHomes: ProfessionalCareHome[],
  questionnaire: ProfessionalQuestionnaireResponse,
  apiBaseUrl?: string
): Promise<ProfessionalCareHome[]> {
  try {
    console.log('🎯 Using Enhanced MVP algorithm (100-point, medical+safety+location)');
    
    // ✅ FIX: Use relative path through Vite proxy by default (like other features)
    const baseUrl = apiBaseUrl || (import.meta.env as any).VITE_API_URL || '';
    
    // Format homes for backend (convert frontend format to backend format)
    const homesForBackend = enrichedHomes.map(home => ({
      name: home.name,
      care_types: home.care_types || [],
      cqc_rating_safe: home.cqcDeepDive?.safe_rating || home.cqcDeepDive?.overall_rating || 'Unknown',
      cqc_rating_overall: home.cqcDeepDive?.overall_rating || 'Unknown',
      cqc_rating_effective: home.cqcDeepDive?.effective_rating,
      cqc_rating_caring: home.cqcDeepDive?.caring_rating,
      fsa_rating: home.fsa_rating,
      distance_km: parseFloat(home.distance) || 0,
      google_rating: home.googlePlaces?.rating,
      google_reviews_count: home.googlePlaces?.review_count,
      has_wheelchair_access: home.wheelchairAccessible || false,
      has_hoist: home.hasHoist || false,
      has_hospital_bed: home.hasHospitalBed || false,
      has_nursing_staff: home.hasNursingStaff || false,
      registration_type: home.registrationType,
      // Include all fields from original home object
      ...home,
    }));
    
    // ✅ FIX: Use new endpoint that accepts pre-enriched homes (no duplicate DB load)
    try {
      console.log(`📡 Calling match-enriched-homes endpoint: ${baseUrl}/api/match-enriched-homes`);
      
      const response = await axios.post(
        `${baseUrl}/api/match-enriched-homes`,
        {
          enriched_homes: enrichedHomes,
          questionnaire: questionnaire
        },
        { 
          timeout: 30000, // 30 second timeout
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );
      
      // ✅ FIX: Validate response structure
      if (!response || !response.data) {
        throw new Error('Invalid backend response: missing data');
      }
      
      if (!Array.isArray(response.data.matched_homes)) {
        throw new Error('Invalid backend response: matched_homes is not an array');
      }
      
      // ✅ FIX: Check for empty matched homes
      if (response.data.matched_homes.length === 0) {
        console.warn('⚠️ Backend returned 0 matched homes, falling back to simple matching');
        return fallbackSimpleMatching(enrichedHomes, questionnaire);
      }
      
      const backendHomes = response.data.matched_homes;
      console.log(`✅ Backend matched ${backendHomes.length} homes using Enhanced MVP (no duplicate DB load)`);
      
      // ✅ FIX: Validate each matched home structure
      const validHomes = backendHomes.filter((h: any) => {
        if (!h.home || !h.matchScore) {
          console.warn('⚠️ Invalid matched home structure:', h);
          return false;
        }
        return true;
      });
      
      if (validHomes.length === 0) {
        console.warn('⚠️ No valid matched homes after validation, falling back to simple matching');
        return fallbackSimpleMatching(enrichedHomes, questionnaire);
      }
      
      // Transform backend response to frontend format
      const matchedHomes = validHomes.map((backendMatch: any) => {
          // Find original enriched home to preserve all enrichment data
          const originalHome = enrichedHomes.find(
            (h) => h.name === backendMatch.home?.name || h.id === backendMatch.home?.id || h.id === backendMatch.home?.id
          ) || enrichedHomes[0]; // Fallback to first if not found
          
          return {
            ...originalHome,
            matchScore: backendMatch.matchScore || Math.round(
              (backendMatch.factorScores?.medical || 0) * 0.3 +
              (backendMatch.factorScores?.safety || 0) * 0.4 +
              (backendMatch.factorScores?.location || 0) * 0.25
            ),
            matchResult: backendMatch.matchResult || {
              total_score: backendMatch.matchScore || 0,
              medical_score: backendMatch.factorScores?.medical || 0,
              safety_score: backendMatch.factorScores?.safety || 0,
              location_score: backendMatch.factorScores?.location || 0,
              constraints_met: backendMatch.matchResult?.constraints_met !== false,
              warnings: backendMatch.matchResult?.warnings || []
            },
            whyChosen: backendMatch.matchResult?.constraints_met === false
              ? `Eliminated: ${(backendMatch.matchResult?.warnings || []).join(', ')}`
              : `Enhanced MVP Score: ${backendMatch.matchScore || 0} (Medical: ${backendMatch.factorScores?.medical || 0}, Safety: ${backendMatch.factorScores?.safety || 0}, Location: ${backendMatch.factorScores?.location || 0})`,
            keyStrengths: extractKeyStrengthsFromBackend(originalHome, backendMatch),
          };
        });
        
        // Sort by match score and return top 5
        const rankedHomes = matchedHomes
          .filter(h => h.matchResult?.constraints_met !== false) // Filter out homes that failed constraints
          .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
          .slice(0, 5);
        
        // ✅ FIX: Final validation before returning
        if (rankedHomes.length === 0) {
          console.warn('⚠️ No homes passed constraints after matching, falling back to simple matching');
          return fallbackSimpleMatching(enrichedHomes, questionnaire);
        }
        
        console.log(`✅ Enhanced MVP matched ${rankedHomes.length} homes successfully`);
        return rankedHomes;
      
    } catch (backendError: any) {
      const errorMsg = backendError.response?.data?.detail || 
                       backendError.message || 
                       'Backend Enhanced MVP endpoint error';
      console.warn(`⚠️ Backend Enhanced MVP failed: ${errorMsg}`);
      console.warn('⚠️ Falling back to client-side simple matching...');
      
      // Fallback to simple scoring if backend unavailable
      return fallbackSimpleMatching(enrichedHomes, questionnaire);
    }
    
  } catch (error) {
    console.error('❌ Matching failed with critical error:', error);
    // Return empty array with error instead of throwing
    return [];
  }
}

// ✅ FIX: Improved fallback matching that uses enriched data and medical needs
function fallbackSimpleMatching(
  enrichedHomes: ProfessionalCareHome[],
  questionnaire: ProfessionalQuestionnaireResponse
): ProfessionalCareHome[] {
  console.warn('⚠️ Using fallback simple matching (Enhanced MVP backend unavailable)');
  
  const medicalConditions = questionnaire.section_3_medical_needs?.q9_medical_conditions || [];
  const careTypes = questionnaire.section_3_medical_needs?.q8_care_types || [];
  const mobilityLevel = questionnaire.section_3_medical_needs?.q10_mobility_level || '';
  
  const scoredHomes = enrichedHomes.map((home) => {
    let totalScore = 0;

    // Quality/Reputation score (0-100) - uses enriched CQC and Google data
    const qualityScore = calculateQualityScore(home);
    totalScore += qualityScore * 0.35;

    // ✅ FIX: Medical match score - uses enriched data and medical conditions
    const medicalScore = calculateMedicalMatchScore(home, medicalConditions, careTypes, mobilityLevel);
    totalScore += medicalScore * 0.30; // Increased weight for medical match

    // Safety score (0-100) - uses enriched CQC and FSA data
    const safetyScore = calculateSafetyScore(home);
    totalScore += safetyScore * 0.20;

    // Cost score (0-100)
    const costScore = calculateCostScore(home, questionnaire);
    totalScore += costScore * 0.10;

    // Location score (0-100)
    const locationScore = calculateLocationScore(home, questionnaire);
    totalScore += locationScore * 0.05;

    return {
      ...home,
      matchScore: Math.round(totalScore),
      matchResult: {
        total_score: Math.round(totalScore),
        medical_score: Math.round(medicalScore),
        safety_score: Math.round(safetyScore),
        location_score: Math.round(locationScore),
        constraints_met: true,
        warnings: [],
      },
      whyChosen: `Fallback scoring: ${Math.round(totalScore)} (Medical: ${Math.round(medicalScore)}, Safety: ${Math.round(safetyScore)})`,
      keyStrengths: extractKeyStrengths(home, questionnaire),
    };
  });

  // Sort by match score descending
  const rankedHomes = scoredHomes
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 5);

  console.log(`⚠️ Fallback matched ${rankedHomes.length} homes`);
  return rankedHomes;
}

function extractKeyStrengthsFromBackend(
  home: ProfessionalCareHome,
  backendMatch: any
): string[] {
  const strengths: string[] = [];
  
  const medicalScore = backendMatch.factorScores?.medical || 0;
  const safetyScore = backendMatch.factorScores?.safety || 0;
  const locationScore = backendMatch.factorScores?.location || 0;
  
  // Medical match strength
  if (medicalScore >= 25) {
    strengths.push('Strong medical match');
  }
  
  // Safety strength
  if (safetyScore >= 30) {
    strengths.push('Excellent safety rating');
  }
  
  // Location strength
  if (locationScore >= 15) {
    strengths.push('Convenient location');
  }
  
  // Additional strengths from home data
  if (home.cqcDeepDive?.overall_rating?.toLowerCase() === 'good' ||
      home.cqcDeepDive?.overall_rating?.toLowerCase() === 'outstanding') {
    strengths.push('Outstanding CQC rating');
  }
  
  if (home.googlePlaces?.rating && home.googlePlaces.rating >= 4.5) {
    strengths.push('Highly rated by community');
  }
  
  return strengths.slice(0, 3); // Top 3 strengths only
}

function calculateQualityScore(home: ProfessionalCareHome): number {
  let score = 50;
  
  if (home.cqcDeepDive?.overall_rating) {
    const rating = home.cqcDeepDive.overall_rating.toLowerCase();
    if (rating === 'outstanding') score += 25;
    else if (rating === 'good') score += 20;
    else if (rating === 'requires improvement') score -= 10;
    else if (rating === 'inadequate') score -= 20;
  }
  
  if (home.googlePlaces?.rating) {
    score += Math.min(home.googlePlaces.rating * 3, 25);
  }
  
  return Math.max(0, Math.min(100, score));
}

function calculateCostScore(home: ProfessionalCareHome, questionnaire: ProfessionalQuestionnaireResponse): number {
  let score = 50;
  
  const budget = parseInt(questionnaire.section_2_location_budget.q7_budget) || 3000;
  if (home.weeklyPrice <= budget) {
    score += 30;
  } else if (home.weeklyPrice <= budget * 1.2) {
    score += 15;
  } else {
    score -= 20;
  }
  
  return Math.max(0, Math.min(100, score));
}

function calculateLocationScore(home: ProfessionalCareHome, questionnaire: ProfessionalQuestionnaireResponse): number {
  let score = 50;
  
  const distanceKm = parseFloat(home.distance) || 0;
  if (distanceKm < 5) score += 25;
  else if (distanceKm < 15) score += 15;
  else if (distanceKm < 30) score += 5;
  
  return Math.max(0, Math.min(100, score));
}

function calculateComfortScore(home: ProfessionalCareHome): number {
  let score = 50;
  
  if (home.keyStrengths && home.keyStrengths.length > 0) {
    score += Math.min(home.keyStrengths.length * 5, 25);
  }
  
  return Math.max(0, Math.min(100, score));
}

// ✅ FIX: Calculate medical match score using enriched data
function calculateMedicalMatchScore(
  home: ProfessionalCareHome,
  medicalConditions: string[],
  careTypes: string[],
  mobilityLevel: string
): number {
  let score = 50; // Base score
  
  // Check if home supports required care types (from enriched data)
  if (home.medicalCare) {
    const homeCareTypes = home.medicalCare.service_types || [];
    const hasRequiredCare = careTypes.some(ct => 
      homeCareTypes.some(hct => 
        hct.toLowerCase().includes(ct.toLowerCase())
      )
    );
    if (hasRequiredCare) score += 20;
  }
  
  // Check CQC ratings for medical care quality
  if (home.cqcDeepDive) {
    const effectiveRating = home.cqcDeepDive.effective_rating || home.cqcDeepDive.overall_rating;
    if (effectiveRating?.toLowerCase() === 'outstanding') score += 15;
    else if (effectiveRating?.toLowerCase() === 'good') score += 10;
  }
  
  // Check for dementia care if needed
  if (medicalConditions.some(c => c.toLowerCase().includes('dementia'))) {
    if (home.medicalCare?.care_dementia) score += 15;
  }
  
  // Check for nursing care if needed
  if (careTypes.some(ct => ct.toLowerCase().includes('nursing'))) {
    if (home.medicalCare?.care_nursing) score += 15;
  }
  
  // Mobility considerations
  if (mobilityLevel && (mobilityLevel.toLowerCase().includes('wheelchair') || mobilityLevel.toLowerCase().includes('limited'))) {
    if (home.wheelchairAccessible) score += 10;
  }
  
  return Math.max(0, Math.min(100, score));
}

// ✅ FIX: Calculate safety score using enriched CQC and FSA data
function calculateSafetyScore(home: ProfessionalCareHome): number {
  let score = 50; // Base score
  
  // CQC safety rating
  if (home.cqcDeepDive) {
    const safeRating = home.cqcDeepDive.safe_rating || home.cqcDeepDive.overall_rating;
    if (safeRating?.toLowerCase() === 'outstanding') score += 25;
    else if (safeRating?.toLowerCase() === 'good') score += 20;
    else if (safeRating?.toLowerCase() === 'requires improvement') score -= 15;
    else if (safeRating?.toLowerCase() === 'inadequate') score -= 25;
  }
  
  // FSA food hygiene rating
  if (home.fsaDetailed?.rating) {
    const fsaRating = home.fsaDetailed.rating;
    if (fsaRating >= 5) score += 15;
    else if (fsaRating >= 4) score += 10;
    else if (fsaRating <= 2) score -= 10;
  }
  
  // Safety analysis from enriched data
  if (home.safetyAnalysis?.safety_score) {
    score = (score + home.safetyAnalysis.safety_score) / 2; // Average with safety score
  }
  
  return Math.max(0, Math.min(100, score));
}

function extractKeyStrengths(home: ProfessionalCareHome, questionnaire: ProfessionalQuestionnaireResponse): string[] {
  const strengths: string[] = [];
  
  // ✅ FIX: Use enriched data for strengths
  if (home.cqcDeepDive?.overall_rating?.toLowerCase() === 'good' || 
      home.cqcDeepDive?.overall_rating?.toLowerCase() === 'outstanding') {
    strengths.push('Strong CQC rating');
  }
  
  if (home.googlePlaces?.rating && home.googlePlaces.rating >= 4.5) {
    strengths.push('Excellent community reviews');
  }
  
  if (home.fsaDetailed?.rating && home.fsaDetailed.rating >= 4) {
    strengths.push('Good food hygiene rating');
  }
  
  if (home.financialStability?.financial_health === 'healthy') {
    strengths.push('Financially stable');
  }
  
  if (home.weeklyPrice <= 3000) {
    strengths.push('Competitive pricing');
  }
  
  // Medical care strengths
  const medicalConditions = questionnaire.section_3_medical_needs?.q9_medical_conditions || [];
  if (medicalConditions.length > 0 && home.medicalCare) {
    if (home.medicalCare.care_dementia && medicalConditions.some(c => c.toLowerCase().includes('dementia'))) {
      strengths.push('Specialized dementia care');
    }
    if (home.medicalCare.care_nursing) {
      strengths.push('Nursing care available');
    }
  }
  
  return strengths.slice(0, 4); // Top 4 strengths
}
