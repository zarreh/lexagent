# ruff: noqa: E501
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


def _case_id(index: int) -> str:
    return f"SYN-{index:04d}"


def _case(n: int, jurisdiction: str, issue: str, facts: str, holding: str) -> PrecedentSummary:
    return PrecedentSummary(
        case_id=_case_id(n), jurisdiction=jurisdiction, issue=issue, facts=facts, holding=holding
    )


def all_precedents() -> list[PrecedentSummary]:
    """Synthetic cases written against the sections in seed_statutes.py."""
    return [
        _case(
            1,
            "TX",
            "security deposit refund",
            "Tenant vacated after a one-year lease and provided a forwarding address. Landlord kept the entire $1,200 deposit for carpet cleaning and minor wall scuffs.",
            "Landlord must refund the deposit on or before the 30th day after surrender under Section 92.103(a) and may not retain any portion to cover normal wear and tear under Section 92.104(b). Tenant awarded the full deposit.",
        ),
        _case(
            2,
            "TX",
            "eviction notice",
            "Landlord posted a three-day oral notice to vacate for nonpayment and immediately filed eviction.",
            "Section 24.005(a) requires written notice to vacate before a forcible detainer suit is filed. Eviction dismissed for lack of written notice.",
        ),
        _case(
            3,
            "TX",
            "habitability repair",
            "Tenant, current on rent, gave written notice in January that the heater was broken and a second written notice after two weeks. Landlord made no repair for three more weeks.",
            "The condition materially affected health and safety and the landlord had more than a reasonable time (presumptively seven days) under Section 92.056. Tenant entitled to judicial remedies under Section 92.0563, including a repair order, a rent reduction, and a civil penalty of one month's rent plus $500.",
        ),
        _case(
            4,
            "TX",
            "tenant lockout",
            "Landlord changed the locks while the tenant was current on rent and refused to give the tenant a key.",
            "No bona fide repair, emergency, abandonment, or lawful lock change for delinquent rent applied, so the exclusion violated Section 92.0081(b). Tenant may recover possession or terminate the lease and recover a civil penalty of one month's rent plus $1,000.",
        ),
        _case(
            5,
            "TX",
            "retaliatory eviction",
            "Tenant complained to the city about code violations. Two months later landlord increased rent by 25%.",
            "A rent increase within six months of the tenant's good-faith complaint to a governmental entity is prohibited retaliation under Section 92.331(b) unless an exception in Section 92.332 applies. Tenant may recover a civil penalty of one month's rent plus $500 under Section 92.333.",
        ),
        _case(
            6,
            "TX",
            "late fee",
            "Lease said nothing about late fees. Landlord charged a $75 late fee the day after rent was due.",
            "A late fee is collectible only if notice of the fee is in the written lease, the fee is reasonable, and rent has remained unpaid two full days after the due date under Section 92.019(a). The fee was not collectible.",
        ),
        _case(
            7,
            "TX",
            "early termination",
            "Tenant abandoned a six-month lease after two months for a job relocation. Landlord re-let the unit to a new tenant after one month.",
            "The landlord has a duty to mitigate damages when a tenant abandons the premises under Section 91.006, and that duty cannot be waived in the lease. Tenant owes no rent for the period the replacement tenant paid.",
        ),
        _case(
            8,
            "TX",
            "tenant duty to maintain",
            "Tenant intentionally clogged a sink and refused to report it, causing water damage.",
            "Deterioration caused by the tenant's negligence, carelessness, accident, or abuse is not normal wear and tear under Section 92.001(4). Landlord may deduct the repair cost from the deposit under Section 92.104(a) and has no duty to repair conditions the tenant caused under Section 92.052(b).",
        ),
        _case(
            9,
            "CA",
            "security deposit refund",
            "Tenant moved out and received no itemized statement. Landlord returned $100 of a $2,000 deposit 45 days later.",
            "Section 1950.5(h)(1) requires an itemized statement and return of the remainder within 21 days. A landlord who in bad faith fails to comply is not entitled to claim any amount of the security under Section 1950.5(h)(7) and may face statutory damages of up to twice the deposit for bad faith retention under Section 1950.5(m).",
        ),
        _case(
            10,
            "CA",
            "habitability repair",
            "Roof leaked for two months; landlord ignored repeated written notices. Tenant repaired the roof for less than one month's rent and deducted the cost.",
            "A leaking roof lacks effective waterproofing and makes the dwelling untenantable under Section 1941.1(a)(1). After notice and a reasonable time, the tenant may repair and deduct up to one month's rent under Section 1942(a), no more than twice in any 12-month period.",
        ),
        _case(
            11,
            "CA",
            "retaliatory eviction",
            "After tenant organized a tenants' association, landlord served a 30-day notice to terminate a month-to-month tenancy.",
            "Terminating a tenancy to retaliate against a tenant for lawfully organizing a lessees' association is unlawful under Section 1942.5(d); the tenant bears the burden of producing evidence that the landlord's conduct was retaliatory.",
        ),
        _case(
            12,
            "CA",
            "landlord entry",
            "Landlord entered to make repairs with 48 hours' written notice during business hours.",
            "Entry complied with Section 1954: reasonable written notice (24 hours is presumed reasonable), normal business hours, and a permitted purpose.",
        ),
        _case(
            13,
            "CA",
            "landlord entry",
            "Landlord phoned the tenant the day before a buyer's tour of the unit. The tenant had never received written notice that the property was for sale.",
            "Oral notice of entry to show the unit to prospective purchasers is allowed only if the landlord notified the tenant in writing within 120 days that the property is for sale and that oral contact may be used under Section 1954(d)(2); otherwise reasonable written notice is required.",
        ),
        _case(
            14,
            "CA",
            "eviction notice",
            "Landlord gave a 30-day notice to vacate after tenant resided for 14 months.",
            "An owner must give at least 60 days' written notice to terminate a residential periodic tenancy under Section 1946.1(b), unless the tenant has resided in the dwelling less than one year under Section 1946.1(c). Notice is invalid.",
        ),
        _case(
            15,
            "CA",
            "early termination",
            "Tenant terminated a month-to-month tenancy with 15 days' notice after residing for six months.",
            "A month-to-month tenancy may be terminated by giving at least 30 days' written notice under Section 1946(a), and rent is due through the termination date. Tenant owes rent for the notice period.",
        ),
        _case(
            16,
            "CA",
            "tenant duty to maintain",
            "Tenant repeatedly flushed inappropriate items, causing plumbing backups.",
            "Tenants must properly use and operate plumbing fixtures under Section 1941.2(a)(3), and the landlord has no duty to repair a dilapidation the tenant's substantial violation causes.",
        ),
        _case(
            17,
            "TX",
            "security deposit refund",
            "Tenant moved out and gave a forwarding address in writing. Landlord sent no itemized list of deductions and kept the deposit for 60 days.",
            "Landlord must refund the deposit or give an itemized list of deductions on or before the 30th day after surrender under Sections 92.103(a) and 92.104(c). Missing the deadline is presumed bad faith under Section 92.109(d), and a landlord who in bad faith fails to provide the list forfeits the right to withhold any portion of the deposit under Section 92.109(b).",
        ),
        _case(
            18,
            "TX",
            "habitability repair",
            "Tenant's air conditioning failed in July. After written notice and a second written notice, with rent current, the landlord made no repair for six weeks.",
            "The tenant may terminate the lease or obtain judicial remedies under Sections 92.056(e) and 92.0563, including an order to repair and a civil penalty of one month's rent plus $500.",
        ),
        _case(
            19,
            "CA",
            "retaliatory eviction",
            "Tenant requested repairs of a broken furnace. Two weeks later the landlord raised the rent and served a notice of termination.",
            "Rent increases or termination within 180 days after a tenant gives notice about tenantability are prohibited retaliation under Section 1942.5(a) if the tenant is not in default on rent, unless the landlord has a lawful cause.",
        ),
        _case(
            20,
            "TX",
            "early termination",
            "Month-to-month tenant moved out after giving two weeks' notice.",
            "Under Section 91.001(b) a month-to-month tenancy terminates on the later of the date in the notice or one month after the notice is given. Tenant is liable for rent only up to the termination date under Section 91.001(d).",
        ),
        _case(
            21,
            "TX",
            "security deposit refund",
            "Landlord deducted $400 for repainting after a two-year tenancy and gave no receipts.",
            "Repainting after ordinary use is normal wear and tear under Section 92.001(4) and cannot be deducted from the deposit under Section 92.104(b).",
        ),
        _case(
            22,
            "TX",
            "tenant lockout",
            "Landlord kept the tenant out of the unit for two days while crews repaired a burst water main and flooded floors.",
            "Excluding a tenant during bona fide repairs or an emergency is permitted under Section 92.0081(b)(1); the lockout provision was not violated.",
        ),
        _case(
            23,
            "TX",
            "eviction notice",
            "Landlord gave a written notice to vacate but filed eviction two days later.",
            "Section 24.005(a) requires at least three days' written notice to vacate, unless the lease sets a different period, before a forcible detainer suit is filed. The suit was premature.",
        ),
        _case(
            24,
            "TX",
            "habitability repair",
            "Tenant paid a plumber to fix a burst pipe without first giving the landlord notice that the tenant intended to repair.",
            "Repair-and-deduct requires prior notice stating the tenant's intent to repair under Section 92.0561(d)(2); the deduction was disallowed.",
        ),
        _case(
            25,
            "CA",
            "security deposit refund",
            "Landlord returned the deposit 15 days after move-out with an itemized statement showing $250 for damage beyond normal wear.",
            "Return within 21 days with an itemized statement satisfies Section 1950.5(h)(1); deductions for damage beyond ordinary wear and tear are permitted under Section 1950.5(e).",
        ),
        _case(
            26,
            "CA",
            "habitability repair",
            "Tenant had no hot water for 35 days after written notice and the landlord did not act. Tenant paid a plumber $300, less than one month's rent, and deducted it.",
            "Lack of hot and cold running water makes the dwelling untenantable under Section 1941.1(a)(3). A tenant who repairs and deducts after the 30th day following notice is presumed to have acted after a reasonable time under Section 1942(b).",
        ),
        _case(
            27,
            "CA",
            "landlord entry",
            "Landlord entered without notice to show the unit to a friend interested in renting it later.",
            "Entry to exhibit the unit to prospective tenants still requires reasonable written notice under Section 1954(d)(1); the entry was improper.",
        ),
        _case(
            28,
            "CA",
            "retaliatory eviction",
            "After the tenant reported a mold problem to the city, the landlord threatened to report the tenant's family to immigration authorities.",
            "Reporting or threatening to report a lessee or associated individuals to immigration authorities is retaliatory conduct prohibited under Section 1942.5(c).",
        ),
        _case(
            29,
            "CA",
            "tenant duty to maintain",
            "Tenant left the unit filthy and damaged a smoke detector.",
            "Section 1941.2(a) obliges tenants to keep the premises clean and sanitary and not to damage the dwelling unit or its equipment; the landlord may recover the cost of cleaning and repair.",
        ),
        _case(
            30,
            "CA",
            "eviction notice",
            "Tenant of six months received a 30-day notice from the landlord to end a month-to-month tenancy.",
            "For a tenancy of less than one year, 30 days' written notice suffices under Section 1946.1(c).",
        ),
    ]


def write_precedents_json(path: Path) -> None:
    """Write the synthetic precedent corpus as newline-delimited JSON records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [p.model_dump() for p in all_precedents()]
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


if __name__ == "__main__":
    write_precedents_json(Path(__file__).with_name("sample") / "precedents.json")
    print(f"Wrote {len(all_precedents())} synthetic precedents to data/sample/precedents.json")
