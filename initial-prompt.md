# React Native Pipe Center App - Development Plan

## Project Overview
Build a **local-only** professional business pricing calculator and quotation management app for React Native with the following core features:
- Calculator with discount/margin calculations and GST
- Configuration management with AsyncStorage persistence  
- Quotations system with 30-day auto-cleanup
- **Local PDF generation** for quotations (no server required)
- Cross-platform compatibility (Android/iOS)
- **Offline-first approach** - all data stored locally on device

## Target Device Compatibility
- **Primary**: Pixel 3a Android 12.0 (as shown in development environment)
- **Target**: All modern Android (API 21+) and iOS (13+) devices
- **Architecture**: Compatible with both old and new React Native architecture

## Development Approach
- **Phase-based development**: Complete one phase at a time with review checkpoints
- **Compatibility-first**: Use thoroughly tested, compatible package versions
- **Research-driven**: Web search for all package compatibility before implementation
- **Manual control**: Developer handles all npm commands and installations

## Technical Requirements

### React Native Version Strategy
Based on comprehensive package compatibility research:
- **Target Version**: React Native 0.74.x (optimal compatibility sweet spot)
- **Reasoning**: 
  - AsyncStorage 2.2.0: Requires RN 0.65+ (2.0.0+ needs RN 0.65+)
  - React Navigation 7.1.10: Requires RN 0.60+, works with latest versions
  - react-native-html-to-pdf 0.12.0: Supports RN 0.60+ (but 3 years old)
  - React Hook Form: No specific RN restrictions, works with both React/RN
  - RN 0.74.x still supports `react-native init` command (removed in 0.77)
- **New Architecture**: Compatible but optional

### Core Dependencies Compatibility Matrix
**COMPATIBILITY RESEARCH RESULTS:**

**Navigation**: React Navigation v7
- @react-navigation/native@7.1.10 ✅ RN 0.60+
- @react-navigation/bottom-tabs@6.6.1 ✅ RN 0.60+ 
- react-native-screens@3.34.0 ✅ RN 0.68+
- react-native-safe-area-context@4.14.0 ✅ RN 0.60+

**Data Persistence**: AsyncStorage
- @react-native-async-storage/async-storage@2.2.0 ✅ RN 0.65+
- **Critical**: v2.0.0+ requires minimum RN 0.65

**PDF Generation**: ⚠️ RESEARCH REQUIRED
- react-native-html-to-pdf@0.12.0 ✅ RN 0.60+ (3 years old, maintenance concerns)
- **Alternative needed**: Consider server-side PDF generation or newer libraries

**Form Handling**: React Hook Form
- react-hook-form@7.54.0 ✅ Works with React Native (no version restrictions)
- Lightweight (8.6KB), zero dependencies
- Supports validation schemas (Yup/Zod)

**OPTIMAL COMPATIBILITY TARGET**: React Native 0.74.x
- All packages confirmed compatible
- Stable version with good long-term support
- Still supports react-native init command

### Project Structure
```
PipeCenter/
├── src/
│   ├── components/     # Reusable UI components
│   ├── screens/        # Screen components
│   ├── navigation/     # Navigation setup
│   ├── services/       # Data persistence, PDF generation
│   ├── utils/          # Helper functions, calculations
│   ├── types/          # TypeScript definitions
│   └── constants/      # App constants
├── assets/            # Images, fonts
└── __tests__/         # Test files
```

## Feature Specifications

### 1. Calculator Screen
- Numeric input for initial price
- Two discount percentage inputs (sequential application)
- Margin percentage input
- Optional 18% GST toggle
- **Calculation**: `((initial_price - discount1%) - discount2%) + margin% + GST%`
- Real-time calculation display
- Configuration dropdown for quick-select
- Clear/reset functionality

### 2. Configuration Management
- Create/edit/delete configurations
- Fields: name, first discount %, second discount %, margin %
- AsyncStorage persistence
- Data validation and error handling
- Quick-select integration with calculator

### 3. Quotations System
- List view with last 30 days of quotations
- Create new quotation with:
  - Buyer name and address
  - Dynamic item table (S.No, Item Name, Rate, Quantity, Unit, Amount)
  - Add/edit/delete rows via modals
  - Rate calculation options:
    1. Direct rate entry
    2. Configuration + initial price calculation
    3. Custom calculation (no GST for items)
- Calculations:
  - Subtotal (no GST)
  - 18% GST on subtotal
  - Optional transport charges
  - Final total
- 30-day auto-cleanup of old quotations

### 4. Local PDF Generation
- Professional quotation format generated on-device
- Company header
- Buyer details section
- Itemized table with calculations
- Save to device local storage
- Share functionality via device sharing options
- **No internet/server required** - fully offline capable

### 5. Data Structures
```typescript
interface Configuration {
  id: string;
  name: string;
  firstDiscount: number;
  secondDiscount: number;
  margin: number;
  createdAt: number;
}

interface QuotationItem {
  sno: number;
  itemName: string;
  rate: number;
  quantity: number;
  unit: string;
  amount: number;
}

interface Quotation {
  id: string;
  buyerName: string;
  buyerAddress: string;
  items: QuotationItem[];
  subtotal: number;
  gst: number;
  transportCharges: number;
  total: number;
  createdAt: number;
}
```

## Critical Compatibility Findings

### PDF Generation Challenge ⚠️
**Issue**: react-native-html-to-pdf (primary option) has maintenance concerns:
- Last updated 3 years ago (v0.12.0)
- Community reports compatibility issues with newer Android versions
- Still functional but may need alternatives

**Local PDF Generation Solutions** (No server required):
1. **react-native-html-to-pdf** (current best option):
   - Despite maintenance concerns, still widely used
   - Converts HTML strings to PDF locally on device
   - Requires storage permissions for Android
   
2. **react-native-pdf-lib**:
   - Creates PDFs programmatically 
   - More control over PDF structure
   - Last updated 5 years ago
   
3. **WebView-based approach**:
   - Use WebView to render HTML
   - Capture as image or print to PDF
   - Platform-specific implementations

4. **Alternative Libraries**:
   - @react-native-print (iOS focused)
   - react-native-view-shot + jsPDF combination

**Recommendation**: Start with react-native-html-to-pdf despite age, with fallback plan for alternatives if issues arise

### Phase 1: Research & Compatibility Analysis ✅
- [x] Research React Native CLI setup best practices 2025
- [x] Determine optimal React Native version: **0.74.x**
- [x] Research all package versions for compatibility
- [x] Create compatibility matrix (see above)
- [x] **PROJECT INITIALIZED**: React Native 0.74.5 "PipeCenter" ready
- [ ] Research exact package versions for dependencies
- [ ] Provide dependency installation commands
- [ ] Document Android permissions needed
- [ ] Research local PDF generation alternatives

### Phase 2: Project Setup & Architecture ⏳
- [ ] Set up project structure
- [ ] Configure TypeScript (if needed)
- [ ] Install and configure navigation
- [ ] Set up AsyncStorage
- [ ] Create basic navigation shell
- [ ] Test on Android emulator

### Phase 3: Calculator Implementation ⏳
- [ ] Build calculator UI
- [ ] Implement calculation logic
- [ ] Add configuration management
- [ ] Integrate AsyncStorage
- [ ] Add input validation
- [ ] Test calculations thoroughly

### Phase 4: Quotations System ⏳
- [ ] Create quotation list screen
- [ ] Build quotation creation flow
- [ ] Implement dynamic item management
- [ ] Add calculation logic
- [ ] Implement 30-day cleanup
- [ ] Add data persistence

### Phase 5: PDF Generation ⏳
- [ ] Research and choose PDF library
- [ ] Implement PDF template
- [ ] Add professional formatting
- [ ] Integrate with quotations
- [ ] Test file generation and sharing
- [ ] Handle permissions

### Phase 6: UI/UX Polish & Testing ⏳
- [ ] Professional styling
- [ ] Error handling
- [ ] Loading states
- [ ] Responsive design
- [ ] Comprehensive testing
- [ ] Performance optimization

## Instructions for Claude Code

### 1. RESEARCH FIRST, CODE LATER
- **Start every phase with comprehensive web search**
- Research React Native version compatibility thoroughly
- Find exact package versions that work together
- **Do not write any code until research is complete**

### 2. NO AUTOMATIC INSTALLATIONS
- **Never run npm install or react-native init commands**
- Always provide exact commands for user to run
- Research compatibility before suggesting packages
- Let user handle all installations manually

### 3. PHASE-BY-PHASE DEVELOPMENT
- Complete only ONE phase at a time
- Ask for user review before proceeding to next phase
- Update the phase checklist as tasks are completed
- **Stop and ask for approval between phases**

### 4. COMPATIBILITY-FIRST APPROACH
- Use dependency compatibility data and profiles
- Research each package's React Native version support
- Prefer stable, well-maintained packages
- Document any compatibility concerns

### 5. ERROR HANDLING & VALIDATION
- Add proper error boundaries
- Validate all numeric inputs
- Handle AsyncStorage errors gracefully
- Add loading states for all async operations

### 6. PROFESSIONAL STANDARDS
- Use TypeScript for type safety
- Follow React Native best practices
- Add proper commenting
- Implement proper state management
- Handle Android permissions correctly

## Success Criteria
- App builds and runs without errors on Android emulator
- All calculations work correctly with proper precision
- Data persists between app sessions
- PDFs generate with professional formatting
- 30-day cleanup works automatically
- Professional UI suitable for business use
- Smooth performance on target devices

## Development Notes
- Focus on business-appropriate design and functionality
- **Offline-first architecture** - app must work without internet connection
- Prioritize reliability over flashy features  
- Ensure calculations handle decimal precision properly
- Test thoroughly on both Android and iOS if possible
- **Local data only** - no server dependencies or cloud storage
- Document any known limitations or requirements
- Handle device storage limitations gracefully

**REMEMBER**: This is a business app that needs to be reliable, professional, and functional above all else.