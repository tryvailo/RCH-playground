/**
 * Medical Calculator
 * Scores home's medical capabilities (0-30 points)
 * Ported from Python services/matching/calculators/medical_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class MedicalCalculator extends CategoryCalculator {
  readonly categoryName = 'medical';
  readonly maxPoints = 30.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      const medicalNeeds = userProfile?.section_3_medical_needs || {};
      const medicalConditions = medicalNeeds.q9_medical_conditions || [];
      const careTypes = medicalNeeds.q8_care_types || [];
      const mobilityLevel = medicalNeeds.q10_mobility_level || '';

      // 1. Specialist care match (10 points)
      const specialistScore = await this.scoreSpecialistCare(
        home,
        medicalConditions,
        enrichedData
      );
      score += specialistScore;

      // 2. Nursing level (8 points)
      const nursingScore = await this.scoreNursingLevel(
        home,
        careTypes,
        enrichedData
      );
      score += nursingScore;

      // 3. Medical equipment (7 points)
      const equipmentScore = await this.scoreEquipment(home, enrichedData);
      score += equipmentScore;

      // 4. Emergency protocols (5 points)
      const emergencyScore = await this.scoreEmergency(
        home,
        medicalNeeds.q11_medication_management,
        enrichedData
      );
      score += emergencyScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating medical score: ${error}`);
      return 0.0;
    }
  }

  private async scoreSpecialistCare(
    home: any,
    medicalConditions: string[],
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    const homeCareTypes = this.safeList(home.care_types);
    const homeCareTypesStr = homeCareTypes.join(' ').toLowerCase();
    const homeNameLower = this.normalizeString(home.name);

    // Dementia care (4 points)
    if (medicalConditions.includes('dementia_alzheimers')) {
      if (
        this.checkContains(homeCareTypesStr, 'dementia') ||
        home.care_dementia ||
        this.checkContains(homeNameLower, 'dementia') ||
        this.extractField(enrichedData, 'cqc_detailed', 'dementia_care')
      ) {
        score += 4.0;
      }
    }

    // Diabetes care (2 points)
    if (medicalConditions.includes('diabetes')) {
      if (
        this.checkContains(homeCareTypesStr, 'diabetes') ||
        this.extractField(enrichedData, 'medical', 'diabetes_support')
      ) {
        score += 2.0;
      }
    }

    // Cardiac care (2 points)
    if (medicalConditions.includes('cardiac')) {
      if (
        this.checkContains(homeCareTypesStr, 'cardiac') ||
        this.extractField(enrichedData, 'medical', 'cardiac_support')
      ) {
        score += 2.0;
      }
    }

    // Mobility support (2 points)
    if (medicalConditions.includes('mobility_issues')) {
      if (
        this.extractField(enrichedData, 'medical', 'mobility_support') ||
        home.mobility_support
      ) {
        score += 2.0;
      }
    }

    return Math.min(score, 10.0);
  }

  private async scoreNursingLevel(
    home: any,
    careTypes: string[],
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    // Check if nursing care needed
    const needsNursing =
      careTypes.includes('nursing') || careTypes.includes('general_nursing');

    if (needsNursing) {
      // Check if home provides nursing
      const homeCareTypes = this.safeList(home.care_types);
      const hasNursing = homeCareTypes.some((ct: string) =>
        this.normalizeString(ct).includes('nursing')
      );

      if (hasNursing) {
        score += 5.0; // Base nursing match

        // RN count bonus (3 points)
        const rnCount = this.safeInt(
          this.extractField(enrichedData, 'staff', 'rn_count'),
          0
        );
        if (rnCount >= 3) {
          score += 3.0;
        } else if (rnCount >= 1) {
          score += 1.5;
        }
      }
    }

    return Math.min(score, 8.0);
  }

  private async scoreEquipment(
    home: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    // Medical equipment availability
    const equipment = this.extractField(enrichedData, 'medical', 'equipment');
    if (equipment) {
      const equipmentList = this.safeList(equipment);
      if (equipmentList.length >= 5) {
        score += 7.0;
      } else if (equipmentList.length >= 3) {
        score += 4.0;
      } else if (equipmentList.length >= 1) {
        score += 2.0;
      }
    }

    return Math.min(score, 7.0);
  }

  private async scoreEmergency(
    home: any,
    medicationNeeds: string,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    // Emergency protocols
    const hasProtocols = this.extractField(
      enrichedData,
      'medical',
      'emergency_protocols'
    );
    if (hasProtocols) {
      score += 3.0;
    }

    // Medication management
    if (medicationNeeds && medicationNeeds !== 'none') {
      const hasMedManagement = this.extractField(
        enrichedData,
        'medical',
        'medication_management'
      );
      if (hasMedManagement) {
        score += 2.0;
      }
    }

    return Math.min(score, 5.0);
  }
}



