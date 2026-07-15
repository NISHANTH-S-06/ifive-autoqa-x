import { faqItems } from '../data/faq';

export function FAQ() {
  return (
    <section className="section" id="about">
      <div className="section-inner">
        <div className="section-title">
          <h2>FAQ</h2>
        </div>
        <div className="faq-list">
          {faqItems.map((item) => (
            <article className="faq-item" key={item.question}>
              <h3>{item.question}</h3>
              <p>{item.answer}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

