import { AgentWorkflow } from '../components/AgentWorkflow';
import { CTA } from '../components/CTA';
import { FAQ } from '../components/FAQ';
import { FeatureCards } from '../components/FeatureCards';
import { Footer } from '../components/Footer';
import { Header } from '../components/Header';
import { Hero } from '../components/Hero';
import { ProductConnections } from '../components/ProductConnections';
import { ReportsSection } from '../components/ReportsSection';
import { SecuritySection } from '../components/SecuritySection';
import { TestDashboardPreview } from '../components/TestDashboardPreview';
import { TestManagementCore } from '../components/TestManagementCore';
import { ConnectionTargetsCore } from '../components/ConnectionTargetsCore';
import { AutomatedRunsCore } from '../components/AutomatedRunsCore';
import { DefectsCore } from '../components/DefectsCore';
import { ManagementReportsCore } from '../components/ManagementReportsCore';
import { FinalReleaseCore } from '../components/FinalReleaseCore';
import { AccountSecurityPanel } from '../components/AccountSecurityPanel';
import { AdminPanels } from '../components/AdminPanels';

export function HomePage() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <FeatureCards />
        <AgentWorkflow />
        <ProductConnections />
        <TestDashboardPreview />
        <TestManagementCore />
        <ConnectionTargetsCore />
        <AutomatedRunsCore />
        <DefectsCore />
        <ManagementReportsCore />
        <FinalReleaseCore />
        <AccountSecurityPanel />
        <AdminPanels />
        <SecuritySection />
        <ReportsSection />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </>
  );
}
