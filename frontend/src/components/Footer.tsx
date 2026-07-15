const columns = {
  Platform: ['Overview', 'Features', 'Agents', 'Reports', 'Security'],
  Products: ['ERP Testing', 'HRMS Testing', 'CRM Testing', 'IIoT Testing', 'Integration Testing'],
  Resources: ['Documentation', 'Test Guides', 'Roadmap', 'FAQ'],
  Company: ['About', 'Contact', 'Privacy', 'Terms'],
};

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="section-inner footer-grid">
        <div>
          <h3>iFive AutoQA</h3>
          <p>Local-first AI-assisted quality engineering for critical iFive business workflows.</p>
        </div>
        {Object.entries(columns).map(([title, links]) => (
          <div key={title}>
            <h4>{title}</h4>
            {links.map((link) => (
              <a href="#top" key={link}>
                {link}
              </a>
            ))}
          </div>
        ))}
      </div>
    </footer>
  );
}

