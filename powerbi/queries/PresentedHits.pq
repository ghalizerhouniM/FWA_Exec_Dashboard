let
  // Parameter: RootFolder (Text)
  Source = Csv.Document(File.Contents(RootFolder & "/Presented Hits - Summary Statistics.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  TrimmedHeaders = Table.TransformColumnNames(Promoted, each Text.Trim(_)),
  // Remove columns that are entirely null (handles trailing blank column)
  NonNullCols = Table.SelectColumns(TrimmedHeaders, List.Select(Table.ColumnNames(TrimmedHeaders), (c) => List.AnyTrue(List.Transform(Table.Column(TrimmedHeaders, c), each _ <> null and Text.Trim(Text.From(_)) <> "")))),
  // Drop fully blank rows
  NonBlank = Table.SelectRows(NonNullCols, each List.AnyTrue(List.Transform(Record.ToList(_), (v) => v <> null and Text.Trim(Text.From(v)) <> ""))),
  CleanCurrency = (tbl as table, cols as list) as table =>
    List.Accumulate(cols, tbl, (state, col) => if Table.HasColumns(state, col) then Table.TransformColumns(state, {{col, each try Number.FromText(Text.Replace(Text.Replace(Text.Trim(Text.From(_)), "$", ""), ",", "")) otherwise null, type number}}) else state),
  CurrencyCols = {"Total Overpayment", "Total Paid Amount", "Average Overpayment Per Provider", "Average Overpayment Per Claim"},
  Cleaned = CleanCurrency(NonBlank, CurrencyCols),
  WithDate = if Table.HasColumns(Cleaned, "Date of Client Delivery") then Table.TransformColumns(Cleaned, {{"Date of Client Delivery", each try Date.From(_) otherwise null, type date}}) else Cleaned
in
  WithDate