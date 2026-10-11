from collections import defaultdict

SUBJECTS = [
    "Thermodynamics",
    "Manufacturing",
    "Materials",
    "Mechanics of Materials",
    "Automobile Engineering",
]

QUESTION_BANK = [
    {"id":"T1","subject":"Thermodynamics","difficulty":"Easy","question":"For an ideal gas undergoing an isothermal process, which property remains constant?","options":["Pressure","Volume","Temperature","Density"],"answer":"Temperature","explanation":"An isothermal process occurs at constant temperature."},
    {"id":"T2","subject":"Thermodynamics","difficulty":"Medium","question":"For a heat engine, thermal efficiency is best expressed as:","options":["Heat rejected / heat supplied","Net work output / heat supplied","Heat supplied / net work output","Net work output / heat rejected"],"answer":"Net work output / heat supplied","explanation":"Thermal efficiency is the useful net work divided by heat supplied."},
    {"id":"T3","subject":"Thermodynamics","difficulty":"Hard","question":"For a reversible adiabatic process of an ideal gas, which quantity remains constant?","options":["Enthalpy","Entropy","Pressure","Volume"],"answer":"Entropy","explanation":"A reversible adiabatic process is isentropic."},
    {"id":"M1","subject":"Manufacturing","difficulty":"Easy","question":"Which process is commonly used to produce a part by forcing molten metal into a mould?","options":["Forging","Casting","Broaching","Rolling"],"answer":"Casting","explanation":"Casting fills a mould with molten material, which solidifies into the desired shape."},
    {"id":"M2","subject":"Manufacturing","difficulty":"Medium","question":"In machining, increasing cutting speed generally tends to increase which effect?","options":["Tool temperature","Tool life in all cases","Workpiece density","Chip thickness in all cases"],"answer":"Tool temperature","explanation":"Higher cutting speed generally raises heat generation and cutting-zone temperature."},
    {"id":"M3","subject":"Manufacturing","difficulty":"Hard","question":"In statistical process control, a control chart is primarily used to:","options":["Calculate component mass","Monitor process variation over time","Choose material colour","Replace all inspections"],"answer":"Monitor process variation over time","explanation":"Control charts help distinguish common-cause variation from potential special causes."},
    {"id":"MA1","subject":"Materials","difficulty":"Easy","question":"Which property describes resistance to indentation or scratching?","options":["Hardness","Ductility","Malleability","Creep"],"answer":"Hardness","explanation":"Hardness measures resistance to localized plastic deformation such as indentation."},
    {"id":"MA2","subject":"Materials","difficulty":"Medium","question":"Which heat treatment is commonly used to increase steel hardness by forming martensite?","options":["Annealing only","Quenching","Normalizing only","Stress relieving only"],"answer":"Quenching","explanation":"Quenching rapidly cools austenitized steel and can form hard martensite, depending on composition."},
    {"id":"MA3","subject":"Materials","difficulty":"Hard","question":"Fatigue failure is most closely associated with:","options":["Repeated or fluctuating loading","Only constant compressive load","Only high static temperature","Zero stress"],"answer":"Repeated or fluctuating loading","explanation":"Fatigue cracks can initiate and grow under cyclic or fluctuating stresses."},
    {"id":"S1","subject":"Mechanics of Materials","difficulty":"Easy","question":"Normal stress under a uniform axial load is calculated as:","options":["Force × area","Force / area","Area / force","Force + area"],"answer":"Force / area","explanation":"For uniform axial loading, normal stress is force divided by cross-sectional area."},
    {"id":"S2","subject":"Mechanics of Materials","difficulty":"Medium","question":"For a linear elastic material within its proportional limit, Hooke's law relates stress to:","options":["Strain","Density","Hardness","Thermal conductivity"],"answer":"Strain","explanation":"In the linear elastic region, stress is proportional to strain."},
    {"id":"S3","subject":"Mechanics of Materials","difficulty":"Hard","question":"For a simply supported beam with a central point load, the maximum bending moment occurs:","options":["At either support","At the centre","At one-quarter span only","Outside the beam"],"answer":"At the centre","explanation":"For a central point load on a simply supported beam, maximum bending moment occurs at midspan."},
    {"id":"A1","subject":"Automobile Engineering","difficulty":"Easy","question":"What is the primary purpose of an automotive differential?","options":["Allow driven wheels to rotate at different speeds","Increase tyre pressure","Cool engine oil directly","Control valve timing"],"answer":"Allow driven wheels to rotate at different speeds","explanation":"A differential allows left and right driven wheels to rotate at different speeds during turns."},
    {"id":"A2","subject":"Automobile Engineering","difficulty":"Medium","question":"ABS primarily helps prevent:","options":["Wheel lock-up during braking","Engine overheating","Battery overcharging","Tyre wear under every condition"],"answer":"Wheel lock-up during braking","explanation":"Anti-lock braking systems modulate braking to help prevent wheel lock-up."},
    {"id":"A3","subject":"Automobile Engineering","difficulty":"Hard","question":"In a conventional four-stroke engine, one complete cycle takes how many crankshaft revolutions?","options":["One","Two","Three","Four"],"answer":"Two","explanation":"Intake, compression, power and exhaust occur over two crankshaft revolutions."},
]

DIFFICULTY_WEIGHT = {"Easy": 1, "Medium": 2, "Hard": 3}

class PlacementAgent:
    """A small explainable agent that tracks performance and selects follow-up questions."""
    def __init__(self):
        self.history = []
        self.mastered_ids = set()

    def record_answer(self, question, selected, correct):
        self.history.append({
            "question_id": question["id"],
            "question": question["question"],
            "subject": question["subject"],
            "selected": selected,
            "correct": bool(correct),
            "difficulty": question["difficulty"],
        })
        if correct:
            self.mastered_ids.add(question["id"])

    def subject_scores(self):
        scores = {}
        for subject in SUBJECTS:
            entries = [h for h in self.history if h["subject"] == subject]
            correct = sum(1 for h in entries if h["correct"])
            attempted = len(entries)
            scores[subject] = {
                "correct": correct,
                "attempted": attempted,
                "percent": round(100 * correct / attempted) if attempted else 0,
            }
        return scores

    def weakest_subject(self):
        scores = self.subject_scores()
        attempted_subjects = [s for s in SUBJECTS if scores[s]["attempted"] > 0]
        if not attempted_subjects:
            return SUBJECTS[0]
        return min(attempted_subjects, key=lambda s: (scores[s]["percent"], -scores[s]["attempted"]))

    def choose_next_question(self, answered_ids=None):
        answered_ids = set(answered_ids or [])
        available = [q for q in QUESTION_BANK if q["id"] not in answered_ids]
        if not available:
            # Recycle the bank only after all questions have been attempted.
            available = list(QUESTION_BANK)
        if not self.history:
            return available[0]
        scores = self.subject_scores()
        attempted = [s for s in SUBJECTS if scores[s]["attempted"] > 0]
        if not attempted:
            target = SUBJECTS[0]
        else:
            target = min(attempted, key=lambda s: (scores[s]["percent"], -scores[s]["attempted"]))
        same_subject = [q for q in available if q["subject"] == target]
        if same_subject:
            # After a wrong answer, prioritize an easier/reinforcement question when available.
            last = self.history[-1]
            if not last["correct"]:
                same_subject.sort(key=lambda q: DIFFICULTY_WEIGHT[q["difficulty"]])
            else:
                same_subject.sort(key=lambda q: DIFFICULTY_WEIGHT[q["difficulty"]], reverse=True)
            return same_subject[0]
        return available[0]

def make_revision_plan(agent, target_role, days, daily_minutes):
    scores = agent.subject_scores()
    if agent.history:
        ordered = sorted(
            SUBJECTS,
            key=lambda s: (
                scores[s]["percent"] if scores[s]["attempted"] else -1,
                -scores[s]["attempted"]
            )
        )
    else:
        ordered = list(SUBJECTS)
    role_bonus = {
        "Automotive": "Connect the concept to a vehicle system and explain one real-world application.",
        "Manufacturing / Quality": "Revise the process, common defects, inspection methods and one quality tool.",
        "Design / CAE": "Revise governing equations, assumptions, boundary conditions and one design example.",
        "Mechanical Core": "Revise the key definition, governing equation and one solved numerical problem.",
    }
    plan = []
    for day in range(1, days + 1):
        subject = ordered[(day - 1) % len(ordered)]
        score = scores[subject]
        if score["attempted"] == 0:
            reason = "No diagnostic answers yet; establish a baseline."
        else:
            reason = f"Current diagnostic score: {score['percent']}%."
        plan.append({
            "day": day,
            "subject": subject,
            "minutes": daily_minutes,
            "activity": role_bonus[target_role],
            "reason": reason,
        })
    return plan
