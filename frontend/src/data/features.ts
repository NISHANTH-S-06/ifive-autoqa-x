export const features = [
  {
    title: 'UI Automation',
    description: 'Test pages, buttons, forms, menus and workflows.',
  },
  {
    title: 'API Testing',
    description: 'Validate authentication, requests, responses and schemas.',
  },
  {
    title: 'Role & Permission Testing',
    description: 'Check authorized and unauthorized access.',
  },
  {
    title: 'Cross-Browser Testing',
    description: 'Run tests on Chromium, Firefox and WebKit.',
  },
  {
    title: 'Failure Evidence',
    description: 'Capture screenshots, video, trace, console and network logs.',
  },
  {
    title: 'AI-Assisted Test Creation',
    description: 'Generate reviewable plans and Playwright test suggestions.',
  },
];

export const workflowSteps = [
  ['Understand', 'Capture product, module, role and expected workflow.'],
  ['Plan', 'Planner Agent prepares a detailed test plan.'],
  ['Generate', 'Generator Agent creates Playwright tests.'],
  ['Execute', 'Playwright runs deterministic tests.'],
  ['Detect', 'System collects failures and evidence.'],
  ['Review', 'Healer Agent suggests corrections for human approval.'],
  ['Report', 'Dashboard displays pass, fail, defect and coverage results.'],
];

export const agents = [
  ['Planner Agent', 'Converts requirements into test plans.'],
  ['Generator Agent', 'Creates Playwright TypeScript tests.'],
  ['Healer Agent', 'Analyzes failures and recommends safe repairs.'],
  ['Safety Agent', 'Blocks destructive and unauthorized actions.'],
];

export const dashboardMetrics = [
  ['Total Tests', '248'],
  ['Pass Rate', '94%'],
  ['Failed Tests', '14'],
  ['Open Defects', '9'],
  ['Avg Runtime', '18m'],
  ['Coverage', '5 products'],
];

export const securityRules = [
  'QA or sandbox environments only',
  'No production destructive testing',
  'No payment execution',
  'No payroll execution',
  'No record deletion',
  'No approval execution',
  'No IIoT machine-control actions',
  'Environment-based secrets',
  'Human approval for generated and healed tests',
  'Complete audit history',
];

export const technologyItems = [
  'Playwright Test',
  'TypeScript',
  'FastAPI',
  'React',
  'SQLite',
  'Ollama',
  'Qwen2.5-Coder',
  'Playwright MCP',
  'Git',
];

export const reportItems = [
  'Test Summary',
  'Pass/Fail Breakdown',
  'Product Coverage',
  'Failure Category',
  'Evidence Attachments',
  'Execution Time',
  'Browser Details',
  'Recommended Defect Owner',
  'Severity',
  'Re-run History',
];

