

---

# **🌐 End-to-End Workflow for PCR/PoA Relief & Investigation (Human Process – Verified Version)**

## **1. Filing the Case at Vishesh Thana**

The process begins when a victim of caste-based discrimination or atrocity approaches a *Vishesh Thana*, which is a special police station responsible for SC/ST-related crimes.

At this stage, the **Investigation Officer (IO)**:

* Registers the FIR
* Uploads the FIR document into the system
* Enters FIR number and incident details
* Collects and uploads Aadhaar, caste certificate, medical reports, postmortem reports, and any incident-proof documents
* Collects the victim’s bank details

Once the IO submits the FIR, your backend can fetch and verify linked Aadhaar and FIR metadata automatically.

From here onwards, **two tracks begin simultaneously**:
**(A)** the *administrative relief process*
**(B)** the *police investigation process*

---

# **🔵 TRACK A — Relief Approval & DBT Flow**

## **2. Verification & Amount Proposal by Tribal Officer**

The relief request is forwarded to the **Tribal Officer**, who is responsible for validating eligibility under the PCR/PoA Acts.

This officer:

* Verifies FIR, Aadhaar, and medical proof
* Confirms caste eligibility
* Checks whether incident meets PoA/PCR relief categories
* Decides the **initial relief amount** as per government guidelines
* Forwards the case to the District Magistrate (DM)

This is the first major verification checkpoint.

---

## **3. District Magistrate (DM) Review + Victim Statement**

The **DM** is the main sanctioning authority.

The DM:

* Reviews each document
* Cross-checks the Tribal Officer’s recommended allowance
* Requires the victim to physically appear to provide a statement if fund type is Fixed Deposit
  (Your system can notify the victim and schedule appointments)

If corrections are needed:

* DM sends the case **back to the Tribal Officer**
* Tribal Officer updates details and resends

After satisfaction:

* DM approves and forwards the request to the **State Nodal Officer (SNO)**

---

## **4. State Nodal Officer — Fund Approval**

The SNO validates that all DM-level approvals are proper.

The SNO:

* Approves the release of funds
* Allocates the necessary financial amount from the state’s PCR/PoA budget
* Sends the funds to the **district Tribal Officer’s treasury account**

This is where “money enters the pipeline.”

---

## **5. Tribal Officer (District) — PFMS & Bank Processing**

Once funds arrive at the district level:

* Tribal Officer creates and submits a **PFMS request letter**
* Issues a **permission/authorization letter to the bank after PFMS approves the request**
* Bank releases the **first tranche (25%)** of the total approved allowance directly to the victim’s account

This completes the **first stage of DBT**.

---

# **🔵 TRACK B — Police Investigation & Chargesheet Flow (Parallel)**

## **6. Investigation → DSP → Chargesheet Submission**

Parallel to relief processing, the police continue the criminal investigation.

The **DSP (Deputy Superintendent of Police)** eventually:

* Completes investigation
* Prepares the **chargesheet**
* Submits it to the court
* Updates the portal with:

  * Chargesheet number
  * Date
  * Offense sections
  * Case status

The chargesheet controls eligibility for the *next tranche* of financial relief.

---

# **🔵 SECOND TRANCHE (additional 25–50%) — After Chargesheet**

## **7. Release of Additional Relief Based on Case Severity**

After chargesheet submission:

* The system or Tribal officer verifies chargesheet status
* The case severity category is confirmed (minor, moderate, severe)
* Victim becomes eligible for a **second tranche**, ranging from **25% to 50%**, depending on offense gravity

Again:

* Tribal Officer handles PFMS documentation
* Bank releases the second tranche to the victim

---

# **🔵 FINAL TRANCHE — After Case Completion**

## **8. Court Verdict → Final Settlement**

When the court delivers the judgment:

* Court staff upload judgment into eCourts
* DSP(Investigation Officer) or a designated court officer updates your portal with case completion details

After this:

* Victim becomes eligible for the **final remaining portion** of the relief amount
* Tribal Officer processes the final PFMS request
* Bank transfers the last tranche

This marks the **completion of the relief request lifecycle**.

---

# **🎯 Final Outcome**

The entire case—from FIR filing to last fund transfer—has these major checkpoints:

1. FIR filed
2. Tribal Officer verification
3. DM approval
4. SNO fund release
5. First 25% disbursal
6. Chargesheet submitted
7. Second tranche (25–50%) disbursal
8. Case completion
9. Final tranche disbursal

Your digital system will unify these fragmented steps into one trackable process.

---