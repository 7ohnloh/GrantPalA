from flask import Blueprint, request, render_template
from database import get_db

eligibility_bp = Blueprint('eligibilityresults', __name__)

@eligibility_bp.route("/eligibilityresults", methods=["POST"])
def evaluate_eligibility():
    data = request.get_json()
    grant = data.get("grant", {})
    project = data.get("project", {})

    results = {
        "project_name": project.get("project_name", "Unnamed Project"),
        "grant_name": grant.get("grant_name", "Unnamed Grant"),
        "match_percent": 0,
        "overall_match": False,
        "timeline": {"match": False, "note": "Not evaluated"},
        "budget": {"match": False, "note": "Not evaluated"},
        "key_directions": {"match": False, "note": "Not evaluated"},
        "other_fields": {}
    }

    score = 0
    total = 3  # Update if you add more fields

    # Match timeline
    timeline_grant = str(grant.get("timeline_condition", "")).lower()
    timeline_proj = str(project.get("timeline", "")).lower()
    if any(kw in timeline_proj for kw in timeline_grant.split()):
        results["timeline"]["match"] = True
        results["timeline"]["note"] = "Project timeline aligns with grant requirement."
        score += 1
    else:
        results["timeline"]["note"] = "Project timeline may not align clearly."

    # Match budget (only if both are present and numeric-like)
    import re
    def extract_number(s):
        s = str(s)  # Convert to string first
        matches = re.findall(r"\d{3,}", s.replace(",", ""))
        return int(matches[0]) if matches else 0


    budget_grant = extract_number(grant.get("budget_policy", ""))
    budget_proj = extract_number(project.get("budget", ""))
    if budget_grant and budget_proj:
        if budget_proj <= budget_grant:
            results["budget"]["match"] = True
            results["budget"]["note"] = f"Project budget (${budget_proj}) is within grant budget (${budget_grant})."
            score += 1
        else:
            results["budget"]["note"] = f"Project budget (${budget_proj}) exceeds grant cap (${budget_grant})."
    else:
        results["budget"]["note"] = "Budget could not be numerically evaluated."

    # Match key directions (intersection)
    grant_dirs = set(map(str.lower, grant.get("key_directions", [])))
    project_dirs = set(map(str.lower, project.get("key_directions", [])))
    overlap = grant_dirs & project_dirs

    if overlap:
        results["key_directions"]["match"] = True
        results["key_directions"]["note"] = f"Shared priorities: {', '.join(overlap)}"
        score += 1
    else:
        results["key_directions"]["note"] = "No overlapping directions found."

    # Optional: Store other comparisons (e.g., eligibility or justification keywords)
    results["other_fields"] = {
        "eligible_applicants": grant.get("eligible_applicants", ""),
        "target_beneficiaries": project.get("target_beneficiaries", ""),
        "selection_criteria": grant.get("selection_criteria", ""),
        "justification": project.get("justification", "")
    }

    # Final scoring
    match_percent = round((score / total) * 100)
    results["match_percent"] = match_percent
    results["overall_match"] = match_percent >= 60  # Set your own threshold

    return render_template("eligibilityresults.html", result=results)
