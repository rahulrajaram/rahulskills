export default defineIntent({
  id: "larger-move-qualification",
  objective: "Qualify one bounded local baseline for continuation state, composition locks, learning ingestion, and the independently frozen continuation trace",
  artifacts: {
    qualification: artifact({
      mediaType: "application/json",
      contract: described("A deterministic epoch-one qualification report preserving controller and consumer evidence classes"),
      maxBytes: 262144,
    }),
  },
  workflow: sequence(
    achieve({
      id: "run-qualification-suite",
      objective: "Run the maintained read-only epoch-one qualification suite",
      produces: ["qualification"],
    }),
    establish({
      id: "assess-qualification-report",
      claim: "The epoch-one report records continuation, composition, learning and trace checks with explicit authority and multi-epoch limits",
      consumes: ["qualification"],
    }),
  ),
  acceptance: established("assess-qualification-report"),
});
