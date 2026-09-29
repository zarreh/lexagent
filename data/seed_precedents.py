"""Generate a seeded synthetic precedent corpus for LexAgent.

Case summaries are synthetic. They are inspired by the issue types covered in
landlord-tenant coursework but do not reproduce any course material or any
real court opinion. Each record is tagged `synthetic: true`.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class PrecedentSummary(BaseModel):
    """One synthetic case summary."""

    case_id: str
    jurisdiction: str = Field(..., pattern="^(TX|CA)$")
    issue: str
    facts: str
    holding: str
    synthetic: bool = True

    def to_markdown(self) -> str:
        return (
            f"# {self.case_id} ({self.jurisdiction}) — {self.issue}\n\n"
            f"**Facts:** {self.facts}\n\n"
            f"**Holding:** {self.holding}\n"
        )


_ISSUES = [
    "security deposit refund",
    "eviction notice",
    "habitability repair",
    "landlord entry",
    "retaliatory eviction",
    "rent increase",
    "early termination",
    "tenant duty to maintain",
]


def _case_id(index: int) -> str:
    return f"SYN-{index:04d}"


def _tx_precedents() -> list[PrecedentSummary]:
    return [
        PrecedentSummary(
            case_id=_case_id(1),
            jurisdiction="TX",
            issue="security deposit refund",
            facts="Tenant vacated after a one-year lease and provided a forwarding address. "
            "Landlord kept the entire $1,200 deposit for carpet cleaning and minor wall "
            "scuffs.",
            holding="Landlord must return the deposit within 30 days and may only deduct "
            "actual damages beyond normal wear and tear. Tenant awarded the full deposit "
            "plus costs.",
        ),
        PrecedentSummary(
            case_id=_case_id(2),
            jurisdiction="TX",
            issue="eviction notice",
            facts="Landlord posted a three-day oral notice to vacate for nonpayment and "
            "immediately filed eviction.",
            holding="Oral notice does not satisfy Section 24.005. Eviction dismissed for lack "
            "of written notice to vacate.",
        ),
        PrecedentSummary(
            case_id=_case_id(3),
            jurisdiction="TX",
            issue="habitability repair",
            facts="Tenant reported a broken heater in January. Landlord did nothing for three "
            "weeks.",
            holding="Tenant's notice was adequate; landlord's failure to repair materially "
            "affected health and safety. Tenant entitled to repair-and-deduct and partial "
            "rent abatement.",
        ),
        PrecedentSummary(
            case_id=_case_id(4),
            jurisdiction="TX",
            issue="landlord entry",
            facts="Landlord entered repeatedly without notice to show the unit, including once "
            "while tenant was asleep.",
            holding="Entry without reasonable notice violated Section 92.0081 absent emergency "
            "or abandonment. Tenant awarded nominal damages.",
        ),
        PrecedentSummary(
            case_id=_case_id(5),
            jurisdiction="TX",
            issue="retaliatory eviction",
            facts="Tenant complained to the city about code violations. One week later "
            "landlord increased rent by 25%.",
            holding="Rent increase shortly after tenant's good-faith complaint creates a "
            "presumption of retaliation under Section 92.331.",
        ),
        PrecedentSummary(
            case_id=_case_id(6),
            jurisdiction="TX",
            issue="rent increase",
            facts="Month-to-month tenant received one week's notice of a rent increase.",
            holding="One week is not reasonable notice; landlord must provide at least one "
            "rental period's notice.",
        ),
        PrecedentSummary(
            case_id=_case_id(7),
            jurisdiction="TX",
            issue="early termination",
            facts="Tenant broke a six-month lease after two months for a job relocation and "
            "mitigated by finding a replacement tenant.",
            holding="Tenant's mitigation effort limits landlord's damages to actual lost rent "
            "and reasonable re-letting costs.",
        ),
        PrecedentSummary(
            case_id=_case_id(8),
            jurisdiction="TX",
            issue="tenant duty to maintain",
            facts="Tenant intentionally clogged a sink and refused to report it, causing water "
            "damage.",
            holding="Tenant is liable for willful or negligent damage beyond ordinary wear and "
            "tear.",
        ),
    ]


def _ca_precedents() -> list[PrecedentSummary]:
    return [
        PrecedentSummary(
            case_id=_case_id(9),
            jurisdiction="CA",
            issue="security deposit refund",
            facts="Tenant moved out and received no itemized statement. Landlord returned $100 "
            "of a $2,000 deposit 45 days later.",
            holding="Landlord violated Section 1950.5 by failing to provide an itemized "
            "statement within 21 days. Tenant entitled to full refund of remaining "
            "deposit.",
        ),
        PrecedentSummary(
            case_id=_case_id(10),
            jurisdiction="CA",
            issue="habitability repair",
            facts="Roof leaked for two months; landlord ignored written notices. Tenant "
            "withheld rent.",
            holding="Tenant may use repair-and-deduct or rent withholding for substantial "
            "habitability defects after reasonable notice.",
        ),
        PrecedentSummary(
            case_id=_case_id(11),
            jurisdiction="CA",
            issue="retaliatory eviction",
            facts="After tenant organized a tenants' association, landlord served a 30-day "
            "notice to terminate a month-to-month tenancy.",
            holding="Termination within 180 days of tenant's lawful organizing activity raises "
            "a rebuttable presumption of retaliation under Section 1942.5.",
        ),
        PrecedentSummary(
            case_id=_case_id(12),
            jurisdiction="CA",
            issue="landlord entry",
            facts="Landlord entered to make repairs with 48 hours' written notice during "
            "business hours.",
            holding="Entry complied with Section 1954: reasonable written notice, normal "
            "business hours, and a permitted purpose.",
        ),
        PrecedentSummary(
            case_id=_case_id(13),
            jurisdiction="CA",
            issue="rent increase",
            facts="Tenant received a 10-day notice of a rent increase in a city without rent "
            "control.",
            holding="State law does not cap rent increases where no local rent control "
            "applies, but reasonable notice is required; 10 days is likely insufficient "
            "for a month-to-month tenancy.",
        ),
        PrecedentSummary(
            case_id=_case_id(14),
            jurisdiction="CA",
            issue="eviction notice",
            facts="Landlord gave a 30-day notice to vacate after tenant resided for 14 months.",
            holding="For a tenant of one year or more, Section 1946.1 requires 60 days' "
            "written notice. Notice is invalid.",
        ),
        PrecedentSummary(
            case_id=_case_id(15),
            jurisdiction="CA",
            issue="early termination",
            facts="Tenant terminated a month-to-month tenancy with 15 days' notice after "
            "residing for six months.",
            holding="Tenant must give at least 30 days' written notice under Section 1946.1. "
            "Tenant may owe rent for the notice period.",
        ),
        PrecedentSummary(
            case_id=_case_id(16),
            jurisdiction="CA",
            issue="tenant duty to maintain",
            facts="Tenant repeatedly flushed inappropriate items, causing plumbing backups.",
            holding="Tenant's conduct constituted negligent destruction; landlord may recover "
            "repair costs.",
        ),
    ]


def _additional_precedents() -> list[PrecedentSummary]:
    def case(n: int, j: str, issue: str, facts: str, holding: str) -> PrecedentSummary:
        return PrecedentSummary(
            case_id=_case_id(n), jurisdiction=j, issue=issue, facts=facts, holding=holding
        )

    return [
        case(
            17,
            "TX",
            "security deposit refund",
            "Tenant moved out and gave a forwarding address in writing. Landlord sent no "
            "itemized list of deductions and kept the deposit for 60 days.",
            "Landlord must refund the deposit or send an itemized list within 30 days of "
            "surrender under Sections 92.103 and 92.104. A landlord who misses the deadline "
            "without a good-faith basis forfeits the right to keep any of the deposit.",
        ),
        case(
            18,
            "TX",
            "habitability repair",
            "Tenant's air conditioning failed in July. After written notice and current rent "
            "payments, the landlord made no repair for six weeks.",
            "Failure to repair a condition that materially affects health or safety after "
            "notice entitles the tenant to the remedies in Section 92.0581, including "
            "terminating the lease or judicial relief.",
        ),
        case(
            19,
            "CA",
            "retaliatory eviction",
            "Tenant requested repairs of a broken furnace. Two weeks later the landlord "
            "raised the rent and served a notice of termination.",
            "Rent increases or termination shortly after a tenant lawfully asserts habitability "
            "rights are retaliatory under Section 1942.5 unless the landlord shows a "
            "legitimate independent reason.",
        ),
        case(
            20,
            "TX",
            "early termination",
            "Month-to-month tenant left with two weeks' oral notice.",
            "A monthly tenancy ends only on at least one month's written notice under Section "
            "91.001. Tenant remains liable for rent through the notice period.",
        ),
        case(
            21,
            "TX",
            "security deposit refund",
            "Landlord deducted $400 for repainting after a two-year tenancy and gave no receipts.",
            "Repainting after ordinary use is normal wear and tear and cannot be charged "
            "against the deposit under Section 92.102.",
        ),
        case(
            22,
            "TX",
            "landlord entry",
            "Landlord entered while the tenant was away to respond to a reported gas smell.",
            "Entry without prior notice is allowed in an emergency under Section 92.0081.",
        ),
        case(
            23,
            "TX",
            "eviction notice",
            "Landlord gave a written notice to vacate but filed eviction two days later.",
            "Section 24.005 requires the notice period set by the lease, or the statutory "
            "default if the lease is silent, to run before an eviction suit is filed.",
        ),
        case(
            24,
            "TX",
            "habitability repair",
            "Tenant paid for a plumber to fix a burst pipe without first giving the landlord "
            "written notice.",
            "The repair-and-deduct remedy requires prior written notice and time for the "
            "landlord to repair; deduction was disallowed.",
        ),
        case(
            25,
            "CA",
            "security deposit refund",
            "Landlord returned the deposit 15 days after move-out with an itemized statement "
            "showing $250 for damage beyond normal wear.",
            "Return within 21 days with an itemized statement satisfies Section 1950.5; "
            "deductions for actual damage beyond ordinary wear are permitted.",
        ),
        case(
            26,
            "CA",
            "habitability repair",
            "Tenant had no hot water for two weeks. Landlord was notified in writing and did "
            "not act.",
            "Lack of hot running water is a habitability defect under Section 1941. The tenant "
            "may repair and deduct up to one month's rent under Section 1942.",
        ),
        case(
            27,
            "CA",
            "landlord entry",
            "Landlord entered without notice to show the unit to a friend interested in "
            "renting it later.",
            "Entry to show the unit to prospective tenants still requires reasonable written "
            "notice under Section 1954; the entry was improper.",
        ),
        case(
            28,
            "CA",
            "retaliatory eviction",
            "Landlord ended a tenancy because the tenant's child enrolled in a particular "
            "public school.",
            "Section 1940.4 bars terminating or penalizing a tenancy based on a child's school "
            "enrollment.",
        ),
        case(
            29,
            "CA",
            "tenant duty to maintain",
            "Tenant left the unit filthy and disabled a smoke detector's battery.",
            "Section 1941.2 requires tenants to keep premises clean and sanitary and not to "
            "destroy or damage them; landlord may recover the cost of cleaning and repair.",
        ),
        case(
            30,
            "CA",
            "eviction notice",
            "Tenant of six months received a 30-day notice from the landlord to end a "
            "month-to-month tenancy.",
            "For a tenancy under one year, 30 days' written notice suffices under Section 1946.1.",
        ),
    ]


def all_precedents() -> list[PrecedentSummary]:
    return _tx_precedents() + _ca_precedents() + _additional_precedents()


def write_precedents_json(path: Path) -> None:
    """Write the synthetic precedent corpus as newline-delimited JSON records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [p.model_dump() for p in all_precedents()]
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


if __name__ == "__main__":
    write_precedents_json(Path(__file__).with_name("sample") / "precedents.json")
    print(f"Wrote {len(all_precedents())} synthetic precedents to data/sample/precedents.json")
