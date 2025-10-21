import React from 'react'
import { Box } from '@mui/material'
import HeroSection from './HeroSection'
import StrategyMarketplaceSection from './StrategyMarketplaceSection'
import HowItWorksSection from './HowItWorksSection'
import CompanyIntroSection from './CompanyIntroSection'
import CommunityHighlightSection from './CommunityHighlightSection'
import CoreServicesSection from './CoreServicesSection'
import UserReviewsSection from './UserReviewsSection'
import PricingSection from './PricingSection'
import FooterSection from './FooterSection'

interface LandingPageProps {
  onLoginClick: () => void
}

const LandingPage: React.FC<LandingPageProps> = ({ onLoginClick }) => {
  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: '100vw',
        overflowX: 'hidden',
        position: 'relative'
      }}
    >
      {/* Hero Section */}
      <HeroSection onLoginClick={onLoginClick} />

      {/* Strategy Marketplace - 핵심 기능 */}
      <StrategyMarketplaceSection onLoginClick={onLoginClick} />

      {/* How It Works */}
      <HowItWorksSection />

      {/* Company Introduction */}
      <CompanyIntroSection />

      {/* Community Highlights */}
      <CommunityHighlightSection onLoginClick={onLoginClick} />

      {/* Core Services */}
      <CoreServicesSection />

      {/* User Reviews */}
      <UserReviewsSection />

      {/* Pricing Plans */}
      <PricingSection onLoginClick={onLoginClick} />

      {/* Footer */}
      <FooterSection />
    </Box>
  )
}

export default LandingPage
