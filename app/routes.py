import os
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
    jsonify,
    current_app,
)
from werkzeug.utils import secure_filename
from docx import Document

from app.extensions import db
from app.models import Meeting
from app.services.ai_service import (
    process_meeting_transcript,
    chat_with_meeting_context,
)
from app.services.pdf_service import create_meeting_minutes_pdf

main_bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"txt", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(file_path):
    try:
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Read Error: {e}")
        return None


@main_bp.route("/")
def homepage():
    return render_template("index.html")


@main_bp.route("/upload")
def upload_page():
    return render_template("upload.html")


@main_bp.route("/process", methods=["POST"])
def process_transcript():
    transcript_text = ""
    title = request.form.get("meeting_title", "Untitled")

    if request.form.get("transcript_text", "").strip():
        transcript_text = request.form.get("transcript_text")
    else:
        file = request.files.get("transcript_file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            transcript_text = extract_text(filepath)
            os.remove(filepath)

    if not transcript_text or len(transcript_text) < 20:
        flash("Transcript too short or invalid.", "error")
        return redirect(url_for("main.upload_page"))

    try:
        ai_res = process_meeting_transcript(transcript_text)
        meeting = Meeting(
            title=title,
            summary=ai_res.get("summary"),
            action_items=ai_res.get("action_items"),
            decisions=ai_res.get("decisions"),
            original_transcript=transcript_text,
            sentiment=ai_res.get("sentiment"),
            keywords=ai_res.get("keywords"),
        )
        db.session.add(meeting)
        db.session.commit()
        return redirect(url_for("main.view_results", meeting_id=meeting.id))
    except Exception as e:
        print(f"Error: {e}")
        flash(f"Processing Error: {e}", "error")
        return redirect(url_for("main.upload_page"))


@main_bp.route("/results/<int:meeting_id>")
def view_results(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    return render_template("results.html", meeting=meeting)


@main_bp.route("/history")
def past_meetings():
    meetings = Meeting.query.order_by(Meeting.date_created.desc()).all()
    return render_template("past_meetings.html", meetings=meetings)


@main_bp.route("/export/<int:meeting_id>")
def export_pdf(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    try:
        pdf_path = create_meeting_minutes_pdf(meeting)
        return send_file(
            pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path)
        )
    except Exception as e:
        flash(f"Export Error: {e}", "error")
        return redirect(url_for("main.view_results", meeting_id=meeting_id))


@main_bp.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.json
    meeting = Meeting.query.get_or_404(data.get("meeting_id"))
    answer = chat_with_meeting_context(
        meeting.original_transcript, data.get("question")
    )
    return jsonify({"answer": answer})
