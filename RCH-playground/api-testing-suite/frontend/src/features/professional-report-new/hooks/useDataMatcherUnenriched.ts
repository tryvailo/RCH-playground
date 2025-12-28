import axios from 'axios';
import type { ProfessionalQuestionnaireResponse, ProfessionalCareHome } from '../types';

/**
 * Match homes WITHOUT enrichment - uses only database data
 * This is the FIRST step: match candidates, then enrich only top-5
 * 
 * ✅ REFACTOR: New approach - match first, enrich later
 */
export async function matchHomesUnenriched(
  homes: ProfessionalCareHome[],
  questionnaire: ProfessionalQuestionnaireResponse,
  apiBaseUrl?: string
): Promise<ProfessionalCareHome[]> {
  try {
    console.log(`🎯 Matching ${homes.length} homes WITHOUT enrichment (database-only matching)`);
    
    // ✅ FIX: Use relative path through Vite proxy by default (like other features)
    const baseUrl = apiBaseUrl || (import.meta.env as any).VITE_API_URL || '';
    
    // Call backend endpoint for matching without enrichment
    try {
      console.log(`📡 Calling match-unenriched-homes endpoint: ${baseUrl}/api/match-unenriched-homes`);
      
      const response = await axios.post(
        `${baseUrl}/api/match-unenriched-homes`,
        {
          homes: homes, // Raw homes from database
          questionnaire: questionnaire
        },
        { 
          timeout: 30000,
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );
      
      // ✅ Validate response structure
      if (!response || !response.data) {
        throw new Error('Invalid backend response: missing data');
      }
      
      if (!Array.isArray(response.data.matched_homes)) {
        throw new Error('Invalid backend response: matched_homes is not an array');
      }
      
      // ✅ Check for empty matched homes
      if (response.data.matched_homes.length === 0) {
        console.warn('⚠️ Backend returned 0 matched homes, using fallback matching');
        return fallbackSimpleMatchingUnenriched(homes, questionnaire);
      }
      
      const backendHomes = response.data.matched_homes;
      console.log(`✅ Backend matched ${backendHomes.length} homes using database-only data`);
      
      // ✅ Validate each matched home structure
      const validHomes = backendHomes.filter((h: any) => {
        if (!h.home || h.matchScore === undefined) {
          console.warn('⚠️ Invalid matched home structure:', h);
          return false;
        }
        return true;
      });
      
      if (validHomes.length === 0) {
        console.warn('⚠️ No valid matched homes after validation, using fallback matching');
        return fallbackSimpleMatchingUnenriched(homes, questionnaire);
      }
      
      // Transform backend response to frontend format
      const matchedHomes = validHomes.map((backendMatch: any) => {
        // Find original home to preserve all data
        const originalHome = homes.find(
          (h) => h.name === backendMatch.home?.name || 
                 h.id === backendMatch.home?.id || 
                 h.id === backendMatch.home?.id
        );
        
        if (!originalHome) {
          console.warn('⚠️ Original home not found for matched home:', backendMatch.home?.name);
          return null;
        }
        
        return {
          ...originalHome,
          matchScore: backendMatch.matchScore || 0,
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
            : `Database Match Score: ${backendMatch.matchScore || 0}`,
          keyStrengths: extractKeyStrengthsFromBackend(originalHome, backendMatch),
        };
      }).filter((h): h is ProfessionalCareHome => h !== null);
      
      // Sort by match score and return ALL (not just top 5)
      // Top-30 will be selected in useProfessionalReportNew
      const rankedHomes = matchedHomes
        .filter(h => h.matchResult?.constraints_met !== false)
        .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
      
      if (rankedHomes.length === 0) {
        console.warn('⚠️ No homes passed constraints after matching, using fallback');
        return fallbackSimpleMatchingUnenriched(homes, questionnaire);
      }
      
      console.log(`✅ Database-only matching: ${rankedHomes.length} candidates scored`);
      return rankedHomes;
      
    } catch (backendError: any) {
      const errorMsg = backendError.response?.data?.detail || 
                       backendError.message || 
                       'Backend matching endpoint error';
      console.warn(`⚠️ Backend matching failed: ${errorMsg}`);
      console.warn('⚠️ Falling back to client-side simple matching...');
      
      // Fallback to simple scoring if backend unavailable
      return fallbackSimpleMatchingUnenriched(homes, questionnaire);
    }
    
  } catch (error) {
    console.error('❌ Matching failed with critical error:', error);
    // Return empty array with error instead of throwing
    return [];
  }
}

// Fallback: Simple scoring using only database data (no enrichment)
function fallbackSimpleMatchingUnenriched(
  homes: ProfessionalCareHome[],
  questionnaire: ProfessionalQuestionnaireResponse
): ProfessionalCareHome[] {
  console.warn('⚠️ Using fallback simple matching (database-only, no enrichment)');
  
  const scoredHomes = homes.map((home) => {
    let totalScore = 0;

    // Quality score (0-100) - uses only CQC rating from DB
    const qualityScore = calculateQualityScoreFromDB(home);
    totalScore += qualityScore * 0.35;

    // Cost score (0-100) - uses only weeklyPrice from DB
    const costScore = calculateCostScore(home, questionnaire);
    totalScore += costScore * 0.25;

    // Location score (0-100) - uses only distance from DB
    const locationScore = calculateLocationScore(home, questionnaire);
    totalScore += locationScore * 0.25;

    // Basic score (0-100) - uses only basic data
    const basicScore = 50; // Base score
    totalScore += basicScore * 0.15;

    return {
      ...home,
      matchScore: Math.round(totalScore),
      matchResult: {
        total_score: Math.round(totalScore),
        medical_score: 0, // Not available without enrichment
        safety_score: Math.round(qualityScore * 0.5), // Partial from CQC rating
        location_score: Math.round(locationScore),
        constraints_met: true,
        warnings: [],
      },
      whyChosen: `Fallback database scoring: ${Math.round(totalScore)} (enrichment unavailable)`,
      keyStrengths: extractKeyStrengthsFromDB(home),
    };
  });

  // Sort by match score descending and return ALL (not just top-5)
  const rankedHomes = scoredHomes
    .sort((a, b) => b.matchScore - a.matchScore);

  console.log(`⚠️ Fallback matched ${rankedHomes.length} homes (database-only)`);
  return rankedHomes;
}

function calculateQualityScoreFromDB(home: ProfessionalCareHome): number {
  let score = 50;
  
  // Use only CQC rating from database (no enriched data)
  if (home.cqcRating) {
    const rating = home.cqcRating.toLowerCase();
    if (rating === 'outstanding') score += 25;
    else if (rating === 'good') score += 20;
    else if (rating === 'requires improvement') score -= 10;
    else if (rating === 'inadequate') score -= 20;
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
  
  // Additional strengths from home data (database only)
  if (home.cqcRating?.toLowerCase() === 'good' ||
      home.cqcRating?.toLowerCase() === 'outstanding') {
    strengths.push('Outstanding CQC rating');
  }
  
  return strengths.slice(0, 3); // Top 3 strengths only
}

function extractKeyStrengthsFromDB(home: ProfessionalCareHome): string[] {
  const strengths: string[] = [];
  
  if (home.cqcRating?.toLowerCase() === 'good' || 
      home.cqcRating?.toLowerCase() === 'outstanding') {
    strengths.push('Strong CQC rating');
  }
  
  if (home.weeklyPrice <= 3000) {
    strengths.push('Competitive pricing');
  }
  
  const distanceKm = parseFloat(home.distance) || 0;
  if (distanceKm < 5) {
    strengths.push('Very close location');
  }
  
  return strengths;
}

