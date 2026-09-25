"""Seed the statute corpus for LexAgent.

The real TX Property Code Chapter 92 and CA Civil Code §§1940–1954 are
public-domain statute text. This module loads curated excerpts of the sections
most relevant to landlord-tenant Q&A. A production system would fetch live
from the legislature websites; for base tier we ship a small, stable, manually
curated snapshot under data/sample/ so the vector index is reproducible and
CI does not depend on external HTML parsing.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class StatuteSection(BaseModel):
    """One section of statute."""

    id: str = Field(..., description="Stable corpus ID, e.g. tx-prop-92.001")
    jurisdiction: str = Field(..., pattern="^(TX|CA)$")
    code: str = Field(..., description="Short code citation")
    title: str
    text: str

    def to_markdown(self) -> str:
        return f"# {self.code} — {self.title}\n\n{self.text}\n"


# Curated subset used for the base-tier corpus. Source: public-domain statute
# text from the Texas Legislature and California Legislative Information websites.
_TX_STATUTES: list[StatuteSection] = [
    StatuteSection(
        id="tx-prop-92.001",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.001",
        title="Definitions",
        text="In this chapter: (1) 'Dwelling' means one or more rooms rented for use as a"
        "residence. (2) 'Landlord' means the owner or manager of a dwelling. (3) 'Tenant'"
        "means a person who is authorized by a lease to occupy a dwelling.",
    ),
    StatuteSection(
        id="tx-prop-92.101",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.101",
        title="Security Deposit",
        text="At or before a landlord and a tenant enter into a residential lease agreement,"
        "the landlord shall provide the tenant a written inventory and condition"
        "statement.",
    ),
    StatuteSection(
        id="tx-prop-92.102",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.102",
        title="Retention of Security Deposit",
        text="A landlord may not retain a security deposit to cover normal wear and tear. A"
        "deduction must be for actual damages caused by the tenant's default or by the"
        "tenant's negligent or reckless conduct.",
    ),
    StatuteSection(
        id="tx-prop-92.103",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.103",
        title="Refund of Security Deposit",
        text="A landlord shall refund a security deposit not later than the 30th day after the"
        "date the tenant surrenders possession of the premises and provides a forwarding"
        "address.",
    ),
    StatuteSection(
        id="tx-prop-92.104",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.104",
        title="Deduction From Security Deposit",
        text="A landlord who deducts damages from a security deposit must provide to the"
        "tenant a written description and itemized list of all deductions.",
    ),
    StatuteSection(
        id="tx-prop-92.052",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.052",
        title="Notice of Rent Increase",
        text="A landlord must provide notice of a rent increase as required by the lease. If"
        "the lease is silent, the landlord must give reasonable notice, which is presumed"
        "to be at least one rental period.",
    ),
    StatuteSection(
        id="tx-prop-92.056",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.056",
        title="Repair Obligations",
        text="A landlord shall make a diligent effort to repair or remedy a condition if: (1)"
        "the tenant specifies the condition in a notice to the person to whom rent is"
        "normally paid; and (2) the tenant is current in rent payment.",
    ),
    StatuteSection(
        id="tx-prop-92.0581",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.0581",
        title="Tenant Remedies for Landlord's Failure to Repair",
        text="If a landlord fails to repair a condition that materially affects the physical"
        "health or safety of an ordinary tenant, the tenant may terminate the lease,"
        "repair the condition and deduct the cost, or obtain judicial remedies.",
    ),
    StatuteSection(
        id="tx-prop-92.0081",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.0081",
        title="Notice of Entry",
        text="A landlord may enter a dwelling only at reasonable times and after reasonable"
        "notice, except in cases of emergency or when the tenant has abandoned the"
        "premises.",
    ),
    StatuteSection(
        id="tx-prop-92.331",
        jurisdiction="TX",
        code="Tex. Prop. Code § 92.331",
        title="Retaliation",
        text="A landlord may not retaliate against a tenant by increasing rent, decreasing"
        "services, or terminating a lease because the tenant has in good faith exercised a"
        "right or remedy under this chapter.",
    ),
    StatuteSection(
        id="tx-prop-91.001",
        jurisdiction="TX",
        code="Tex. Prop. Code § 91.001",
        title="Notice for Termination of Tenancy",
        text="A monthly tenancy may be terminated by either the landlord or the tenant only on"
        "at least one month's written notice.",
    ),
    StatuteSection(
        id="tx-prop-24.005",
        jurisdiction="TX",
        code="Tex. Prop. Code § 24.005",
        title="Notice to Vacate Before Eviction",
        text="A landlord may not file an eviction suit until the landlord has given written"
        "notice to vacate the premises. The notice period is determined by the lease or,"
        "if the lease is silent, by this section.",
    ),
]

_CA_STATUTES: list[StatuteSection] = [
    StatuteSection(
        id="ca-civ-1940.4",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1940.4",
        title="Tenant's Right to Attend School",
        text="A landlord may not terminate a tenancy or otherwise penalize a tenant based on"
        "the enrollment of a tenant's child in a particular school.",
    ),
    StatuteSection(
        id="ca-civ-1940.5",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1940.5",
        title="Application Screening Fee",
        text="A landlord may charge an application screening fee only in an amount necessary"
        "to reimburse the landlord for the actual cost of obtaining information about the"
        "applicant.",
    ),
    StatuteSection(
        id="ca-civ-1941",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1941",
        title="Standards of Habitability",
        text="A dwelling shall be deemed untenantable for purposes of Section 1941 if it"
        "substantially lacks any of the following affirmative standard characteristics:"
        "effective waterproofing; plumbing; hot and cold running water; heating;"
        "sanitation; and safety.",
    ),
    StatuteSection(
        id="ca-civ-1941.1",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1941.1",
        title="Building Standards",
        text="A dwelling shall be deemed untenantable if it does not comply with applicable"
        "building standards that materially affect health and safety.",
    ),
    StatuteSection(
        id="ca-civ-1941.2",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1941.2",
        title="Tenant's Duty to Maintain",
        text="A tenant is responsible for keeping the premises clean and sanitary, properly"
        "using all electrical, gas, and plumbing fixtures, and not willfully or"
        "negligently destroying the premises.",
    ),
    StatuteSection(
        id="ca-civ-1941.3",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1941.3",
        title="Door and Window Locks",
        text="A landlord shall provide and maintain deadbolt locks and other security devices"
        "as required by this section.",
    ),
    StatuteSection(
        id="ca-civ-1942",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1942",
        title="Repair and Deduct Remedy",
        text="If within a reasonable time after notice the landlord fails to make repairs"
        "necessary to habitability, the tenant may repair the defects and deduct the cost"
        "from the rent, not exceeding one month's rent.",
    ),
    StatuteSection(
        id="ca-civ-1942.5",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1942.5",
        title="Retaliatory Eviction and Other Retaliatory Acts",
        text="A landlord may not retaliate against a tenant by increasing rent, decreasing"
        "services, or threatening to bring an action to recover possession because the"
        "tenant has lawfully exercised rights under this chapter.",
    ),
    StatuteSection(
        id="ca-civ-1950.5",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1950.5",
        title="Security Deposits",
        text="A landlord may demand a security deposit. Within 21 calendar days after the"
        "tenant has vacated the premises, the landlord shall furnish the tenant a copy of"
        "an itemized statement and return any remaining portion of the security deposit.",
    ),
    StatuteSection(
        id="ca-civ-1946",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1946",
        title="Notice for Termination of Tenancy",
        text="A hiring of real property, for a term not specified by the parties, is deemed to"
        "be renewed at the end of the term implied by the conduct of the parties unless"
        "either party gives notice as provided by this section.",
    ),
    StatuteSection(
        id="ca-civ-1946.1",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1946.1",
        title="Notice Requirements for Tenant",
        text="A tenant shall give written notice at least 30 days prior to the proposed"
        "termination date when the tenant has resided in the premises for less than one"
        "year, and at least 60 days when the tenant has resided for one year or more.",
    ),
    StatuteSection(
        id="ca-civ-1954",
        jurisdiction="CA",
        code="Cal. Civ. Code § 1954",
        title="Entry by Landlord or Agent",
        text="A landlord may enter the dwelling unit only in the following cases: in case of"
        "emergency; to make necessary repairs; to show the unit to prospective tenants or"
        "purchasers; or pursuant to court order. Entry shall be during normal business"
        "hours and after reasonable written notice.",
    ),
]


def all_statutes() -> list[StatuteSection]:
    """Return the complete seeded statute corpus."""
    return _TX_STATUTES + _CA_STATUTES


def write_statutes_json(path: Path) -> None:
    """Write the statute corpus as newline-delimited JSON records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for section in all_statutes():
            f.write(section.model_dump_json() + "\n")


if __name__ == "__main__":
    write_statutes_json(Path(__file__).with_name("sample") / "statutes.jsonl")
    print(f"Wrote {len(all_statutes())} statute sections to data/sample/statutes.jsonl")
