export function Hero() {
  const trustPoints = [
    'Local-first testing',
    'Deterministic Playwright execution',
    'Complete failure evidence',
    'Human-approved AI suggestions',
  ];

  return (
    <section className="hero" id="top">
      <div className="section-inner hero-layout">
        <div>
          <span className="badge">AI-Assisted Quality Engineering Platform</span>
          <h1>
            Test Every Workflow.
            <span>Release with Confidence.</span>
          </h1>
          <p>
            Automate functional, API, role, workflow and regression testing across iFive ERP,
            HRMS, CRM, IIoT and Application Integration products.
          </p>
          <div className="hero-actions">
            <a className="button button-primary" href="#request-demo">
              Request AutoQA Demo
            </a>
            <a className="button button-secondary" href="#workflow">
              View Testing Workflow
            </a>
          </div>
          <div className="trust-list">
            {trustPoints.map((item) => (
              <span className="trust-item" key={item}>
                {item}
              </span>
            ))}
          </div>
        </div>
        <div className="engine-map" aria-label="AutoQA product connection flow">
          <div className="engine-column">
            {['iFive ERP', 'iFive HRMS', 'iFive CRM', 'iFive IIoT', 'Application Integration'].map((item) => (
              <span className="engine-pill" key={item}>
                {item}
              </span>
            ))}
          </div>
          <div className="engine-core">iFive AutoQA</div>
          <div className="engine-column">
            {['UI Tests', 'API Tests', 'Workflow Tests', 'Permission Tests', 'Export Tests', 'Reports'].map((item) => (
              <span className="output-pill" key={item}>
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

