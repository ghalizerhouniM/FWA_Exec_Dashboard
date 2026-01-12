# DAX Measures

-- KPIs
Total Overpayment (Presented) = SUM('Presented Hits'[Total Overpayment])

Total Overpayment (All) = SUM('All Hits'[Total Overpayment])

Providers Flagged (Presented) = SUM('Presented Hits'[Number of Provider Hits])

Providers Flagged (All) = SUM('All Hits'[Number of Provider Hits])

Claims Flagged (Presented) = SUM('Presented Hits'[Number of Claim Hits])

Claims Flagged (All) = SUM('All Hits'[Number of Claim Hits])

Concepts Delivered = DISTINCTCOUNT('Presented Hits'[Concept])

-- Date helpers (optional: use a separate Date table and mark as date table)
Min Delivery Date = MIN('Presented Hits'[Date of Client Delivery])

Max Delivery Date = MAX('All Hits'[Date of Client Delivery])

-- Cumulative overpayment (Presented)
Cumulative Overpayment (Presented) =
VAR MaxDate = MAX('Presented Hits'[Date of Client Delivery])
RETURN
  CALCULATE(
    [Total Overpayment (Presented)],
    FILTER(ALL('Presented Hits'[Date of Client Delivery]), 'Presented Hits'[Date of Client Delivery] <= MaxDate)
  )

-- Cumulative overpayment (All)
Cumulative Overpayment (All) =
VAR MaxDate = MAX('All Hits'[Date of Client Delivery])
RETURN
  CALCULATE(
    [Total Overpayment (All)],
    FILTER(ALL('All Hits'[Date of Client Delivery]), 'All Hits'[Date of Client Delivery] <= MaxDate)
  )

-- Delivered dates table (for cadence calculations)
Delivered Dates =
ADDCOLUMNS(
  SUMMARIZE('Presented Hits', 'Presented Hits'[Concept], "DeliveryDate", MIN('Presented Hits'[Date of Client Delivery])),
  "Baseline", DATE(2025,11,5),
  "Delta Days", DATEDIFF([Baseline], [DeliveryDate], DAY)
)

-- Average successive cadence (days) using Delivered Dates
Average Successive Cadence (Days) =
VAR T =
  ADDCOLUMNS(
    CALCULATETABLE(VALUES(DeliveredDates[DeliveryDate]), ALL(DeliveredDates[DeliveryDate])),
    "Rank", RANKX(ALL(DeliveredDates[DeliveryDate]), DeliveredDates[DeliveryDate], , ASC)
  )
VAR WithPrev = ADDCOLUMNS(T, "PrevDate", CALCULATE(MAX(DeliveredDates[DeliveryDate]), FILTER(ALL(DeliveredDates[DeliveryDate]), RANKX(ALL(DeliveredDates[DeliveryDate]), DeliveredDates[DeliveryDate], , ASC) = [Rank] - 1)))
VAR Intervals = ADDCOLUMNS(WithPrev, "IntervalDays", DATEDIFF([PrevDate], [DeliveryDate], DAY))
RETURN AVERAGEX(FILTER(Intervals, NOT(ISBLANK([IntervalDays]))), [IntervalDays])

-- Whitepaper link column (as a calculated column on a concept table)
Whitepaper URL =
VAR Name = 'Presented Hits'[Concept]
VAR Base = SELECTEDVALUE(Parameters[WhitepapersBase], "/Whitepapers/")
RETURN Base & Name & ".pdf"

-- Provider-level counts (if needed)
Providers Count = DISTINCTCOUNT('Presented Provider Hits'[Billing NPI])
