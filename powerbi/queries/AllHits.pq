let
  // Parameter: RootFolder (Text) e.g., "/Users/you/Documents/FWA/Executive Dashboard"
  Source = Csv.Document(File.Contents(RootFolder & "/All Hits - Summary Statistics.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  TrimmedHeaders = Table.TransformColumnNames(Promoted, each Text.Trim(_)),
  // Drop fully blank rows
  NonBlank = Table.SelectRows(TrimmedHeaders, each List.AnyTrue(List.Transform(Record.ToList(_), (v) => v <> null and Text.Trim(Text.From(v)) <> ""))),
  // Ensure known types and clean currency-like columns
  ToTextNPI = if Table.HasColumns(NonBlank, "Billing NPI") then Table.TransformColumnTypes(NonBlank, {{"Billing NPI", type text}}) else NonBlank,
  CleanCurrency = (tbl as table, cols as list) as table =>
    List.Accumulate(cols, tbl, (state, col) => if Table.HasColumns(state, col) then Table.TransformColumns(state, {{col, each try Number.FromText(Text.Replace(Text.Replace(Text.Trim(Text.From(_)), "$", ""), ",", "")) otherwise null, type number}}) else state),
  CurrencyCols = {"Total Overpayment", "Total Paid Amount", "Average Overpayment Per Provider", "Average Overpayment Per Claim"},
  Cleaned = CleanCurrency(ToTextNPI, CurrencyCols),
  // Parse date
  WithDate = if Table.HasColumns(Cleaned, "Date of Client Delivery") then Table.TransformColumns(Cleaned, {{"Date of Client Delivery", each try Date.From(_) otherwise null, type date}}) else Cleaned
in
  WithDate