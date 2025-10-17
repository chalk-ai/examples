from enum import Enum

from pydantic import BaseModel, Field


# TODO(elvis): different AI summary based on meeting type
class MeetingType(str, Enum):
    kickoff = "kickoff"
    office_hours = "office_hours"
    discovery = "discovery"
    pilot_planning = "pilot_planning"
    internal_meeting = "internal_meeting"
    go_live = "go_live"
    pricing = "pricing"
    book_club = "book_club"
    case_study = "case_study"
    misc_and_vendor = "misc_and_vendor"
    missing = "missing"


class StructuredOutputMeetingType(BaseModel):
    meeting_type: MeetingType = Field(
        ...,
        description=(
            "The categorized type of meeting based on its title or purpose. "
            "Options:\n"
            "- kickoff: Pilot, project, or sandbox planning.\n"
            "- office_hours: Customer onboarding, office hours, technical syncs, support, pairing.\n"
            "- discovery: Discovery, walkthroughs, demos, new stakeholder intros.\n"
            "- pilot_planning: Trials, proofs of concept (POCs), product testing.\n"
            "- internal_meeting: Internal team onboarding, training, or enablement (not customer onboarding).\n"
            "- go_live: Deployments, migrations, or post-launch reviews.\n"
            "- pricing: Commercial/pricing discussions.\n"
            "- book_club: Internal learning or book club.\n"
            "- case_study: Case study interviews or related discussions.\n"
            "- misc_and_vendor: Vague, unclear, or placeholder titles; meetings with external vendors/partners that are not about Chalk deployment or customer-facing projects."
        ),
    )


def prompt_meeting_type_user() -> str:
    return """
    You are a system that classifies meeting titles into specific categories based on their content and purpose. Use the following categories:

    1. **kickoff**
       Initial meetings to start a pilot, project, or engagement. This includes planning sessions, strategic discussions, and sandbox or trial planning.

    2. **office_hours**
       Any collaborative or technical working session involving the customer, including office hours, customer onboarding, infrastructure discussions, pairing, live troubleshooting, support calls, debugging sessions, or general syncs and check-ins.

    3. **discovery**
       Introductory conversations, discovery calls, product demos, or walkthroughs with new stakeholders or teams.

    4. **pilot_planning**
       Meetings focused on product evaluations, trials, proof of concepts (POCs), testing phases, or determining fit.

    5. **internal_meeting**
       Internal team meetings for onboarding, training, or enablement. This category is for internal onboarding and training—not for customer onboarding (which belongs in office_hours).

    6. **go_live**
       Meetings related to launching something into production, conducting a go-live, migrations, or post-deployment reviews.

    7. **pricing**
       Discussions centered on pricing, commercial terms, or contract negotiations.

    8. **book_club**
       Internal learning-focused sessions like book clubs, team knowledge sharing, or educational discussions.

    9. **case_study**
       Meetings to gather information for or discuss customer case studies, testimonials, or success stories.

    10. **misc_and_vendor**
        Titles that are too vague, unclear, or act as placeholders, as well as meetings with external vendors or partners that are not about deploying Chalk or customer-facing projects.

   11. **missing**
        If the meeting title is missing, not one of the categories above, or cannot be classified then return the classification as **missing**.

    Your output should be:
    {
        "meeting_type": "<enum_value>"
    }
    ---

    Given the following meeting title, classify it into exactly **one** of the categories above by returning the lowercase enum key (e.g., `kickoff`, `discovery`, etc.).

    **Meeting Title:** "{{ FathomCall.meeting_title }}"

    **Transcript** {{ FathomCall.transcript }}

    """
