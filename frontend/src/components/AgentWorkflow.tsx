import { agents, workflowSteps } from '../data/features';

export function AgentWorkflow() {
  return (
    <section className="section" id="workflow">
      <div className="section-inner">
        <div className="section-title">
          <h2>How AutoQA Works</h2>
          <p>Agents assist the workflow while deterministic Playwright assertions own the result.</p>
        </div>
        <div className="workflow-list">
          {workflowSteps.map(([title, description]) => (
            <article className="workflow-step" key={title}>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
        <div className="section-title" id="test-agents">
          <h2>AI Agents</h2>
          <p>AI assists the testing process. Final pass or fail is always decided by deterministic Playwright assertions.</p>
        </div>
        <div className="grid grid-4">
          {agents.map(([title, description]) => (
            <article className="card" key={title}>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

