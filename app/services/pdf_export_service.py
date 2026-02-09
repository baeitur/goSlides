"""PDF export for participant/registrant lists."""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def export_registrants_pdf(activity, registrants):
    """Generate PDF buffer with participant list for the activity."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6,
    )
    story = []
    story.append(Paragraph("Go Slides – Participant List", title_style))
    story.append(Paragraph(activity.title, styles["Heading2"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"Activity date: {activity.date.strftime('%d %B %Y') if activity.date else 'TBA'}", styles["Normal"]))
    story.append(Spacer(1, 0.8 * cm))

    data = [["#", "Name", "School", "Email", "Phone", "Status", "Attended"]]
    for i, r in enumerate(registrants, 1):
        data.append([
            str(i),
            r.name or "",
            r.school or "",
            r.email or "",
            r.phone or "",
            r.status or "",
            "Yes" if r.attended_at else "No",
        ])

    t = Table(data, colWidths=[1.2 * cm, 3.5 * cm, 3.5 * cm, 4 * cm, 3 * cm, 1.8 * cm, 1.5 * cm])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1BA3A8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
        ])
    )
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer
