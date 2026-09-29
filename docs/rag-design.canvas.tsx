import { useState } from "cursor/canvas";
import {
  Callout,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

type Source = "RAG" | "SQL" | "SQL+RAG" | "No answer";

const QUESTIONS: Array<{
  id: string;
  source: Source;
  ask: string;
  evidence: string;
}> = [
  {
    id: "Q1",
    source: "RAG",
    ask: "NorthstarPay 喺 2026-03-15 嘅收單費率、固定費、最低費係幾多？",
    evidence: "NSP-FEE-2025-01。2.90% + 0.30 USD，最低 0.50 USD。",
  },
  {
    id: "Q2",
    source: "RAG",
    ask: "同一條費率問題，日期改做 2026-04-02。",
    evidence: "必須命中 NSP-FEE-2026-04。2.60% + 0.30 USD，FX markup 200 bps。唔好再引用 2025-01。",
  },
  {
    id: "Q3",
    source: "RAG",
    ask: "NorthstarPay 跨幣種 FX markup 點計？可唔可以再加一次落 total fee？",
    evidence: "NSP-FX-2025-01 / NSP-FX-2026-04。Markup 已經喺 applied rate 入面。",
  },
  {
    id: "Q4",
    source: "SQL",
    ask: "NSP-FX-0001 嘅 total fee 同 expected net 係幾多？",
    evidence: "交易行。total_fee 3.3850 USD，expected_net 102.9950 USD。",
  },
  {
    id: "Q5",
    source: "SQL+RAG",
    ask: "點解 NSP-VER-0002 到手少過 NSP-FX-0001？百分比費明明平咗。",
    evidence: "兩行交易 + 兩個版本文件。Mid 同係 1.08。Markup 150 → 200 bps。",
  },
  {
    id: "Q6",
    source: "SQL+RAG",
    ask: "點解 CDG-FEEHIKE-0002 比 CDG-FEEHIKE-0001 貴？",
    evidence: "固定費 2.00 → 3.50 USD。引用 CDG-FEE-2026-06。",
  },
  {
    id: "Q7",
    source: "SQL",
    ask: "邊筆交易用咗最低收費？邊筆 settled 短咗？",
    evidence: "NSP-MINFEE-0001 min_fee_applied。NSP-SHORT-0001 variance -0.5000，short_pay。",
  },
  {
    id: "Q8",
    source: "SQL+RAG",
    ask: "HFL-REFUND-0001 會唔會退返原本 9 HKD 百分比費？",
    evidence: "refund_returns_percent_fee = false。退款另收 1.00 HKD。expected_net -501.0000。",
  },
  {
    id: "Q9",
    source: "SQL+RAG",
    ask: "失敗交易收唔收費？比較 NSP-FAIL-0001 同 CDG-FAIL-0001。",
    evidence: "Northstar 失敗費 0。CedarGate payout 失敗收 attempt fee 0.25 USD。",
  },
  {
    id: "Q10",
    source: "No answer",
    ask: "可唔可以用比特幣結算？",
    evidence: "文件冇寫。答案必須係無法確認。唔好用模型記憶補費率。",
  },
];

const FILTERS: Array<"All" | Source> = ["All", "RAG", "SQL", "SQL+RAG", "No answer"];

export default function RagDesign() {
  const [filter, setFilter] = useState<"All" | Source>("All");
  const rows = QUESTIONS.filter((q) => filter === "All" || q.source === filter).map((q) => [
    q.id,
    q.source,
    q.ask,
    q.evidence,
  ]);

  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Fake-Bank RAG design</H1>
        <Text tone="secondary">
          Payment reconciliation explainer. Fictional gateways only. Numbers below match sql/seed/01_reference_seed.sql.
        </Text>
      </Stack>

      <Row gap={16}>
        <Stat value="3" label="Gateways" />
        <Stat value="10" label="Golden transactions" />
        <Stat value="~5,000" label="Generated later" />
        <Stat value="10" label="Core questions" />
      </Row>

      <Callout tone="warning" title="Two sources, one formula">
        fee_schedule_tb holds the rates the generator uses. Markdown under docs/source/ holds the sentences the retriever quotes. Both must use the same numbers. The model never invents a third rate.
      </Callout>

      <H2>Ask path</H2>
      <Grid columns={4} gap={12}>
        <Stack gap={4}>
          <H3>1. Question</H3>
          <Text size="small">User asks in the UI. FastAPI receives it. The API key stays on the server.</Text>
        </Stack>
        <Stack gap={4}>
          <H3>2. Route</H3>
          <Text size="small">Fee wording goes to document search. Amounts go to SQL tools. Mixed questions do both.</Text>
        </Stack>
        <Stack gap={4}>
          <H3>3. Evidence</H3>
          <Text size="small">Chunks carry doc code, version, and dates. SQL returns txn_ref and fee columns.</Text>
        </Stack>
        <Stack gap={4}>
          <H3>4. Answer</H3>
          <Text size="small">The model may only explain the evidence. Missing evidence returns 無法確認.</Text>
        </Stack>
      </Grid>

      <Divider />

      <H2>Core questions</H2>
      <Row gap={8} wrap>
        {FILTERS.map((item) => (
          <Pill key={item} active={filter === item} onClick={() => setFilter(item)}>
            {item}
          </Pill>
        ))}
      </Row>
      <Table
        headers={["ID", "Source", "Question", "What must support the answer"]}
        rows={rows}
        striped
        stickyHeader
      />
      <Text size="small" tone="secondary">
        Date rule: store occurred_at as timestamptz UTC. Interpret 昨日 and 上星期 in Asia/Hong_Kong, then query a concrete range. Fee version uses that Hong Kong civil date.
      </Text>

      <H2>Fee identity</H2>
      <Table
        headers={["Term", "Meaning", "Rule locked in transaction_tb"]}
        rows={[
          ["Fixed fee", "Flat amount in settlement currency", "Added before the minimum"],
          ["Percent fee", "Rate times absolute settlement gross", "Round half-up to 4 d.p."],
          ["FX markup", "Worse rate than mid", "Inside applied_fx_rate. Not added again"],
          ["Min fee", "Floor on percent + fixed", "min_fee_applied when percent + fixed is lower"],
          ["Attempt fee", "Charge on a failed txn", "Only failed_attempt_fee. Other fees are 0"],
          ["Expected net", "What the merchant should receive", "settlement_gross - total_fee"],
          ["Settled amount", "What the gateway actually paid", "Signed the same way as expected net"],
          ["Variance", "Reconciliation gap", "settled_amount - expected_net"],
        ]}
        columnAlign={["left", "left", "left"]}
      />

      <H2>Build order</H2>
      <Table
        headers={["Step", "You do this", "Done when"]}
        rows={[
          ["A", "Apply the SQL files to local Postgres", "10 golden txn_ref values exist"],
          ["B", "Hand-calc NSP-FX-0001 and NSP-MINFEE-0001", "Your paper result matches the row"],
          ["C", "Write the 10 Markdown files listed in document_tb", "Each file's numbers match fee_schedule_tb"],
          ["D", "Write scripts/generate_data.py with seed 42", "About 5,000 rows, golden refs untouched"],
          ["E", "Chunk by heading into document_chunk_tb", "A fee rule and its exception stay in one chunk"],
          ["F", "Search chunks with no LLM", "Q1 and Q2 return different versions"],
          ["G", "JWT login, admin and user", "User queries only see owner_user_id = self"],
          ["H", "Then call the LLM, with citations", "Q10 stays 無法確認"],
        ]}
      />

      <Text size="small" tone="secondary">
        Local demo passwords live in the seed file header. They are bcrypt hashes for this database only.
      </Text>
    </Stack>
  );
}
