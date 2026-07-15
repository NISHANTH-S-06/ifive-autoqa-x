import { reportItems, technologyItems } from '../data/features';

export function ReportsSection() {
  return (
    <section className="section" id="resources">
      <div className="section-inner split">
        <div>
          <div className="section-title">
            <h2>Reporting</h2>
            <p>Every failure should arrive with enough context to reproduce and assign the defect.</p>
          </div>
          <ul className="check-list">
            {reportItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <div className="section-title">
            <h2>Technology</h2>
            <p>The pilot stack stays free, local, and friendly to repeatable engineering workflows.</p>
          </div>
          <ul className="check-list">
            {technologyItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

