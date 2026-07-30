import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List


class AdvancedReportService:
    def generate_html_report(self, run_data: Dict[str, Any], results: List[Dict[str, Any]], defects: List[Dict[str, Any]]) -> str:
        status = run_data.get("status", "UNKNOWN")
        status_color = "#10B981" if status == "PASS" else ("#F59E0B" if status == "PASS_WITH_WARNINGS" else ("#EF4444" if status == "FAIL" else "#6B7280"))

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Advanced QA Validation Report - Run #{run_data.get('id')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0F172A; color: #F8FAFC; margin: 0; padding: 30px; }}
        .header {{ background: #1E293B; border-radius: 12px; padding: 24px; border: 1px solid #334155; margin-bottom: 24px; }}
        .title {{ font-size: 24px; font-weight: bold; margin-bottom: 8px; color: #38BDF8; }}
        .badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-weight: bold; background: {status_color}; color: #FFFFFF; font-size: 14px; }}
        .section {{ background: #1E293B; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #94A3B8; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #0F172A; color: #94A3B8; font-weight: 600; }}
        .pass {{ color: #10B981; font-weight: 600; }}
        .fail {{ color: #EF4444; font-weight: 600; }}
        .warning {{ color: #F59E0B; font-weight: 600; }}
        .blocked {{ color: #6B7280; font-weight: 600; }}
        .info {{ color: #38BDF8; }}
        .footer {{ font-size: 12px; color: #64748B; margin-top: 40px; text-align: center; border-top: 1px solid #334155; padding-top: 16px; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="title">iFive AutoQA X — Advanced QA Validation Report</div>
                <div style="color: #94A3B8; font-size: 14px;">Project ID: {run_data.get('project_id')} | Test Plan Version #{run_data.get('test_plan_version_id')}</div>
            </div>
            <div>
                <span class="badge">{status}</span>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Execution Metadata</div>
        <table>
            <tr><th>Run ID</th><td>#{run_data.get('id')}</td><th>Automated Run ID</th><td>#{run_data.get('automated_run_id') or 'N/A'}</td></tr>
            <tr><th>Started At</th><td>{run_data.get('started_at')}</td><th>Completed At</th><td>{run_data.get('completed_at') or 'N/A'}</td></tr>
            <tr><th>Result Hash</th><td colspan="3"><code style="color: #38BDF8;">{run_data.get('result_hash') or 'N/A'}</code></td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">Validation Layer Results ({len(results)})</div>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Severity</th>
                    <th>Message</th>
                    <th>Duration (ms)</th>
                </tr>
            </thead>
            <tbody>
"""
        for r in results:
            st = r.get("status", "INFO")
            st_class = st.lower()
            html += f"""
                <tr>
                    <td><strong>{r.get('validator_type')}</strong></td>
                    <td><span class="{st_class}">{st}</span></td>
                    <td>{r.get('severity', 'INFO')}</td>
                    <td>{r.get('message')}</td>
                    <td>{r.get('duration_ms', 0)}ms</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
"""

        if defects:
            html += f"""
    <div class="section">
        <div class="section-title">Defects & Findings ({len(defects)})</div>
        <table>
            <thead>
                <tr>
                    <th>Fingerprint</th>
                    <th>Type</th>
                    <th>Reason Code</th>
                    <th>Title</th>
                </tr>
            </thead>
            <tbody>
"""
            for d in defects:
                html += f"""
                <tr>
                    <td><code>{d.get('fingerprint', '')[:12]}...</code></td>
                    <td>{d.get('validator_type')}</td>
                    <td><span class="fail">{d.get('reason_code')}</span></td>
                    <td>{d.get('title')}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""

        report_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
        html += f"""
    <div class="footer">
        Generated by iFive AutoQA X Enterprise Platform | Report SHA-256: <code>{report_hash}</code> | Strictly Local Authorized Verification
    </div>
</body>
</html>
"""
        return html

    def generate_pdf_report(self, run_data: Dict[str, Any], results: List[Dict[str, Any]], defects: List[Dict[str, Any]]) -> bytes:
        """
        Generates a valid minimalist PDF file representing the Advanced QA Validation Report.
        """
        status = run_data.get("status", "UNKNOWN")
        run_id = run_data.get("id", 0)

        # Build clean PDF stream content
        text_lines = [
            f"%PDF-1.4",
            f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
            f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
            f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj",
            f"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        ]

        # Draw text stream content
        stream_content = "BT /F1 16 Tf 50 740 Td (iFive AutoQA X - Advanced QA Validation Report) Tj ET\n"
        stream_content += f"BT /F1 12 Tf 50 715 Td (Run ID: #{run_id}  |  Status: {status}  |  Project: #{run_data.get('project_id')}) Tj ET\n"
        stream_content += f"BT /F1 10 Tf 50 690 Td (Result Hash: {run_data.get('result_hash') or 'N/A'}) Tj ET\n"
        stream_content += "BT /F1 12 Tf 50 660 Td (Validation Results:) Tj ET\n"

        y = 640
        for r in results[:15]:
            msg = r.get('message', '')[:65].replace('(', '[').replace(')', ']')
            line = f"[{r.get('validator_type')}] {r.get('status')}: {msg}"
            stream_content += f"BT /F1 9 Tf 50 {y} Td ({line}) Tj ET\n"
            y -= 18

        if defects:
            y -= 10
            stream_content += f"BT /F1 12 Tf 50 {y} Td (Defects Grouped: {len(defects)}) Tj ET\n"
            y -= 20
            for d in defects[:5]:
                t = d.get('title', '')[:65].replace('(', '[').replace(')', ']')
                stream_content += f"BT /F1 9 Tf 50 {y} Td (- {t}) Tj ET\n"
                y -= 16

        stream_content += "BT /F1 8 Tf 50 50 Td (Generated by iFive AutoQA X Enterprise Platform - Strictly Read-Only Local Verified) Tj ET\n"

        stream_bytes = stream_content.encode('latin1')
        stream_obj = f"4 0 obj << /Length {len(stream_bytes)} >> stream\n".encode('latin1') + stream_bytes + b"\nendstream\nendobj\n"

        pdf_body = "\n".join(text_lines).encode('latin1') + b"\n" + stream_obj
        pdf_body += f"xref\n0 6\n0000000000 65535 f \ntrailer << /Size 6 /Root 1 0 R >>\nstartxref\n{len(pdf_body)}\n%%EOF\n".encode('latin1')

        return pdf_body
