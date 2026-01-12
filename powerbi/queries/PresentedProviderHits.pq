let
  // Parameter: RootFolder (Text)
  Source = Csv.Document(File.Contents(RootFolder & "/Presented Provider Hits.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  TrimmedHeaders = Table.TransformColumnNames(Promoted, each Text.Trim(_)),
  // Drop fully blank rows
  NonBlank = Table.SelectRows(TrimmedHeaders, each List.AnyTrue(List.Transform(Record.ToList(_), (v) => v <> null and Text.Trim(Text.From(v)) <> ""))),
  ToTextNPI = if Table.HasColumns(NonBlank, "Billing NPI") then Table.TransformColumnTypes(NonBlank, {{"Billing NPI", type text}}) else NonBlank,
  Renamed = Table.TransformColumnNames(ToTextNPI, each if _ = "Total Qualifying Paid Amount" then "Total Overpayment" else if _ = "Number of Claim Hits" then "NumberOfClaimHits" else _),
  CleanCurrency = (tbl as table, cols as list) as table =>
    List.Accumulate(cols, tbl, (state, col) => if Table.HasColumns(state, col) then Table.TransformColumns(state, {{col, each try Number.FromText(Text.Replace(Text.Replace(Text.Trim(Text.From(_)), "$", ""), ",", "")) otherwise null, type number}}) else state),
  CurrencyCols = {"Total Overpayment", "Total Paid Amount"},
  Cleaned = CleanCurrency(Renamed, CurrencyCols)
in
  Cleaned