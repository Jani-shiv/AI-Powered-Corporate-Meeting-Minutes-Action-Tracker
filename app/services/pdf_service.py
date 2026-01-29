"""
PDF generation module for CorpMeet-AI application.
Creates professional meeting minutes PDFs using ReportLab.
"""

import os
from datetime import datetime
from flask import current_app
from reportlab.lib import colors

# ... imports ...


def create_meeting_minutes_pdf(meeting, output_path=None):
    # ...
    if not output_path:
        safe_title = "".join(
            c for c in meeting.title if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        date_str = meeting.date_created.strftime("%Y%m%d_%H%M")
        filename = f"meeting_minutes_{safe_title}_{date_str}.pdf".replace(" ", "_")
        # Use absolute path from current_app config or static folder
        output_path = os.path.join(
            current_app.root_path, "static", "downloads", filename
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # ...

    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    # Container for the 'Flowable' objects
    story = []

    # Get styles
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e3a8a"),  # Corporate blue
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor("#1e40af"),
    )

    body_style = ParagraphStyle(
        "CustomBody", parent=styles["Normal"], fontSize=11, spaceAfter=6, leftIndent=20
    )

    # Add title
    title = Paragraph("MEETING MINUTES", title_style)
    story.append(title)
    story.append(Spacer(1, 12))

    # Add meeting details header
    meeting_info = [
        ["Meeting Title:", meeting.title],
        ["Date & Time:", meeting.date_created.strftime("%B %d, %Y at %I:%M %p")],
        ["Generated:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        [
            "Sentiment:",
            getattr(meeting, "sentiment", "N/A"),
        ],  # Handle potential missing attr
        ["Key Topics:", ", ".join(meeting.get_keywords()[:5])],  # Limit to 5 keywords
    ]

    meeting_table = Table(meeting_info, colWidths=[2 * inch, 4 * inch])
    meeting_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1e40af")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 0),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8fafc")],
                ),
            ]
        )
    )

    story.append(meeting_table)
    story.append(Spacer(1, 30))

    # Add meeting summary
    if meeting.get_summary():
        story.append(Paragraph("MEETING SUMMARY", heading_style))
        for point in meeting.get_summary():
            bullet_point = Paragraph(f"• {point}", body_style)
            story.append(bullet_point)
        story.append(Spacer(1, 20))

    # Add action items
    if meeting.get_action_items():
        story.append(Paragraph("ACTION ITEMS", heading_style))

        # Create action items table
        action_data = [["Task", "Assigned To", "Deadline"]]

        for item in meeting.get_action_items():
            action_data.append(
                [
                    item.get("task", "N/A"),
                    item.get("owner", "N/A"),
                    item.get("deadline", "N/A"),
                ]
            )

        action_table = Table(action_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
        action_table.setStyle(
            TableStyle(
                [
                    # Header row styling
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8fafc")],
                    ),
                ]
            )
        )

        story.append(action_table)
        story.append(Spacer(1, 20))

    # Add key decisions
    if meeting.get_decisions():
        story.append(Paragraph("KEY DECISIONS", heading_style))
        for decision in meeting.get_decisions():
            decision_point = Paragraph(f"• {decision}", body_style)
            story.append(decision_point)
        story.append(Spacer(1, 20))

    # Add footer information
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey,
    )

    footer_text = "Generated by CorpMeet-AI - AI-Powered Meeting Minutes Tracker"
    story.append(Paragraph(footer_text, footer_style))

    # Build the PDF
    doc.build(story)

    return output_path


def create_downloads_directory():
    """Ensure the downloads directory exists for PDF files."""
    download_path = os.path.join("static", "downloads")
    os.makedirs(download_path, exist_ok=True)
    return download_path
