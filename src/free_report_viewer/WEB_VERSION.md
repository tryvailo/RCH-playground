# Web Version Report Guide

## Overview

The Free Report Viewer includes an interactive web version that displays reports in a premium, responsive design optimized for user engagement and conversion.

## Features

### 1. **Fair Cost Gap - Center Screen**
- **Red gradient block** with animated counter
- Displays **5-year gap** (£224,640) with CSS animation
- Large, impactful numbers (5rem font size, responsive to 3rem on mobile)
- Text: "Это только вершина айсберга" (This is only the tip of the iceberg)

### 2. **CTA Button**
- **Green gradient button**: "Узнать, как сэкономить £50k+ → Professional £119"
- Prominent placement below Fair Cost Gap
- Click shows upgrade benefits

### 3. **Care Home Cards**
- Displayed in **responsive columns** (max 3 columns)
- Each card shows:
  - Match type badge (Safe Bet, Best Value, Premium)
  - Home name and address
  - Weekly cost, CQC rating, distance
  - Price band and FSA rating
- Cards stack vertically on mobile

### 4. **Professional Peek Expander**
- Expandable section with deep analysis
- Shows CQC rating details
- FSA food hygiene information
- Companies House data teaser
- Upgrade prompt

### 5. **Action Buttons**
- **Поделиться** (Share): Copies report link
- **Перейти к Professional** (Go to Professional): Upgrade CTA
- **Report ID**: Displays shortened report ID

## Design Elements

### Colors
- **Primary Dark**: `#1E2A44` (dark blue)
- **Primary Green**: `#10B981` (accent green)
- **Error Red**: `#EF4444` (Fair Cost Gap)

### Typography
- **Poppins**: Headings (700 weight)
- **Inter**: Body text
- Responsive font sizes

### Animations
- CSS `@keyframes countUp` for Fair Cost Gap counter
- Smooth fade-in and slide-up effect
- 1.5s duration with ease-out timing

### Responsive Design
- **Desktop**: 3-column layout for care homes
- **Mobile** (< 768px): Single column, reduced font sizes
- Streamlit's built-in responsive columns

## Usage

### Toggle Web Version

Click the **"🌐 View Web Version"** button after generating a report. The web version appears below the PDF download button.

### Code Structure

```python
def display_web_version_report(report: FreeReportResponse):
    """Display premium web version of the report"""
    # Header
    # Fair Cost Gap with animated counter
    # CTA button
    # Care home cards
    # Professional Peek expander
    # Action buttons
```

### Key Functions

- `display_web_version_report()`: Main function to render web version
- `display_animated_counter()`: CSS-animated counter for Fair Cost Gap
- `display_care_home_card_web()`: Individual care home card
- `display_professional_peek()`: Expandable deep analysis section

## User Flow

1. User generates report → sees standard report view
2. Clicks "🌐 View Web Version" → web version appears
3. Sees animated Fair Cost Gap counter → emotional impact
4. Reads "Это только вершина айсберга" → creates urgency
5. Clicks CTA button → sees upgrade benefits
6. Reviews care home cards → makes informed decision
7. Expands Professional Peek → sees value of upgrade
8. Clicks action buttons → shares or upgrades

## Conversion Optimization

### Fair Cost Gap Section
- **Emotional impact**: Large red numbers create urgency
- **Social proof**: Shows real cost gap
- **Clear CTA**: Direct path to savings

### Care Home Cards
- **Visual hierarchy**: Match type badges highlight recommendations
- **Key metrics**: Cost, rating, distance at a glance
- **Trust signals**: CQC and FSA ratings

### Professional Peek
- **Teaser content**: Shows value without giving everything
- **Upgrade prompt**: Clear path to more information
- **FOMO**: "Available in Professional Report"

## Technical Notes

### Streamlit Limitations
- CSS animations work but are limited
- JavaScript buttons replaced with Streamlit buttons
- Share functionality uses Streamlit's native components

### Performance
- Web version loads instantly (no API calls)
- CSS animations are GPU-accelerated
- Responsive design uses CSS media queries

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS animations supported
- Responsive design works on all screen sizes

## Future Enhancements

- [ ] Real-time counter animation (JavaScript)
- [ ] Social sharing integration (Twitter, Facebook, LinkedIn)
- [ ] Print-friendly version
- [ ] Email report functionality
- [ ] Analytics tracking
- [ ] A/B testing for CTAs

