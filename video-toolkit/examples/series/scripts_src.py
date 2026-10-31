"""Single source for the four episode scripts.

Each line: (caption, say-or-None, new?, source-or-None). Writes ep*/script.json and the review doc data.
Approved wording from the PCL video is reused verbatim (new=False); new lines carry a source.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
FSO, DCSA = "F S O", "DCSA"

def L(cap, say=None, new=False, src=None):
    return {"cap": cap, **({"say": say} if say else {}), "new": new, **({"src": src} if src else {})}

def fso(s):  # spoken form for captions that mention FSO / SF 86 / SOR / SF 312 / eApp
    return (s.replace("FSO", FSO).replace("SF 86", "S F eighty-six").replace("SF 312", "S F three-twelve")
             .replace("SOR", "S O R").replace("eApp", "e-App").replace("DCSA's", "D C S A's").replace("DOHA's", "Doha's")
             .replace("878-274-1186", "eight seven eight, two seven four, one one eight six"))

def A(cap, new=False, src=None):  # line whose spoken form is derived automatically
    say = fso(cap)
    return L(cap, say if say != cap else None, new, src)

PARTS = ["Submission", "Investigation", "Adjudication", "Maintenance"]

def series_scene(part, lines):
    return {"id": "map", "step": None, "label": f"Part {part} of 4", "lines": lines}

EP = {}

EP[1] = {
    "title": "Your Security Clearance, Part 1: Submission", "series": {"part": 1, "name": "Submission"},
    "scenes": [
        {"id": "title", "step": None, "label": "", "lines": [A("Your security clearance, part one: submission.", True)]},
        series_scene(1, [
            A("Getting a clearance happens in four chunks: submission, investigation, adjudication, and maintenance.", True),
            A("This part covers everything up to the moment your application reaches DCSA.", True)]),
        {"id": "meet", "step": None, "label": "Meet Alex", "lines": [
            A("Meet Alex. Alex just accepted a job that needs a security clearance."),
            A("A clearance is the government's decision that you're eligible for access to classified information."),
            A("For contractor employees, that decision belongs to DCSA: the Defense Counterintelligence and Security Agency.")]},
        {"id": "basics", "step": None, "label": "Before you start", "lines": [
            A("First, the basics. Only an organization with a facility clearance, or a federal agency, can sponsor you for security clearance eligibility."),
            A("And access to classified information is only granted on a need-to-know basis. There are no \"just in case\" clearances."),
            A("If you need access on day one, the process can start pre-employment."),
            A("But if the employment is with a private company, that company is required to have you in a cleared position within 45 days of your eligibility being granted."),
            A("This video follows a contractor employee like Alex. If you'll work directly for a federal agency, its security office will guide you, and some later steps differ.")]},
        {"id": "s1", "step": 1, "label": "Your FSO starts the request", "lines": [
            A("Step one. You will need to show proof of U.S. citizenship to your Facility Security Officer, or FSO."),
            A("Your FSO can check your documents in person or digitally.", True, "DCSA VOI July 2026 (citizenship documents update)"),
            A("Then your FSO will start your investigation request, and you get an email invitation to complete the eApp in NBIS, DCSA's online application.")]},
        {"id": "s2", "step": 2, "label": "You complete the SF 86 in eApp", "lines": [
            A("Step two is yours. In eApp, you complete the SF 86, the Questionnaire for National Security Positions."),
            A("It asks where you've lived, worked, and studied, plus foreign contacts, travel, finances, and more."),
            A("Most questions look back seven to ten years, so you'll need dates, addresses, and people who can vouch for you.", True, "DCSA VOI June 2026 (PVQ: look-back reduced from 7–10 years to 5)"),
            A("You should gather records first, so you're prepared for the questionnaire."),
            A("Be complete and be honest. Leaving something out can hurt you more than the thing itself."),
            A("Before you submit, check for gaps in your timeline, and make sure every date and address is filled in.", True, "Practical advice (not a rule)"),
            A("You'll also sign release forms and get your fingerprints taken electronically."),
            A("Your signed release pages and your fingerprint results are each good for 120 days, so don't let your application sit.", True, "DCSA VOI January 2025 (fingerprint timing)"),
            A("Heads up: a newer form, the Personnel Vetting Questionnaire, is being phased in to replace the SF 86."),
            A("It shortens most look-back periods to five years.", True, "DCSA VOI June 2026")]},
        {"id": "s3", "step": 3, "label": "Your FSO reviews it", "lines": [
            A("Step three. Your FSO reviews the form for completeness."),
            A("What you disclose isn't shared around the company. The NISPOM strictly prohibits that."),
            A("Once the FSO review is complete, it will be released to DCSA, along with your fingerprints.")]},
        {"id": "s4", "step": 4, "label": "DCSA checks the package", "lines": [
            A("Step four. DCSA checks that everything is there. If something's missing, it goes back to your FSO, and you fix it and resubmit."),
            A("Missing fingerprints are a common reason a request gets rejected, so they should be taken close to when your form is released.", True, "DCSA VOI January 2025")]},
        {"id": "next", "step": None, "label": "Wrap-up", "lines": [
            A("That's submission: a sponsor with a real need, proof of citizenship, a complete and honest SF 86, releases and fingerprints, and an FSO review.", True),
            A("Next, in part two: the investigation.", True)]},
        {"id": "end", "step": None, "label": "", "hold": 6.0, "lines": []},
    ]}

EP[2] = {
    "title": "Your Security Clearance, Part 2: Investigation", "series": {"part": 2, "name": "Investigation"},
    "scenes": [
        {"id": "title", "step": None, "label": "", "lines": [A("Your security clearance, part two: investigation.", True)]},
        series_scene(2, [
            A("In part one, Alex's application reached DCSA. Now comes the investigation, where DCSA checks the facts.", True)]),
        {"id": "s5", "step": 5, "label": "Temporary eligibility", "lines": [
            A("Step five. While the full investigation runs, DCSA may grant temporary eligibility. You may hear it called an \"interim.\""),
            A("It's based on your form and early checks, and it can let you start cleared work sooner."),
            A("It has limits, and not getting temporary eligibility is not a denial. It just means you wait for the final decision."),
            A("Those limits: temporary Secret doesn't cover Restricted Data, COMSEC, or NATO information. Those need a final decision.", True, "32 CFR 117.10(l)(1)"),
            A("And temporary eligibility can't last more than a year unless DCSA approves.", True, "32 CFR 117.10(l)")]},
        {"id": "s6", "step": 6, "label": "The background investigation", "lines": [
            A("Step six: the background investigation. DCSA checks records like criminal history and credit."),
            A("How deep it goes depends on your level: a moderate-tier investigation for Secret, and a high-tier one for Top Secret.", True, "Federal Personnel Vetting Investigative Standards (2022) crosswalk"),
            A("Checks can include national databases, your fingerprints, your credit, and your education and employment history.", True, "Federal investigative standards (hedged: \"can include\")"),
            A("Investigators may interview you, your references, and people who know you. Top Secret investigations dig deeper."),
            A("An interview is your chance to explain anything on your form. Keep a copy of your SF 86 handy, and if you don't know an answer, say so.", True, "Practical advice (not a rule)"),
            A("If you speak to an investigator, answer promptly and honestly.")]},
        {"id": "s6b", "step": 6, "label": "Who's who, and waiting", "lines": [
            A("DCSA investigators carry an official DCSA credential card.", True, "DCSA VOI October 2026"),
            A("And if you're unsure an investigator is legitimate, DCSA can verify them. You can contact DCSA by calling 878-274-1186.",
              src=None),
            A("Investigators don't decide your clearance. They gather the facts and report them to an adjudicator.", True, "32 CFR 117.10(a); investigation and adjudication are separate functions"),
            A("While you wait, you can follow your case status online in DCSA's Individual Engagement Platform.", True, "DCSA VOI June 2026 (IEP is live and applicant-facing)"),
            A("And keep your FSO posted about changes, like a foreign trip or a new arrest. Reporting rules already apply while your case is in process.", True, "ISL 2021-02 (covered individuals include those in process)")]},
        {"id": "next", "step": None, "label": "Wrap-up", "lines": [
            A("That's the investigation: temporary eligibility if you qualify, then record checks and interviews.", True),
            A("When it's done, the results go to an adjudicator. That's part three.", True)]},
        {"id": "end", "step": None, "label": "", "hold": 6.0, "lines": []},
    ]}

EP[3] = {
    "title": "Your Security Clearance, Part 3: Adjudication", "series": {"part": 3, "name": "Adjudication"},
    "scenes": [
        {"id": "title", "step": None, "label": "", "lines": [A("Your security clearance, part three: adjudication.", True)]},
        series_scene(3, [A("The investigation is done. Now someone decides. That's adjudication.", True)]),
        {"id": "s7", "step": 7, "label": "Adjudication", "lines": [
            A("Step seven: adjudication. A DCSA adjudicator weighs your case against 13 national adjudicative guidelines, set out in Security Executive Agent Directive 4."),
            A("The 13 are: allegiance to the United States, foreign influence, foreign preference, sexual behavior, and personal conduct;", True, "SEAD 4, guidelines A–E (replaces the approved five-item list, at the owner's request)"),
            A("financial considerations, alcohol consumption, drug involvement and substance misuse, and psychological conditions;", True, "SEAD 4, guidelines F–I"),
            A("criminal conduct, handling protected information, outside activities, and use of information technology.", True, "SEAD 4, guidelines J–M"),
            A("Each guideline lists conditions that raise a concern, and conditions that can ease it.", True, "SEAD 4 (each guideline: disqualifying and mitigating conditions)"),
            A("You are looked at as a whole person. A single bad moment in time doesn't automatically mean a denial.")]},
        {"id": "s7b", "step": 7, "label": "The whole person", "lines": [
            A("Adjudicators weigh how serious it was, how recent and how often, your age at the time, whether it was voluntary, and whether you've changed.", True, "SEAD 4 whole-person factors (same nine as 32 CFR 147.2)"),
            A("Time, honesty, and changed behavior can mitigate past issues."),
            A("But any real doubt is resolved in favor of national security.", True, "SEAD 4; 32 CFR 147.2(b)"),
            A("Most cases end here, with a favorable decision. Some are approved with conditions and extra monitoring."),
            A("That's called conditional eligibility. DCSA can use it to monitor a concern through continuous vetting instead of starting due process.", True, "DCSA VOI January 2025 (conditionals since February 2024)")]},
        {"id": "s8", "step": 8, "label": "Issues? DOHA reviews", "lines": [
            A("If the adjudicator can't decide in your favor, the case goes to DOHA, the Defense Office of Hearings and Appeals."),
            A("If DOHA's attorneys agree there's a real concern, you receive a Statement of Reasons, or SOR, listing each one."),
            A("If they don't agree, eligibility can still be granted.")]},
        {"id": "s9", "step": 9, "label": "You respond to the SOR", "lines": [
            A("Step nine: if you receive an SOR and want to pursue the clearance, you will need to respond."),
            A("You have 20 days to answer in writing, under oath, admitting or denying each allegation."),
            A("You can choose: a hearing before an administrative judge, or a decision on the written record.")]},
        {"id": "s9b", "step": 9, "label": "Hearing or written record", "lines": [
            A("On the written record, you get a copy of the government's evidence and have 30 days to respond with your own documents and explanation.", True, "32 CFR 155, Encl. 3 ¶7"),
            A("At a hearing, a government attorney called Department Counsel presents the case. You can testify, call witnesses, and present documents.", True, "32 CFR 155, Encl. 3 ¶¶14–15"),
            A("You carry the burden of persuasion, so explain the circumstances and show what has changed.", True, "32 CFR 155, Encl. 3 ¶15"),
            A("You may bring a lawyer or a personal representative. If you don't respond at all, the clearance is denied.")]},
        {"id": "s10", "step": 10, "label": "Decision and appeal", "lines": [
            A("Step ten: the judge decides. Either side can appeal to the DOHA Appeal Board within 15 days."),
            A("A final denial means waiting one year before your employer can apply again.")]},
        {"id": "next", "step": None, "label": "Wrap-up", "lines": [
            A("That's adjudication: the guidelines, the whole person, and due process if there are concerns.", True),
            A("Once you're approved, a clearance needs looking after. That's part four: maintenance.", True)]},
        {"id": "end", "step": None, "label": "", "hold": 6.0, "lines": []},
    ]}

EP[4] = {
    "title": "Your Security Clearance, Part 4: Maintenance", "series": {"part": 4, "name": "Maintenance"},
    "bar": {"steps": ["Briefing", "Need-to-know", "Continuous vetting", "Reporting", "Jobs and leaving"],
            "bracket": None, "scenes": ["access", "ntk", "cv", "report", "report2", "moves"]},
    "scenes": [
        {"id": "title", "step": None, "label": "", "lines": [A("Your security clearance, part four: maintenance.", True)]},
        series_scene(4, [A("Alex is approved. Now the job is keeping the clearance in good standing.", True)]),
        {"id": "access", "step": 1, "label": "Eligible is not the same as access", "lines": [
            A("Now, let's say Alex is approved. Being eligible isn't the same as access."),
            A("Before seeing anything classified, Alex gets an initial security briefing and signs the SF 312, a nondisclosure agreement that lasts for life."),
            A("The briefing covers threats, including insider threats, counterintelligence, how classification works, and your reporting duties.", True, "32 CFR 117.12(e)")]},
        {"id": "ntk", "step": 2, "label": "Need-to-know and refreshers", "lines": [
            A("And Alex only sees what the job requires. That's called need-to-know."),
            A("Every 12 months, you'll get refresher training.", True, "32 CFR 117.12(k)")]},
        {"id": "cv", "step": 3, "label": "Continuous vetting", "lines": [
            A("A clearance isn't one and done. Cleared people are enrolled in continuous vetting, with automated record checks and an updated form about every five years."),
            A("That includes FBI Rap Back, which alerts DCSA to new criminal records in near real time.", True, "DCSA VOI August 2026 (Rap Back expansion)")]},
        {"id": "report", "step": 4, "label": "What you report", "lines": [
            A("Your part: report life changes to your FSO, like foreign travel and contacts, money trouble, or an arrest."),
            A("Before a personal trip abroad, give your FSO your itinerary. Report changes, and unplanned day trips to Canada or Mexico, within five business days of getting back.", True, "ISL 2021-02, Table 4"),
            A("Official travel for your government contract doesn't need to be reported.", True, "ISL 2021-02, Table 4"),
            A("Report close and continuing ties with foreign nationals, and any contact with someone you think may be a foreign intelligence officer.", True, "ISL 2021-02, Table 2")]},
        {"id": "report2", "step": 4, "label": "What you report", "lines": [
            A("Also report attempts to get classified information from you, an arrest, alcohol- or drug-related treatment, bankruptcy, or a debt more than 120 days past due.", True, "ISL 2021-02, Table 2"),
            A("Applying for foreign citizenship, using a foreign passport, and media contacts about classified matters are reportable too.", True, "ISL 2021-02, Table 2"),
            A("Top Secret holders report more, including marriage, cohabitation, foreign bank accounts or property, and voting in a foreign election.", True, "ISL 2021-02, Table 3"),
            A("And if you see reportable behavior by another cleared coworker, tell your FSO.", True, "SEAD 3 §F.3; ISL 2021-02")]},
        {"id": "moves", "step": 5, "label": "Changing jobs, and leaving", "lines": [
            A("If you move to another cleared employer, your eligibility generally comes with you. Under federal reciprocity rules, your new FSO confirms it instead of starting over.", True, "SEAD 7"),
            A("When you leave, or no longer need access, your FSO debriefs you. Your SF 312 obligations never end.", True, "32 CFR 117.12(l); SF 312")]},
        {"id": "recap", "step": None, "label": "Series recap", "lines": [
            A("So: your FSO starts it. You complete eApp. DCSA reviews, investigates, and decides, with DOHA stepping in if there are issues."),
            A("Then you're briefed, you sign, and you keep reporting. Tell the truth, meet your deadlines, and talk to your FSO.")]},
        {"id": "end", "step": None, "label": "", "hold": 7.0, "lines": []},
    ]}

if __name__ == "__main__":
    for n, ep in EP.items():
        out = {k: v for k, v in ep.items() if k != "scenes"}
        out["scenes"] = [{**s, "lines": [{k: v for k, v in l.items() if k in ("cap", "say")} for l in s["lines"]]} for s in ep["scenes"]]
        (ROOT / f"ep{n}" / "script.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
        lines = [l for s in ep["scenes"] for l in s["lines"]]
        print(f"ep{n}: {len(lines)} lines, {sum(len(l['cap'].split()) for l in lines)} words, {sum(l['new'] for l in lines)} new")
    (ROOT / "review_data.json").write_text(json.dumps(EP, indent=1, ensure_ascii=False))
