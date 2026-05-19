"""
PDF Report Service — generates downloadable PDF reports for call analysis.
Uses reportlab for PDF generation.
"""

import io
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


class PDFReportService:
    """Generates PDF reports from call analysis data."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Define custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            'CustomTitle', parent=self.styles['Title'],
            fontSize=22, spaceAfter=6, textColor=colors.HexColor('#0e7490'),
        ))
        self.styles.add(ParagraphStyle(
            'SectionHeader', parent=self.styles['Heading2'],
            fontSize=14, spaceAfter=8, spaceBefore=16,
            textColor=colors.HexColor('#1e293b'), borderPadding=(0, 0, 4, 0),
        ))
        self.styles.add(ParagraphStyle(
            'SubHeader', parent=self.styles['Heading3'],
            fontSize=11, spaceAfter=4, textColor=colors.HexColor('#475569'),
        ))
        self.styles.add(ParagraphStyle(
            'BodyCustom', parent=self.styles['Normal'],
            fontSize=10, leading=14, spaceAfter=6, textColor=colors.HexColor('#334155'),
        ))
        self.styles.add(ParagraphStyle(
            'SmallGray', parent=self.styles['Normal'],
            fontSize=8, textColor=colors.HexColor('#94a3b8'),
        ))

    def generate_report(self, analysis: dict) -> bytes:
        """Generate a complete PDF report from analysis data."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=20 * mm, leftMargin=20 * mm,
            topMargin=20 * mm, bottomMargin=20 * mm,
        )

        elements = []
        call = analysis.get("call", {})
        call_id = call.get("call_id", "Unknown")

        # ── Title Page ──
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("CallSense AI", self.styles['CustomTitle']))
        elements.append(Paragraph("Call Analysis Report", self.styles['Heading2']))
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0e7490')))
        elements.append(Spacer(1, 12))

        # Meta info table
        meta_data = [
            ["Call ID:", call_id],
            ["Status:", call.get("status", "N/A")],
            ["Input Type:", call.get("input_type", "N/A")],
            ["Created:", call.get("created_at", "N/A")[:19]],
            ["Processing Time:", f"{call.get('processing_time_seconds', 'N/A')}s"],
        ]
        if call.get("file_name"):
            meta_data.append(["File:", call["file_name"]])
        if call.get("duration_seconds"):
            meta_data.append(["Duration:", f"{round(call['duration_seconds'])}s"])

        meta_table = Table(meta_data, colWidths=[100, 350])
        meta_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        # ── Summary Section ──
        summary = analysis.get("summary")
        if summary:
            elements.append(Paragraph("Summary", self.styles['SectionHeader']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(summary.get("brief_summary", ""), self.styles['BodyCustom']))
            elements.append(Spacer(1, 8))

            elements.append(Paragraph("Customer Intent", self.styles['SubHeader']))
            elements.append(Paragraph(summary.get("customer_intent", "N/A"), self.styles['BodyCustom']))

            if summary.get("key_points"):
                elements.append(Paragraph("Key Points", self.styles['SubHeader']))
                for point in summary["key_points"]:
                    elements.append(Paragraph(f"• {point}", self.styles['BodyCustom']))

            if summary.get("issues_raised"):
                elements.append(Paragraph("Issues Raised", self.styles['SubHeader']))
                for issue in summary["issues_raised"]:
                    elements.append(Paragraph(f"• {issue}", self.styles['BodyCustom']))

            elements.append(Paragraph("Resolution", self.styles['SubHeader']))
            elements.append(Paragraph(summary.get("resolution_provided", "N/A"), self.styles['BodyCustom']))

            if summary.get("action_items"):
                elements.append(Paragraph("Action Items", self.styles['SubHeader']))
                for i, item in enumerate(summary["action_items"], 1):
                    elements.append(Paragraph(f"{i}. {item}", self.styles['BodyCustom']))

            if summary.get("follow_up_needed"):
                elements.append(Spacer(1, 6))
                elements.append(Paragraph(
                    f"⚠ Follow-up Required: {summary.get('follow_up_details', 'Yes')}",
                    self.styles['BodyCustom']
                ))

        # ── Quality Scores Section ──
        scores = analysis.get("quality_scores")
        if scores:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Quality Scores", self.styles['SectionHeader']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
            elements.append(Spacer(1, 6))

            overall = scores.get("overall_score", 0)
            grade = scores.get("grade", "N/A")
            elements.append(Paragraph(
                f"Overall Score: <b>{overall}/10</b> — Grade: <b>{grade}</b>",
                self.styles['BodyCustom']
            ))
            elements.append(Paragraph(scores.get("overall_feedback", ""), self.styles['BodyCustom']))

            score_items = [
                ("Empathy", "empathy_score"), ("Professionalism", "professionalism_score"),
                ("Resolution", "resolution_score"), ("Communication", "communication_score"),
                ("Compliance", "compliance_score"), ("Active Listening", "active_listening_score"),
            ]

            score_table_data = [["Dimension", "Score", "Justification"]]
            for label, key in score_items:
                s = scores.get(key, {})
                sc = s.get("score", "N/A") if isinstance(s, dict) else "N/A"
                just = s.get("justification", "")[:80] if isinstance(s, dict) else ""
                score_table_data.append([label, f"{sc}/10", just])

            t = Table(score_table_data, colWidths=[100, 60, 300])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(Spacer(1, 6))
            elements.append(t)

        # ── Sentiment Section ──
        sentiment = analysis.get("sentiment")
        if sentiment:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Sentiment Analysis", self.styles['SectionHeader']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
            elements.append(Spacer(1, 6))

            sent_data = [
                ["Overall", sentiment.get("overall_sentiment", "N/A")],
                ["Customer", sentiment.get("customer_sentiment", "N/A")],
                ["Agent", sentiment.get("agent_sentiment", "N/A")],
                ["Trajectory", sentiment.get("sentiment_trajectory", "N/A")],
            ]
            for row in sent_data:
                elements.append(Paragraph(f"<b>{row[0]}:</b> {row[1].replace('_', ' ').title()}", self.styles['BodyCustom']))

            if sentiment.get("emotional_triggers"):
                elements.append(Paragraph("Emotional Triggers", self.styles['SubHeader']))
                for trigger in sentiment["emotional_triggers"]:
                    elements.append(Paragraph(f"⚡ {trigger}", self.styles['BodyCustom']))

        # ── Routing Section ──
        routing = analysis.get("routing")
        if routing:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Routing Decision", self.styles['SectionHeader']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
            elements.append(Spacer(1, 6))

            elements.append(Paragraph(f"<b>Category:</b> {routing.get('category', 'N/A').replace('_', ' ').title()}", self.styles['BodyCustom']))
            elements.append(Paragraph(f"<b>Urgency:</b> {routing.get('urgency', 'N/A').title()}", self.styles['BodyCustom']))
            elements.append(Paragraph(f"<b>Resolution:</b> {routing.get('resolution_status', 'N/A').replace('_', ' ').title()}", self.styles['BodyCustom']))
            elements.append(Paragraph(f"<b>Priority:</b> {routing.get('priority_score', 'N/A')}/10", self.styles['BodyCustom']))

            if routing.get("requires_escalation"):
                elements.append(Paragraph(f"⚠ Escalation Required: {routing.get('escalation_reason', '')}", self.styles['BodyCustom']))

            if routing.get("tags"):
                elements.append(Paragraph(f"<b>Tags:</b> {', '.join(routing['tags'])}", self.styles['BodyCustom']))

        # ── Coaching Section ──
        coaching = analysis.get("coaching")
        if coaching:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Coaching Recommendations", self.styles['SectionHeader']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
            elements.append(Spacer(1, 6))

            elements.append(Paragraph(coaching.get("overall_recommendation", ""), self.styles['BodyCustom']))

            if coaching.get("strengths"):
                elements.append(Paragraph("Strengths", self.styles['SubHeader']))
                for s in coaching["strengths"]:
                    elements.append(Paragraph(f"✓ {s}", self.styles['BodyCustom']))

            if coaching.get("areas_for_improvement"):
                elements.append(Paragraph("Areas for Improvement", self.styles['SubHeader']))
                for a in coaching["areas_for_improvement"]:
                    elements.append(Paragraph(f"→ {a}", self.styles['BodyCustom']))

            if coaching.get("training_suggestions"):
                elements.append(Paragraph("Training Suggestions", self.styles['SubHeader']))
                for t in coaching["training_suggestions"]:
                    elements.append(Paragraph(f"📖 {t}", self.styles['BodyCustom']))

        # ── Footer ──
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            f"Generated by CallSense AI — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            self.styles['SmallGray']
        ))

        doc.build(elements)
        return buffer.getvalue()


_pdf_service = None

def get_pdf_service() -> PDFReportService:
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFReportService()
    return _pdf_service
