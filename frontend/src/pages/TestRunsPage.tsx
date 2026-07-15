import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { TestDashboardPreview } from '../components/TestDashboardPreview';

export function TestRunsPage() {
  return (
    <>
      <Header />
      <main className="section">
        <div className="section-inner">
          <TestDashboardPreview />
        </div>
      </main>
      <Footer />
    </>
  );
}
