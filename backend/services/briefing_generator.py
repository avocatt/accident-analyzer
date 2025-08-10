from typing import Optional
import os
from datetime import datetime
from io import BytesIO
import base64

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from models.analysis_result import AnalysisResult


class BriefingGenerator:
    """
    Generates attorney briefing documents in HTML and PDF formats
    """
    
    def __init__(self):
        self.html_template = self._load_html_template()
    
    def _load_html_template(self) -> str:
        """
        Load or define HTML template for briefing
        """
        return """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LexIntake - Attorney Briefing</title>
            <style>
                body {
                    font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    line-height: 1.6;
                    color: #0A2240;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #F0F4F8;
                }
                .header {
                    background: #0A2240;
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }
                .header h1 {
                    margin: 0;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 700;
                }
                .disclaimer {
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }
                .section {
                    background: white;
                    padding: 25px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .section h2 {
                    color: #0A2240;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 700;
                    border-bottom: 2px solid #2ECC71;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                .party-info {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }
                .party-card {
                    border: 1px solid #e0e0e0;
                    padding: 15px;
                    border-radius: 6px;
                }
                .party-card h3 {
                    color: #0A2240;
                    margin-top: 0;
                }
                .info-row {
                    display: flex;
                    margin: 8px 0;
                }
                .info-label {
                    font-weight: bold;
                    min-width: 120px;
                    color: #6C757D;
                }
                .info-value {
                    flex: 1;
                }
                .fault-assessment {
                    background: #e8f5e9;
                    padding: 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }
                .fault-indicator {
                    background: #2ECC71;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    display: inline-block;
                    margin: 4px;
                }
                .missing-info {
                    color: #dc3545;
                    font-style: italic;
                }
                .confidence-meter {
                    background: #e0e0e0;
                    height: 20px;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }
                .confidence-fill {
                    background: #2ECC71;
                    height: 100%;
                    transition: width 0.3s;
                }
                .recommendations {
                    background: #f0f4f8;
                    padding: 15px;
                    border-radius: 6px;
                }
                .recommendations ul {
                    margin: 10px 0;
                }
                .recommendations li {
                    margin: 8px 0;
                }
                .timestamp {
                    text-align: right;
                    color: #6C757D;
                    font-size: 0.9em;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>LexIntake Attorney Briefing</h1>
                <p style="margin: 10px 0 0 0;">AI-Powered Traffic Accident Analysis</p>
            </div>
            
            <div class="disclaimer">
                <strong>⚠️ Important Notice:</strong> This document is an automated analysis for attorney review purposes only. 
                It does not constitute legal advice. Using this service does not create an attorney-client relationship.
            </div>
            
            {content}
            
            <div class="timestamp">
                Generated: {timestamp}
            </div>
        </body>
        </html>
        """
    
    def generate_html_briefing(self, analysis: AnalysisResult) -> str:
        """
        Generate HTML briefing from analysis result
        """
        content_sections = []
        
        # Case Summary Section
        content_sections.append(f"""
        <div class="section">
            <h2>Case Summary</h2>
            <p>{analysis.case_summary}</p>
        </div>
        """)
        
        # Party Information Section
        content_sections.append(f"""
        <div class="section">
            <h2>Party Information</h2>
            <div class="party-info">
                <div class="party-card">
                    <h3>Party A (Sürücü A)</h3>
                    <div class="info-row">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{analysis.party_a.name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">ID Number:</span>
                        <span class="info-value">{analysis.party_a.id_number or 'Not provided'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Vehicle Plate:</span>
                        <span class="info-value">{analysis.party_a.vehicle_plate}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Vehicle Type:</span>
                        <span class="info-value">{analysis.party_a.vehicle_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Insurance:</span>
                        <span class="info-value">{analysis.party_a.insurance_company or 'Not provided'}</span>
                    </div>
                </div>
                
                <div class="party-card">
                    <h3>Party B (Sürücü B)</h3>
                    <div class="info-row">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{analysis.party_b.name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">ID Number:</span>
                        <span class="info-value">{analysis.party_b.id_number or 'Not provided'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Vehicle Plate:</span>
                        <span class="info-value">{analysis.party_b.vehicle_plate}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Vehicle Type:</span>
                        <span class="info-value">{analysis.party_b.vehicle_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Insurance:</span>
                        <span class="info-value">{analysis.party_b.insurance_company or 'Not provided'}</span>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Accident Details Section
        content_sections.append(f"""
        <div class="section">
            <h2>Accident Details</h2>
            <div class="info-row">
                <span class="info-label">Date:</span>
                <span class="info-value">{analysis.accident_details.date}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Time:</span>
                <span class="info-value">{analysis.accident_details.time}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Location:</span>
                <span class="info-value">{analysis.accident_details.location}</span>
            </div>
            {f'<div class="info-row"><span class="info-label">Conditions:</span><span class="info-value">{analysis.accident_details.weather_conditions}</span></div>' if analysis.accident_details.weather_conditions else ''}
        </div>
        """)
        
        # Form Analysis Section
        if analysis.form_checkboxes.section_13_selections:
            scenarios = ', '.join(map(str, analysis.form_checkboxes.section_13_selections))
            content_sections.append(f"""
            <div class="section">
                <h2>Form Analysis</h2>
                <div class="info-row">
                    <span class="info-label">Damage Zones:</span>
                    <span class="info-value">{', '.join(map(str, analysis.form_checkboxes.section_12_selections)) if analysis.form_checkboxes.section_12_selections else 'Not specified'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Accident Scenarios:</span>
                    <span class="info-value">Boxes {scenarios}</span>
                </div>
                {f'<div class="info-row"><span class="info-label">Initial Impact:</span><span class="info-value">{analysis.form_checkboxes.section_14_initial_impact}</span></div>' if analysis.form_checkboxes.section_14_initial_impact else ''}
            </div>
            """)
        
        # Fault Assessment Section
        content_sections.append(f"""
        <div class="section">
            <h2>Fault Assessment</h2>
            <div class="fault-assessment">
                {f'<p><strong>Preliminary Fault Party:</strong> {analysis.fault_assessment.preliminary_fault_party}</p>' if analysis.fault_assessment.preliminary_fault_party else ''}
                {f'<p><strong>Estimated Fault Distribution:</strong> Party A: {analysis.fault_assessment.party_a_fault_percentage}% - Party B: {analysis.fault_assessment.party_b_fault_percentage}%</p>' if analysis.fault_assessment.party_a_fault_percentage else ''}
                <p><strong>Fault Indicators:</strong></p>
                <div>
                    {''.join([f'<span class="fault-indicator">{indicator}</span>' for indicator in analysis.fault_assessment.fault_indicators])}
                </div>
            </div>
        </div>
        """)
        
        # Photo Analysis Section
        if analysis.photo_analyses:
            photo_html = ""
            for photo in analysis.photo_analyses:
                photo_html += f"""
                <div style="margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                    <strong>Photo {photo.photo_id}:</strong> {photo.description}
                </div>
                """
            content_sections.append(f"""
            <div class="section">
                <h2>Photo Analysis</h2>
                {photo_html}
            </div>
            """)
        
        # Recommendations Section
        if analysis.recommended_actions:
            rec_html = "<ul>" + "".join([f"<li>{rec}</li>" for rec in analysis.recommended_actions]) + "</ul>"
            content_sections.append(f"""
            <div class="section">
                <h2>Recommended Actions</h2>
                <div class="recommendations">
                    {rec_html}
                </div>
            </div>
            """)
        
        # Data Quality Section
        confidence_percentage = int(analysis.extraction_confidence * 100)
        content_sections.append(f"""
        <div class="section">
            <h2>Data Quality Assessment</h2>
            <div class="info-row">
                <span class="info-label">Extraction Confidence:</span>
                <span class="info-value">{confidence_percentage}%</span>
            </div>
            <div class="confidence-meter">
                <div class="confidence-fill" style="width: {confidence_percentage}%"></div>
            </div>
            {f'<p class="missing-info"><strong>Missing Information:</strong> {", ".join(analysis.missing_information)}</p>' if analysis.missing_information else ''}
        </div>
        """)
        
        # Combine all sections
        content = "\n".join(content_sections)
        timestamp = analysis.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return self.html_template.format(content=content, timestamp=timestamp)
    
    def generate_pdf_briefing(self, analysis: AnalysisResult) -> bytes:
        """
        Generate PDF briefing from analysis result
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0A2240'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0A2240'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("LexIntake Attorney Briefing", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6C757D'),
            borderColor=colors.HexColor('#ffc107'),
            borderWidth=1,
            borderPadding=10
        )
        story.append(Paragraph(
            "This document is an automated analysis for attorney review purposes only. "
            "It does not constitute legal advice.",
            disclaimer_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Case Summary
        story.append(Paragraph("Case Summary", heading_style))
        story.append(Paragraph(analysis.case_summary, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Party Information Table
        story.append(Paragraph("Party Information", heading_style))
        party_data = [
            ['', 'Party A', 'Party B'],
            ['Name', analysis.party_a.name, analysis.party_b.name],
            ['Vehicle Plate', analysis.party_a.vehicle_plate, analysis.party_b.vehicle_plate],
            ['Vehicle Type', analysis.party_a.vehicle_type, analysis.party_b.vehicle_type],
            ['Insurance', analysis.party_a.insurance_company or 'N/A', analysis.party_b.insurance_company or 'N/A']
        ]
        
        party_table = Table(party_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
        party_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A2240')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(party_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Accident Details
        story.append(Paragraph("Accident Details", heading_style))
        details_text = f"""
        <b>Date:</b> {analysis.accident_details.date}<br/>
        <b>Time:</b> {analysis.accident_details.time}<br/>
        <b>Location:</b> {analysis.accident_details.location}<br/>
        """
        story.append(Paragraph(details_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Fault Assessment
        if analysis.fault_assessment.preliminary_fault_party:
            story.append(Paragraph("Fault Assessment", heading_style))
            fault_text = f"""
            <b>Preliminary Fault Party:</b> {analysis.fault_assessment.preliminary_fault_party}<br/>
            """
            if analysis.fault_assessment.party_a_fault_percentage:
                fault_text += f"""
                <b>Fault Distribution:</b> Party A: {analysis.fault_assessment.party_a_fault_percentage}% - 
                Party B: {analysis.fault_assessment.party_b_fault_percentage}%<br/>
                """
            story.append(Paragraph(fault_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6C757D'),
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            f"Generated: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes