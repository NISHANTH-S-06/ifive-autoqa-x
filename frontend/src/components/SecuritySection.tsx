import { securityRules } from '../data/features';

export function SecuritySection() {
  return (
    <section className="section" id="solutions">
      <div className="section-inner">
        <div className="section-title">
          <h2>Security and Safety</h2>
          <p>AutoQA is designed for controlled QA and sandbox use, with human approval around AI output.</p>
        </div>
        <div className="grid grid-3">
          {securityRules.map((rule) => (
            <article className="card" key={rule}>
              <h3>{rule}</h3>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

