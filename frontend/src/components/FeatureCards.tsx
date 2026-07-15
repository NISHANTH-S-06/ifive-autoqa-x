import { features } from '../data/features';

export function FeatureCards() {
  return (
    <section className="section" id="platform">
      <div className="section-inner">
        <div className="section-title">
          <h2>Core Features</h2>
          <p>Repeatable coverage for user journeys, APIs, permissions, exports, and failures.</p>
        </div>
        <div className="grid grid-3">
          {features.map((feature) => (
            <article className="card" key={feature.title}>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

