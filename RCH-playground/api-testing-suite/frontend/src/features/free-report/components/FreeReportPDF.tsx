import React from 'react';
import { Document, Page, Text, View, StyleSheet, Image } from '@react-pdf/renderer';
import type { FreeReportData, CareHomeData, QuestionnaireResponse } from '../types';

// Note: @react-pdf/renderer uses Helvetica by default, which is similar to Inter
// For custom fonts, you would need to download and register them locally

// Styles
const styles = StyleSheet.create({
  page: {
    fontFamily: 'Helvetica',
    padding: 40,
    backgroundColor: '#FFFFFF',
  },
  header: {
    backgroundColor: '#1E2A44',
    color: '#FFFFFF',
    padding: 30,
    marginBottom: 30,
    borderRadius: 8,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 700,
    marginBottom: 10,
    color: '#FFFFFF',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#E5E7EB',
    marginBottom: 20,
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  summaryBox: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 15,
    borderRadius: 6,
    flex: 1,
    marginHorizontal: 5,
  },
  summaryLabel: {
    fontSize: 10,
    color: '#D1D5DB',
    marginBottom: 5,
  },
  summaryValue: {
    fontSize: 20,
    fontWeight: 700,
    color: '#FFFFFF',
  },
  chcBox: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    padding: 15,
    borderRadius: 6,
    marginTop: 15,
    border: '1px solid rgba(16, 185, 129, 0.3)',
  },
  chcLabel: {
    fontSize: 10,
    color: '#D1FAE5',
    marginBottom: 5,
  },
  chcValue: {
    fontSize: 28,
    fontWeight: 700,
    color: '#10B981',
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: 700,
    color: '#111827',
    marginBottom: 20,
    marginTop: 10,
  },
  homeCard: {
    marginBottom: 30,
    border: '1px solid #E5E7EB',
    borderRadius: 8,
    overflow: 'hidden',
  },
  homeImage: {
    width: '100%',
    height: 200,
    objectFit: 'cover',
  },
  homeImagePlaceholder: {
    width: '100%',
    height: 200,
    backgroundColor: '#F3F4F6',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  homeContent: {
    padding: 25,
  },
  homeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  homeName: {
    fontSize: 22,
    fontWeight: 700,
    color: '#111827',
    flex: 1,
  },
  badge: {
    backgroundColor: '#FFFFFF',
    padding: '5px 12px',
    borderRadius: 20,
    fontSize: 10,
    fontWeight: 600,
    color: '#1E2A44',
    marginLeft: 10,
  },
  matchBadge: {
    padding: '4px 10px',
    borderRadius: 4,
    fontSize: 9,
    fontWeight: 600,
    marginTop: 5,
  },
  matchBadgeSafe: {
    backgroundColor: '#DBEAFE',
    color: '#1E40AF',
  },
  matchBadgeValue: {
    backgroundColor: '#D1FAE5',
    color: '#065F46',
  },
  matchBadgePremium: {
    backgroundColor: '#F3E8FF',
    color: '#6B21A8',
  },
  priceSection: {
    marginBottom: 20,
    paddingBottom: 15,
    borderBottom: '1px solid #E5E7EB',
  },
  priceMain: {
    fontSize: 36,
    fontWeight: 700,
    color: '#1E2A44',
    marginBottom: 5,
  },
  priceRange: {
    fontSize: 12,
    color: '#6B7280',
  },
  whySection: {
    marginTop: 15,
    padding: 15,
    backgroundColor: '#F9FAFB',
    borderRadius: 6,
  },
  whyTitle: {
    fontSize: 12,
    fontWeight: 600,
    color: '#111827',
    marginBottom: 8,
  },
  whyText: {
    fontSize: 11,
    color: '#374151',
    lineHeight: 1.6,
  },
  detailsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 15,
  },
  detailItem: {
    flex: 1,
  },
  detailLabel: {
    fontSize: 9,
    color: '#6B7280',
    marginBottom: 3,
  },
  detailValue: {
    fontSize: 11,
    fontWeight: 600,
    color: '#111827',
  },
  fairCostGapPage: {
    backgroundColor: '#EF4444',
    color: '#FFFFFF',
    padding: 50,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100%',
  },
  fairCostGapTitle: {
    fontSize: 48,
    fontWeight: 700,
    color: '#FFFFFF',
    marginBottom: 30,
    textAlign: 'center',
  },
  fairCostGapMain: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 40,
    borderRadius: 12,
    marginBottom: 30,
    border: '2px solid rgba(255, 255, 255, 0.2)',
  },
  fairCostGapLabel: {
    fontSize: 18,
    color: '#FEE2E2',
    marginBottom: 10,
  },
  fairCostGapValue: {
    fontSize: 72,
    fontWeight: 700,
    color: '#FFFFFF',
    marginBottom: 20,
  },
  fairCostGapSub: {
    fontSize: 24,
    fontWeight: 600,
    color: '#FFFFFF',
    marginBottom: 10,
  },
  govCoverageBox: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    padding: 25,
    borderRadius: 8,
    border: '1px solid rgba(16, 185, 129, 0.3)',
    marginTop: 20,
  },
  govCoverageLabel: {
    fontSize: 14,
    color: '#D1FAE5',
    marginBottom: 8,
  },
  govCoverageValue: {
    fontSize: 32,
    fontWeight: 700,
    color: '#10B981',
  },
  table: {
    width: '100%',
    marginTop: 20,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderBottom: '2px solid #E5E7EB',
  },
  tableRow: {
    flexDirection: 'row',
    padding: 12,
    borderBottom: '1px solid #E5E7EB',
  },
  tableCell: {
    flex: 1,
    fontSize: 10,
    color: '#374151',
  },
  tableCellHeader: {
    fontWeight: 600,
    color: '#111827',
  },
  tableCellFirst: {
    fontWeight: 600,
    color: '#111827',
  },
  checklistSection: {
    marginTop: 20,
  },
  checklistTitle: {
    fontSize: 16,
    fontWeight: 600,
    color: '#111827',
    marginBottom: 15,
  },
  checklistItem: {
    flexDirection: 'row',
    marginBottom: 10,
    alignItems: 'flex-start',
  },
  checklistCheck: {
    fontSize: 12,
    color: '#10B981',
    marginRight: 8,
    marginTop: 2,
  },
  checklistText: {
    fontSize: 11,
    color: '#374151',
    flex: 1,
    lineHeight: 1.5,
  },
  ctaSection: {
    backgroundColor: '#10B981',
    padding: 40,
    borderRadius: 12,
    textAlign: 'center',
    marginTop: 30,
  },
  ctaTitle: {
    fontSize: 32,
    fontWeight: 700,
    color: '#FFFFFF',
    marginBottom: 10,
  },
  ctaSubtitle: {
    fontSize: 16,
    color: '#D1FAE5',
    marginBottom: 20,
  },
  ctaButton: {
    backgroundColor: '#FFFFFF',
    color: '#10B981',
    padding: '15px 40px',
    borderRadius: 8,
    fontSize: 18,
    fontWeight: 700,
    marginBottom: 10,
  },
  ctaNote: {
    fontSize: 10,
    color: '#D1FAE5',
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 40,
    right: 40,
    textAlign: 'center',
    fontSize: 8,
    color: '#9CA3AF',
  },
});

interface FreeReportPDFProps {
  data: FreeReportData;
  questionnaire?: QuestionnaireResponse;
}

const getMatchBadgeStyle = (matchType: string) => {
  switch (matchType) {
    case 'Safe Bet':
      return styles.matchBadgeSafe;
    case 'Best Value':
      return styles.matchBadgeValue;
    case 'Premium':
      return styles.matchBadgePremium;
    default:
      return styles.matchBadgeSafe;
  }
};

const FreeReportPDF: React.FC<FreeReportPDFProps> = ({ data, questionnaire }) => {
  const { homes, fairCostGap, chcTeaserPercent } = data;

  return (
    <Document>
      {/* Page 1: Header + Summary */}
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Your Personal Report</Text>
          <Text style={styles.headerSubtitle}>
            Report Generated: {new Date().toLocaleDateString('en-GB')}
          </Text>
          {questionnaire && (
            <>
              <View style={styles.summaryGrid}>
                <View style={styles.summaryBox}>
                  <Text style={styles.summaryLabel}>Postcode</Text>
                  <Text style={styles.summaryValue}>{questionnaire.postcode}</Text>
                </View>
                {questionnaire.care_type && (
                  <View style={styles.summaryBox}>
                    <Text style={styles.summaryLabel}>Care Type</Text>
                    <Text style={styles.summaryValue}>{questionnaire.care_type.toUpperCase()}</Text>
                  </View>
                )}
                {questionnaire.budget && (
                  <View style={styles.summaryBox}>
                    <Text style={styles.summaryLabel}>Budget</Text>
                    <Text style={styles.summaryValue}>£{questionnaire.budget.toLocaleString()}/week</Text>
                  </View>
                )}
              </View>
              {chcTeaserPercent > 0 && (
                <View style={styles.chcBox}>
                  <Text style={styles.chcLabel}>CHC Probability</Text>
                  <Text style={styles.chcValue}>{chcTeaserPercent.toFixed(1)}%</Text>
                </View>
              )}
            </>
          )}
        </View>

        <Text style={styles.sectionTitle}>Recommended Care Homes</Text>
        <Text style={{ fontSize: 11, color: '#6B7280', marginBottom: 20 }}>
          This report presents 3 best care home options selected specifically for you.
        </Text>
      </Page>

      {/* Pages 2-4: One page per home */}
      {homes.map((home, index) => {
        const avgPrice = (home.price_range.min + home.price_range.max) / 2;
        const matchBadgeStyle = getMatchBadgeStyle(home.match_type);

        return (
          <Page key={index} size="A4" style={styles.page}>
            <View style={styles.homeCard}>
              {/* Image */}
              {home.photo ? (
                <Image src={home.photo} style={styles.homeImage} />
              ) : (
                <View style={styles.homeImagePlaceholder}>
                  <Text style={{ fontSize: 24, color: '#9CA3AF' }}>🏠</Text>
                </View>
              )}

              <View style={styles.homeContent}>
                {/* Header */}
                <View style={styles.homeHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.homeName}>{home.name}</Text>
                    <View style={[styles.matchBadge, matchBadgeStyle]}>
                      <Text>{home.match_type}</Text>
                    </View>
                  </View>
                  <View style={styles.badge}>
                    <Text>Band {home.band}/5</Text>
                  </View>
                </View>

                {/* Address */}
                {home.address && (
                  <Text style={{ fontSize: 10, color: '#6B7280', marginBottom: 15 }}>
                    📍 {home.address}{home.city ? `, ${home.city}` : ''}
                  </Text>
                )}

                {/* Price */}
                <View style={styles.priceSection}>
                  <Text style={styles.priceMain}>£{avgPrice.toLocaleString()}</Text>
                  <Text style={styles.priceRange}>
                    £{home.price_range.min.toLocaleString()} - £{home.price_range.max.toLocaleString()}/week
                  </Text>
                </View>

                {/* Why This Home */}
                {home.why_this_home && (
                  <View style={styles.whySection}>
                    <Text style={styles.whyTitle}>⭐ Why This Home</Text>
                    <Text style={styles.whyText}>{home.why_this_home}</Text>
                  </View>
                )}

                {/* Details */}
                <View style={styles.detailsGrid}>
                  <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>Distance</Text>
                    <Text style={styles.detailValue}>{home.distance.toFixed(1)} km</Text>
                  </View>
                  <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>FSA Rating</Text>
                    <Text style={styles.detailValue}>{home.fsa_color.toUpperCase()}</Text>
                  </View>
                  {home.rating && (
                    <View style={styles.detailItem}>
                      <Text style={styles.detailLabel}>CQC Rating</Text>
                      <Text style={styles.detailValue}>{home.rating}</Text>
                    </View>
                  )}
                </View>

                {/* Features */}
                {home.features && home.features.length > 0 && (
                  <View style={{ marginTop: 15 }}>
                    <Text style={{ fontSize: 10, fontWeight: 600, color: '#111827', marginBottom: 8 }}>
                      Key Features:
                    </Text>
                    <Text style={{ fontSize: 9, color: '#6B7280', lineHeight: 1.5 }}>
                      {home.features.join(' • ')}
                    </Text>
                  </View>
                )}
              </View>
            </View>
          </Page>
        );
      })}

      {/* Page 5: Fair Cost Gap - Full page red */}
      <Page size="A4" style={styles.fairCostGapPage}>
        <Text style={styles.fairCostGapTitle}>YOUR OVERPAYMENT</Text>

        <View style={styles.fairCostGapMain}>
          <Text style={styles.fairCostGapLabel}>Per Week</Text>
          <Text style={styles.fairCostGapValue}>£{Math.round(fairCostGap.weekly).toLocaleString()}</Text>
          <Text style={styles.fairCostGapSub}>
            £{Math.round(fairCostGap.annual).toLocaleString()}/year
          </Text>
          <Text style={styles.fairCostGapSub}>
            £{Math.round(fairCostGap.fiveYear).toLocaleString()} over 5 years
          </Text>
        </View>

        <View style={styles.govCoverageBox}>
          <Text style={styles.govCoverageLabel}>Government May Cover</Text>
          <Text style={styles.govCoverageValue}>£32,000–£82,000/year</Text>
          <Text style={{ fontSize: 10, color: '#D1FAE5', marginTop: 8 }}>
            If eligible for CHC (Continuing Healthcare)
          </Text>
        </View>
      </Page>

      {/* Page 6: Comparison Table */}
      <Page size="A4" style={styles.page}>
        <Text style={styles.sectionTitle}>Comparison Table</Text>

        <View style={styles.table}>
          <View style={styles.tableHeader}>
            <Text style={[styles.tableCell, styles.tableCellHeader, { flex: 1.5 }]}>Criterion</Text>
            <Text style={[styles.tableCell, styles.tableCellHeader]}>{homes[0]?.name}</Text>
            <Text style={[styles.tableCell, styles.tableCellHeader]}>{homes[1]?.name}</Text>
            <Text style={[styles.tableCell, styles.tableCellHeader]}>{homes[2]?.name}</Text>
          </View>

          {[
            {
              name: 'Weekly Cost',
              home1: `£${Math.round((homes[0]?.price_range.min + homes[0]?.price_range.max) / 2).toLocaleString()}`,
              home2: `£${Math.round((homes[1]?.price_range.min + homes[1]?.price_range.max) / 2).toLocaleString()}`,
              home3: `£${Math.round((homes[2]?.price_range.min + homes[2]?.price_range.max) / 2).toLocaleString()}`,
            },
            {
              name: 'Price Band',
              home1: `${homes[0]?.band}/5`,
              home2: `${homes[1]?.band}/5`,
              home3: `${homes[2]?.band}/5`,
            },
            {
              name: 'Distance',
              home1: `${homes[0]?.distance.toFixed(1)} km`,
              home2: `${homes[1]?.distance.toFixed(1)} km`,
              home3: `${homes[2]?.distance.toFixed(1)} km`,
            },
            {
              name: 'FSA Rating',
              home1: homes[0]?.fsa_rating != null 
                ? `${homes[0].fsa_rating}/5` 
                : homes[0]?.fsa_color?.toUpperCase() || 'N/A',
              home2: homes[1]?.fsa_rating != null 
                ? `${homes[1].fsa_rating}/5` 
                : homes[1]?.fsa_color?.toUpperCase() || 'N/A',
              home3: homes[2]?.fsa_rating != null 
                ? `${homes[2].fsa_rating}/5` 
                : homes[2]?.fsa_color?.toUpperCase() || 'N/A',
            },
            {
              name: 'CQC Rating',
              home1: homes[0]?.rating || 'N/A',
              home2: homes[1]?.rating || 'N/A',
              home3: homes[2]?.rating || 'N/A',
            },
            {
              name: 'Match Type',
              home1: homes[0]?.match_type || 'N/A',
              home2: homes[1]?.match_type || 'N/A',
              home3: homes[2]?.match_type || 'N/A',
            },
          ].map((row, idx) => (
            <View key={idx} style={styles.tableRow}>
              <Text style={[styles.tableCell, styles.tableCellFirst, { flex: 1.5 }]}>{row.name}</Text>
              <Text style={styles.tableCell}>{row.home1}</Text>
              <Text style={styles.tableCell}>{row.home2}</Text>
              <Text style={styles.tableCell}>{row.home3}</Text>
            </View>
          ))}
        </View>
      </Page>

      {/* Page 7: Checklist */}
      <Page size="A4" style={styles.page}>
        <Text style={styles.sectionTitle}>Checklist and Next Steps</Text>

        <View style={styles.checklistSection}>
          <Text style={styles.checklistTitle}>✓ What to Do Now</Text>
          {[
            'Check eligibility for CHC funding',
            'Contact recommended homes',
            'Request detailed pricing information',
            'Organize visits to top 3 homes',
          ].map((item, idx) => (
            <View key={idx} style={styles.checklistItem}>
              <Text style={styles.checklistCheck}>✓</Text>
              <Text style={styles.checklistText}>{item}</Text>
            </View>
          ))}
        </View>

        <View style={[styles.checklistSection, { marginTop: 30 }]}>
          <Text style={styles.checklistTitle}>→ Next Steps</Text>
          {[
            'Apply for CHC assessment',
            'Compare offers from different homes',
            'Discuss funding with local authority',
            'Make a decision based on complete information',
          ].map((item, idx) => (
            <View key={idx} style={styles.checklistItem}>
              <Text style={styles.checklistCheck}>{idx + 1}.</Text>
              <Text style={styles.checklistText}>{item}</Text>
            </View>
          ))}
        </View>
      </Page>

      {/* Page 8: CTA */}
      <Page size="A4" style={styles.page}>
        <View style={styles.ctaSection}>
          <Text style={styles.ctaTitle}>Save £50k+?</Text>
          <Text style={styles.ctaSubtitle}>
            Get professional analysis and personal recommendations
          </Text>
          <View style={styles.ctaButton}>
            <Text style={{ color: '#10B981', fontSize: 18, fontWeight: 700 }}>
              Professional £119 →
            </Text>
          </View>
          <Text style={styles.ctaNote}>
            Includes deep analysis of all homes and funding strategy
          </Text>
        </View>

        <Text style={styles.footer}>
          RightCareHome Free Report • Generated {new Date().toLocaleDateString('ru-RU')}
        </Text>
      </Page>
    </Document>
  );
};

export default FreeReportPDF;

